#!/usr/bin/env python3
"""GitHub Pages向け静的サイトのリンクと基本メタデータを検証する。"""

from __future__ import annotations

import json
import re
import struct
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
from xml.etree import ElementTree as ET

from generate_sitemap import (
    SITEMAP_ENTRIES,
    SITEMAP_NAMESPACE,
    render_sitemap,
)


ROOT = Path(__file__).resolve().parent.parent
HTML_FILES = (
    sorted(ROOT.glob("*.html"))
    + sorted((ROOT / "privacy").glob("*.html"))
    + sorted((ROOT / "releases").glob("*.html"))
)
SITE_ORIGIN = "https://kyudojapan.net"
APP_STORE_URL = (
    "https://apps.apple.com/jp/app/"
    "%E8%87%AA%E5%88%86%E3%81%A0%E3%81%91%E3%81%AE"
    "%E5%BC%93%E9%81%93%E3%83%8E%E3%83%BC%E3%83%88/"
    "id6790650199"
)
APP_STORE_BADGE_URL = (
    "https://tools.applemediaservices.com/api/badges/"
    "download-on-the-app-store/black/ja-jp?size=250x83"
)
CURRENT_IOS_VERSION = "7.3.2"
LEGACY_ORIGIN = "okkun1202lindalinda-ship-it.github.io"
SUPPORT_EMAIL = "mykyudonote@kyudojapan.net"
LEGACY_SUPPORT_EMAIL = "okkun1202.linda.linda@gmail.com"
ANALYTICS_SCRIPT = ROOT / "assets/js/analytics.js"
GA_MEASUREMENT_ID_PATTERN = re.compile(
    r'const\s+measurementId\s*=\s*"(?P<id>G-[A-Z0-9]+)"\s*;'
)
SKIP_SCHEMES = {"http", "https", "mailto", "tel", "data"}
CONTRAST_PAIRS = {
    "本文（Light）": ("#182235", "#f5f7fa"),
    "補助文（Light）": ("#5d6879", "#f5f7fa"),
    "主要ボタン": ("#ffffff", "#46689b"),
    "App Storeボタン（Dark）": ("#ffffff", "#315b8f"),
    "Roadmapラベル（Light）": ("#315b8f", "#dfe9f8"),
    "本文（Dark）": ("#f4f7fb", "#0f1622"),
    "補助文（Dark）": ("#b6c1cf", "#0f1622"),
    "Roadmapラベル（Dark）": ("#b4cef2", "#243b5c"),
}
PNG_ASSETS = {
    "assets/icons/app-icon-source.png": (1024, 1024),
    "assets/icons/apple-touch-icon.png": (180, 180),
    "assets/icons/favicon-32.png": (32, 32),
    "assets/icons/icon-96.png": (96, 96),
    "assets/icons/icon-192.png": (192, 192),
    "assets/icons/icon-512.png": (512, 512),
    "assets/social/x-profile-icon-800x800.png": (800, 800),
}
ALPHA_PNG_ASSETS = {
    "assets/icons/x-logo-black-68.png": (68, 70),
    "assets/icons/x-logo-white-68.png": (68, 70),
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
        self.canonical = ""
        self.og_url = ""
        self.og_image = ""
        self.og_site_name = ""
        self.twitter_url = ""
        self.twitter_image = ""
        self.has_manifest = False
        self.has_favicon = False
        self.has_apple_touch_icon = False
        self.x_links = 0
        self.app_store_links = 0
        self.app_store_badges = 0
        self.head_depth = 0
        self.scripts: list[tuple[str, bool, bool]] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        values = dict(attrs)

        if tag == "head":
            self.head_depth += 1

        if element_id := values.get("id"):
            self.ids.append(element_id)

        if tag == "title":
            self.title_depth += 1

        if tag == "meta" and values.get("name") == "description":
            self.has_description = bool(values.get("content"))

        if tag == "link":
            rel = set((values.get("rel") or "").split())
            if "canonical" in rel:
                self.canonical = values.get("href") or ""
            if "manifest" in rel:
                self.has_manifest = bool(values.get("href"))
            if "icon" in rel:
                self.has_favicon = bool(values.get("href"))
            if "apple-touch-icon" in rel:
                self.has_apple_touch_icon = bool(values.get("href"))

        if tag == "meta":
            if values.get("property") == "og:url":
                self.og_url = values.get("content") or ""
            if values.get("property") == "og:image":
                self.og_image = values.get("content") or ""
            if values.get("property") == "og:site_name":
                self.og_site_name = values.get("content") or ""
            if values.get("name") == "twitter:url":
                self.twitter_url = values.get("content") or ""
            if values.get("name") == "twitter:image":
                self.twitter_image = values.get("content") or ""

        if tag == "img":
            if "alt" not in values:
                self.errors.append(f"altのない画像: {values.get('src', '(srcなし)')}")
            if values.get("src") == APP_STORE_BADGE_URL:
                self.app_store_badges += 1
            classes = set((values.get("class") or "").split())
            if "support-screenshot" in classes and (
                values.get("width"), values.get("height")
            ) != ("720", "1564"):
                self.errors.append(
                    "support-screenshotのwidth・height属性が不正"
                )

        if "style" in values:
            self.errors.append(f"インラインstyleを使用: <{tag}>")

        if tag == "a":
            href = values.get("href", "")
            if href == "https://x.com/MyKyudoNote":
                self.x_links += 1
            if href == APP_STORE_URL:
                self.app_store_links += 1
            if values.get("target") == "_blank":
                rel = set((values.get("rel") or "").split())
                if not {"noopener", "noreferrer"}.issubset(rel):
                    self.errors.append(
                        f'target="_blank"にnoopener noreferrerがない: {href}'
                    )

        if tag == "script":
            self.scripts.append(
                (
                    values.get("src") or "",
                    "async" in values,
                    self.head_depth > 0,
                )
            )

        for attr in ("href", "src"):
            if reference := values.get(attr):
                self.local_references.append((attr, reference))

        if srcset := values.get("srcset"):
            for candidate in srcset.split(","):
                reference = candidate.strip().split()[0]
                self.local_references.append(("srcset", reference))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title" and self.title_depth:
            self.title_depth -= 1
        if tag == "head" and self.head_depth:
            self.head_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.title_depth:
            self.title_text.append(data)


def validate_page(path: Path) -> list[str]:
    parser = PageParser()
    source = path.read_text(encoding="utf-8")
    parser.feed(source)
    errors = list(parser.errors)

    if not "".join(parser.title_text).strip():
        errors.append("titleがない")
    if not parser.has_description:
        errors.append("meta descriptionがない")
    if not parser.canonical:
        errors.append("canonicalがない")

    relative = path.relative_to(ROOT).as_posix()
    if LEGACY_SUPPORT_EMAIL in source:
        errors.append("旧サポートメールアドレスが残っている")
    if relative in {"support.html", "privacy.html", "privacy/index.html"}:
        expected_mailto = f'mailto:{SUPPORT_EMAIL}'
        if expected_mailto not in source:
            errors.append(f"新サポートメールへのリンクがない: {expected_mailto}")
        if SUPPORT_EMAIL not in source:
            errors.append(f"新サポートメールアドレスの表示がない: {SUPPORT_EMAIL}")

    canonical_paths = {
        "index.html": "/",
        "support.html": "/support.html",
        "privacy.html": "/privacy",
        "privacy/index.html": "/privacy",
        "404.html": "/404.html",
        "releases/index.html": "/releases/",
        "releases/v7-0-0.html": "/releases/v7-0-0.html",
        "releases/v7-1-0.html": "/releases/v7-1-0.html",
        "releases/v7-1-1.html": "/releases/v7-1-1.html",
        "releases/v7-1-2.html": "/releases/v7-1-2.html",
        "releases/v7-1-3.html": "/releases/v7-1-3.html",
        "releases/v7-2-0.html": "/releases/v7-2-0.html",
        "releases/v7-2-1.html": "/releases/v7-2-1.html",
        "releases/v7-2-2.html": "/releases/v7-2-2.html",
        "releases/v7-2-3.html": "/releases/v7-2-3.html",
        "releases/v7-2-4.html": "/releases/v7-2-4.html",
        "releases/v7-2-5.html": "/releases/v7-2-5.html",
        "releases/v7-2-6.html": "/releases/v7-2-6.html",
        "releases/v7-3-1.html": "/releases/v7-3-1.html",
        "releases/v7-3-2.html": "/releases/v7-3-2.html",
        "releases/v7-4-0.html": "/releases/v7-4-0.html",
        "releases/v7-4-1.html": "/releases/v7-4-1.html",
    }
    expected_url = f"{SITE_ORIGIN}{canonical_paths[relative]}"
    if parser.canonical and parser.canonical != expected_url:
        errors.append(f"canonicalが独自ドメインURLではない: {parser.canonical}")
    if parser.og_url != expected_url:
        errors.append(f"og:urlが不正: {parser.og_url or '(なし)'}")
    if parser.og_site_name != "Kyudo JAPAN":
        errors.append(f"og:site_nameが不正: {parser.og_site_name or '(なし)'}")
    if parser.twitter_url != expected_url:
        errors.append(f"twitter:urlが不正: {parser.twitter_url or '(なし)'}")
    expected_image = f"{SITE_ORIGIN}/assets/images/ogp-1200x630.png"
    if parser.og_image != expected_image:
        errors.append(f"og:imageが不正: {parser.og_image or '(なし)'}")
    if parser.twitter_image != expected_image:
        errors.append(f"twitter:imageが不正: {parser.twitter_image or '(なし)'}")
    if not parser.has_manifest:
        errors.append("Web Manifestへのリンクがない")
    if not parser.has_favicon:
        errors.append("faviconへのリンクがない")
    if not parser.has_apple_touch_icon:
        errors.append("apple-touch-iconへのリンクがない")

    expected_analytics_src = (
        "assets/js/analytics.js"
        if path.parent == ROOT
        else "../assets/js/analytics.js"
    )
    analytics_scripts = [
        script for script in parser.scripts
        if script[0].endswith("assets/js/analytics.js")
    ]
    if len(analytics_scripts) != 1:
        errors.append(
            f"GA4共通ローダーが1つではない: {len(analytics_scripts)}個"
        )
    else:
        src, is_async, is_in_head = analytics_scripts[0]
        if src != expected_analytics_src:
            errors.append(f"GA4共通ローダーの相対パスが不正: {src}")
        if not is_async:
            errors.append("GA4共通ローダーにasync属性がない")
        if not is_in_head:
            errors.append("GA4共通ローダーがhead内にない")

    direct_google_tags = [
        src for src, _, _ in parser.scripts
        if "googletagmanager.com/gtag/js" in src
    ]
    if direct_google_tags:
        errors.append("GoogleタグをHTMLへ直接記述している")
    if re.search(r"\bG-[A-Z0-9]+\b", source):
        errors.append("Measurement IDをHTMLへ直接記述している")

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
    if relative in {"index.html", "releases/index.html"} and parser.app_store_links == 0:
        errors.append("公開中のApp Storeリンクがない")
    expected_app_store_badges = {
        "index.html": 2,
        "releases/index.html": 1,
        "releases/v7-2-6.html": 1,
    }
    if relative in expected_app_store_badges:
        expected_badge_count = expected_app_store_badges[relative]
        if parser.app_store_badges != expected_badge_count:
            errors.append(
                f"Apple公式App Storeバッジが{expected_badge_count}点ではない: "
                f"{parser.app_store_badges}点"
            )
        trademark_notice = (
            "Apple、Appleのロゴ、およびApp Storeは、"
        )
        if trademark_notice not in source:
            errors.append("Appleの商標クレジットがない")

    if relative == "releases/index.html":
        if f"現行バージョン：{CURRENT_IOS_VERSION}" not in source:
            errors.append("iOSの現行バージョンが明記されていない")
        if "現行バージョン：なし" not in source:
            errors.append("Androidに現行バージョンがないことが明記されていない")
        if (
            '<span class="status">App Store配信中</span>\n'
            '          <h2><a href="v7-3-2.html">Version 7.3.2</a></h2>'
        ) not in source:
            errors.append("Version 7.3.2がApp Store配信中になっていない")
        if (
            '<span class="status">過去の公開版</span>\n'
            '          <h2><a href="v7-3-1.html">Version 7.3.1</a></h2>'
        ) not in source:
            errors.append("Version 7.3.1が過去の公開版になっていない")
        if (
            '<span class="status">過去の公開版</span>\n'
            '          <h2><a href="v7-2-6.html">Version 7.2.6</a></h2>'
        ) not in source:
            errors.append("Version 7.2.6が過去の公開版になっていない")
        if (
            '<span class="status">過去の公開版</span>\n'
            '          <h2><a href="v7-2-5.html">Version 7.2.5</a></h2>'
        ) not in source:
            errors.append("Version 7.2.5が過去の公開版になっていない")

    if relative == f"releases/v{CURRENT_IOS_VERSION.replace('.', '-')}.html":
        if "App Store配信中" not in source:
            errors.append("現行iOS版がApp Store配信中と明記されていない")

    if relative == "releases/v7-3-1.html":
        if "過去の公開版" not in source:
            errors.append("Version 7.3.1が過去の公開版と明記されていない")
        if "Version 7.3.1は、過去の公開版です" not in source:
            errors.append("Version 7.3.1の過去版状態が明記されていない")

    if relative == "releases/v7-3-2.html":
        if "App Store配信中" not in source:
            errors.append("Version 7.3.2がApp Store配信中と明記されていない")
        if "Version 7.3.2は、現在App Storeで公開中です" not in source:
            errors.append("Version 7.3.2の公開状態が明記されていない")

    stale_public_copy = {
        "初回公開前": "公開前の案内が残っている",
        "現行公開版なし": "iOS公開前の案内が残っている",
        "公開予定：未定": "公開予定の古い案内が残っている",
        "最新リリース候補 Version 7.2.6": (
            "未公開版を現行版と誤認させる案内が残っている"
        ),
        "現行公開版 Version 7.2.5": (
            "旧iOS現行バージョンの案内が残っている"
        ),
        "現行公開版はVersion 7.2.5": (
            "旧iOS現行バージョンの案内が残っている"
        ),
        "次期アップデート候補": "未公開版の案内が残っている",
        "開発中・未公開": "未公開版の案内が残っている",
        "App Storeの現行公開版ではありません": (
            "現行公開版ではないという案内が残っている"
        ),
        "承認済み": "利用者向けHTMLに内部工程の表現が残っている",
        "DB Schema 15": "利用者向けHTMLに内部Schema番号が残っている",
        "Build 16": "利用者向けHTMLに内部Build番号が残っている",
        "Build 17": "利用者向けHTMLに内部Build番号が残っている",
    }
    for stale_text, message in stale_public_copy.items():
        if stale_text in source:
            errors.append(f"{message}: {stale_text}")

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


def validate_png(
    path: Path,
    expected_size: tuple[int, int],
    *,
    allow_alpha: bool = False,
) -> list[str]:
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
    if not allow_alpha and data[25] in {4, 6}:
        errors.append(f"{path.relative_to(ROOT)}: アルファチャンネルが残っている")
    return errors


def main() -> int:
    errors: list[str] = []
    for page in HTML_FILES:
        errors.extend(validate_page(page))

    if not ANALYTICS_SCRIPT.exists():
        errors.append("GA4共通ローダーがない: assets/js/analytics.js")
        analytics_source = ""
    else:
        analytics_source = ANALYTICS_SCRIPT.read_text(encoding="utf-8")
    measurement_id_match = GA_MEASUREMENT_ID_PATTERN.search(analytics_source)
    if measurement_id_match is None:
        measurement_id = ""
        errors.append("GA4共通ローダーにMeasurement ID設定がない")
    else:
        measurement_id = measurement_id_match.group("id")
    if measurement_id and analytics_source.count(measurement_id) != 1:
        errors.append("GA4共通ローダーのMeasurement IDが1つではない")
    if analytics_source.count("https://www.googletagmanager.com/gtag/js") != 1:
        errors.append("GA4共通ローダーのGoogleタグURLが1つではない")
    if not re.search(r"\.async\s*=\s*true\b", analytics_source):
        errors.append("Googleタグがasyncで読み込まれていない")
    if 'window.gtag("config", measurementId)' not in analytics_source:
        errors.append("GA4のconfig呼び出しがない")
    if "__kyudoJapanGa4Initialized" not in analytics_source:
        errors.append("GA4共通ローダーに重複初期化防止がない")
    readme_source = (ROOT / "README.md").read_text(encoding="utf-8")
    if measurement_id and f"Measurement ID：`{measurement_id}`" not in readme_source:
        errors.append("READMEのMeasurement IDがGA4共通ローダーと一致しない")

    cname = (ROOT / "CNAME").read_text(encoding="utf-8").strip()
    if cname != "kyudojapan.net":
        errors.append(f"CNAMEが不正: {cname}")

    manifest_path = ROOT / "manifest.webmanifest"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"Web Manifestを読み込めない: {error}")
        manifest = {}
    for key, expected in {"id": "/", "start_url": "/", "scope": "/"}.items():
        if manifest.get(key) != expected:
            errors.append(f"Web Manifestの{key}が不正")
    icon_sizes = {icon.get("sizes") for icon in manifest.get("icons", [])}
    if not {"192x192", "512x512"}.issubset(icon_sizes):
        errors.append("Web Manifestに192px・512pxアイコンがない")

    index_source = (ROOT / "index.html").read_text(encoding="utf-8")
    json_ld_match = re.search(
        r'<script type="application/ld\+json">(?P<body>.*?)</script>',
        index_source,
        flags=re.DOTALL,
    )
    if json_ld_match is None:
        errors.append("トップページにJSON-LDがない")
    else:
        try:
            json_ld = json.loads(json_ld_match.group("body"))
        except json.JSONDecodeError as error:
            errors.append(f"JSON-LDが不正: {error}")
        else:
            serialized = json.dumps(json_ld, ensure_ascii=False)
            if '"@type": "Organization"' not in serialized:
                errors.append("JSON-LDにOrganizationがない")
            if '"@type": "WebSite"' not in serialized:
                errors.append("JSON-LDにWebSiteがない")
            if '"@type": "SoftwareApplication"' not in serialized:
                errors.append("JSON-LDにSoftwareApplicationがない")
            if f'"url": "{SITE_ORIGIN}/"' not in serialized:
                errors.append("JSON-LDのURLが独自ドメインではない")
            if f'"downloadUrl": "{APP_STORE_URL}"' not in serialized:
                errors.append("JSON-LDのApp Store URLが不正")

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if "Host: kyudojapan.net" not in robots:
        errors.append("robots.txtのHostが不正")
    if f"Sitemap: {SITE_ORIGIN}/sitemap.xml" not in robots:
        errors.append("robots.txtのSitemapが不正")

    sitemap_path = ROOT / "sitemap.xml"
    try:
        sitemap = sitemap_path.read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError) as error:
        errors.append(f"sitemap.xmlをUTF-8で読み込めない: {error}")
        sitemap = ""
    if sitemap and not sitemap.startswith(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
    ):
        errors.append("sitemap.xmlのXML宣言またはUTF-8指定が不正")
    try:
        expected_sitemap = render_sitemap()
    except ValueError as error:
        errors.append(f"サイトマップ設定が不正: {error}")
        expected_sitemap = ""
    if sitemap and expected_sitemap and sitemap != expected_sitemap:
        errors.append("sitemap.xmlがgenerate_sitemap.pyの設定と一致しない")

    if sitemap:
        try:
            sitemap_root = ET.fromstring(sitemap)
        except ET.ParseError as error:
            errors.append(f"sitemap.xmlのXMLが不正: {error}")
        else:
            namespace = f"{{{SITEMAP_NAMESPACE}}}"
            if sitemap_root.tag != f"{namespace}urlset":
                errors.append("sitemap.xmlのurlset名前空間が不正")
            sitemap_urls = sitemap_root.findall(f"{namespace}url")
            if len(sitemap_urls) != len(SITEMAP_ENTRIES):
                errors.append("sitemap.xmlのURL件数が設定と一致しない")
            for url in sitemap_urls:
                child_names = [child.tag for child in url]
                expected_names = [
                    f"{namespace}loc",
                    f"{namespace}lastmod",
                    f"{namespace}priority",
                ]
                if child_names != expected_names:
                    errors.append(
                        "sitemap.xmlのurl要素はloc・lastmod・priorityの順で指定する"
                    )
                    break

    if LEGACY_ORIGIN in sitemap or f"<loc>{SITE_ORIGIN}/</loc>" not in sitemap:
        errors.append("sitemap.xmlのURLが独自ドメインへ統一されていない")

    text_extensions = {
        ".html", ".js", ".md", ".xml", ".txt", ".yml", ".webmanifest"
    }
    legacy_analytics_patterns = {
        "Universal Analytics ID": r"\bUA-\d+-\d+\b",
        "analytics.js": r"google-analytics\.com/analytics\.js",
        "旧ga関数": r"\bga\s*\(\s*['\"]create['\"]",
        "旧_gaq": r"\b_gaq\b",
    }
    for source in ROOT.rglob("*"):
        if ".git" in source.parts or not source.is_file() or source.suffix not in text_extensions:
            continue
        source_text = source.read_text(encoding="utf-8")
        documented_dns_target = (
            source.name == "README.md"
            and source_text.count(LEGACY_ORIGIN) == 1
            and f"`{LEGACY_ORIGIN}` へ向けます" in source_text
        )
        if LEGACY_ORIGIN in source_text and not documented_dns_target:
            errors.append(f"旧github.io URLが残っている: {source.relative_to(ROOT)}")
        for label, pattern in legacy_analytics_patterns.items():
            if re.search(pattern, source_text, flags=re.IGNORECASE):
                errors.append(
                    f"古いAnalyticsコード（{label}）が残っている: "
                    f"{source.relative_to(ROOT)}"
                )

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

    for relative_path, expected_size in ALPHA_PNG_ASSETS.items():
        asset = ROOT / relative_path
        if not asset.exists():
            errors.append(f"必須アセットがない: {relative_path}")
        else:
            errors.extend(validate_png(asset, expected_size, allow_alpha=True))

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
