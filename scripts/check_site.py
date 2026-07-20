#!/usr/bin/env python3
"""GitHub Pages向け静的サイトのリンクと基本メタデータを検証する。"""

from __future__ import annotations

import re
import struct
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parent.parent
HTML_FILES = sorted(ROOT.glob("*.html")) + sorted((ROOT / "releases").glob("*.html"))
SKIP_SCHEMES = {"http", "https", "mailto", "tel", "data"}
CONTRAST_PAIRS = {
    "本文（Light）": ("#182235", "#f5f7fa"),
    "補助文（Light）": ("#5d6879", "#f5f7fa"),
    "主要ボタン": ("#ffffff", "#46689b"),
    "本文（Dark）": ("#f4f7fb", "#0f1622"),
    "補助文（Dark）": ("#b6c1cf", "#0f1622"),
}
PNG_ASSETS = {
    "assets/icons/app-icon-source.png": (1024, 1024),
    "assets/icons/apple-touch-icon.png": (180, 180),
    "assets/icons/favicon-32.png": (32, 32),
    "assets/icons/icon-192.png": (192, 192),
    "assets/social/x-profile-icon-800x800.png": (800, 800),
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.local_references: list[tuple[str, str]] = []
        self.errors: list[str] = []
        self.title_depth = 0
        self.title_text: list[str] = []
        self.has_description = False
        self.has_canonical = False
        self.x_links = 0

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        values = dict(attrs)

        if element_id := values.get("id"):
            self.ids.append(element_id)

        if tag == "title":
            self.title_depth += 1

        if tag == "meta" and values.get("name") == "description":
            self.has_description = bool(values.get("content"))

        if tag == "link" and values.get("rel") == "canonical":
            self.has_canonical = bool(values.get("href"))

        if tag == "img":
            if "alt" not in values:
                self.errors.append(f"altのない画像: {values.get('src', '(srcなし)')}")
            classes = set((values.get("class") or "").split())
            if "support-screenshot" in classes and "height" in values:
                self.errors.append(
                    "support-screenshotへ固定height属性を指定している"
                )

        if "style" in values:
            self.errors.append(f"インラインstyleを使用: <{tag}>")

        if tag == "a":
            href = values.get("href", "")
            if href == "https://x.com/MyKyudoNote":
                self.x_links += 1
            if values.get("target") == "_blank":
                rel = set((values.get("rel") or "").split())
                if not {"noopener", "noreferrer"}.issubset(rel):
                    self.errors.append(
                        f'target="_blank"にnoopener noreferrerがない: {href}'
                    )

        for attr in ("href", "src"):
            if reference := values.get(attr):
                self.local_references.append((attr, reference))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title" and self.title_depth:
            self.title_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.title_depth:
            self.title_text.append(data)


def validate_page(path: Path) -> list[str]:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    errors = list(parser.errors)

    if not "".join(parser.title_text).strip():
        errors.append("titleがない")
    if not parser.has_description:
        errors.append("meta descriptionがない")
    if not parser.has_canonical:
        errors.append("canonicalがない")

    duplicate_ids = {item for item in parser.ids if parser.ids.count(item) > 1}
    if duplicate_ids:
        errors.append(f"重複ID: {', '.join(sorted(duplicate_ids))}")

    for attr, raw_reference in parser.local_references:
        parsed = urlparse(raw_reference)
        if parsed.scheme in SKIP_SCHEMES or raw_reference.startswith("#"):
            continue

        reference_path = unquote(parsed.path)
        if not reference_path:
            continue

        candidate = (path.parent / reference_path).resolve()
        if reference_path.endswith("/"):
            candidate = candidate / "index.html"
        if not candidate.exists():
            errors.append(f"{attr}のリンク先がない: {raw_reference}")

    if path.name in {"index.html", "support.html"} and parser.x_links == 0:
        errors.append("公式Xリンクがない")

    return [f"{path.relative_to(ROOT)}: {error}" for error in errors]


def contrast_ratio(foreground: str, background: str) -> float:
    def luminance(color: str) -> float:
        channels = [
            int(color[index : index + 2], 16) / 255
            for index in (1, 3, 5)
        ]
        linear = [
            channel / 12.92
            if channel <= 0.04045
            else ((channel + 0.055) / 1.055) ** 2.4
            for channel in channels
        ]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

    first = luminance(foreground)
    second = luminance(background)
    lighter, darker = max(first, second), min(first, second)
    return (lighter + 0.05) / (darker + 0.05)


def validate_png(path: Path, expected_size: tuple[int, int]) -> list[str]:
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or len(data) < 26:
        return [f"{path.relative_to(ROOT)}: PNG形式ではない"]
    width, height = struct.unpack(">II", data[16:24])
    errors = []
    if (width, height) != expected_size:
        errors.append(
            f"{path.relative_to(ROOT)}: "
            f"{width}x{height}（期待値 {expected_size[0]}x{expected_size[1]}）"
        )
    if data[25] in {4, 6}:
        errors.append(f"{path.relative_to(ROOT)}: アルファチャンネルが残っている")
    return errors


def main() -> int:
    errors: list[str] = []
    for page in HTML_FILES:
        errors.extend(validate_page(page))

    stylesheet = (ROOT / "assets/css/site.css").read_text(encoding="utf-8")
    if re.search(r"object-fit\s*:\s*fill\b", stylesheet):
        errors.append("CSSでobject-fit: fillを使用している")
    support_rule = re.search(
        r"\.support-screenshot\s*\{(?P<body>[^}]*)\}",
        stylesheet,
        flags=re.DOTALL,
    )
    if support_rule is None:
        errors.append("support-screenshotのCSS定義がない")
    else:
        declarations = support_rule.group("body")
        if not re.search(r"height\s*:\s*auto\s*;", declarations):
            errors.append("support-screenshotにheight: autoがない")
        if not re.search(r"object-fit\s*:\s*contain\s*;", declarations):
            errors.append("support-screenshotにobject-fit: containがない")

    required_assets = [
        ROOT / "assets/images/x-header-1500x500.png",
        ROOT / "assets/images/ogp-1200x630.png",
        ROOT / "assets/icons/x-logo.svg",
    ]
    for asset in required_assets:
        if not asset.exists():
            errors.append(f"必須アセットがない: {asset.relative_to(ROOT)}")

    for relative_path, expected_size in PNG_ASSETS.items():
        asset = ROOT / relative_path
        if not asset.exists():
            errors.append(f"必須アセットがない: {relative_path}")
        else:
            errors.extend(validate_png(asset, expected_size))

    contrast_results = {
        name: contrast_ratio(foreground, background)
        for name, (foreground, background) in CONTRAST_PAIRS.items()
    }
    for name, ratio in contrast_results.items():
        if ratio < 4.5:
            errors.append(f"コントラスト不足: {name} {ratio:.2f}:1")

    if errors:
        print("Site validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    ratios = ", ".join(
        f"{name} {ratio:.2f}:1"
        for name, ratio in contrast_results.items()
    )
    print(f"Site validation passed: {len(HTML_FILES)} pages")
    print(f"Contrast checks passed: {ratios}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
