#!/usr/bin/env python3
"""Kyudo JAPAN公式サイトのXMLサイトマップを生成する。"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parent.parent
SITEMAP_PATH = ROOT / "sitemap.xml"
SITE_ORIGIN = "https://kyudojapan.net"
SITEMAP_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"


@dataclass(frozen=True)
class SitemapEntry:
    source: str
    path: str
    lastmod: str
    priority: str


# 公開URLの追加・更新はこの一覧だけを変更し、スクリプトを実行する。
SITEMAP_ENTRIES = (
    SitemapEntry("index.html", "/", "2026-08-02", "1.0"),
    SitemapEntry("guide/index.html", "/guide/", "2026-08-06", "0.8"),
    SitemapEntry("support.html", "/support.html", "2026-07-26", "0.8"),
    SitemapEntry("privacy/index.html", "/privacy", "2026-07-26", "0.8"),
    SitemapEntry("releases/index.html", "/releases/", "2026-08-02", "0.6"),
    SitemapEntry(
        "releases/v7-4-1.html",
        "/releases/v7-4-1.html",
        "2026-08-02",
        "0.6",
    ),
    SitemapEntry(
        "releases/v7-4-0.html",
        "/releases/v7-4-0.html",
        "2026-08-02",
        "0.6",
    ),
    SitemapEntry(
        "releases/v7-3-2.html",
        "/releases/v7-3-2.html",
        "2026-08-01",
        "0.6",
    ),
    SitemapEntry(
        "releases/v7-3-1.html",
        "/releases/v7-3-1.html",
        "2026-08-01",
        "0.6",
    ),
    SitemapEntry(
        "releases/v7-2-6.html",
        "/releases/v7-2-6.html",
        "2026-07-26",
        "0.6",
    ),
    SitemapEntry(
        "releases/v7-2-5.html",
        "/releases/v7-2-5.html",
        "2026-07-26",
        "0.6",
    ),
    SitemapEntry(
        "releases/v7-2-4.html",
        "/releases/v7-2-4.html",
        "2026-07-26",
        "0.7",
    ),
    SitemapEntry(
        "releases/v7-2-3.html",
        "/releases/v7-2-3.html",
        "2026-07-26",
        "0.7",
    ),
    SitemapEntry(
        "releases/v7-2-2.html",
        "/releases/v7-2-2.html",
        "2026-07-26",
        "0.7",
    ),
    SitemapEntry(
        "releases/v7-2-1.html",
        "/releases/v7-2-1.html",
        "2026-07-26",
        "0.6",
    ),
    SitemapEntry(
        "releases/v7-2-0.html",
        "/releases/v7-2-0.html",
        "2026-07-26",
        "0.6",
    ),
    SitemapEntry(
        "releases/v7-1-3.html",
        "/releases/v7-1-3.html",
        "2026-07-26",
        "0.6",
    ),
    SitemapEntry(
        "releases/v7-1-2.html",
        "/releases/v7-1-2.html",
        "2026-07-26",
        "0.6",
    ),
    SitemapEntry(
        "releases/v7-1-1.html",
        "/releases/v7-1-1.html",
        "2026-07-26",
        "0.6",
    ),
    SitemapEntry(
        "releases/v7-1-0.html",
        "/releases/v7-1-0.html",
        "2026-07-26",
        "0.6",
    ),
    SitemapEntry(
        "releases/v7-0-0.html",
        "/releases/v7-0-0.html",
        "2026-07-26",
        "0.5",
    ),
)


def validate_entries(entries: tuple[SitemapEntry, ...] = SITEMAP_ENTRIES) -> None:
    seen_paths: set[str] = set()
    for entry in entries:
        if entry.path in seen_paths:
            raise ValueError(f"URLパスが重複している: {entry.path}")
        seen_paths.add(entry.path)

        if not entry.path.startswith("/") or "#" in entry.path:
            raise ValueError(f"URLパスが不正: {entry.path}")

        source_path = (ROOT / entry.source).resolve()
        if ROOT not in source_path.parents or not source_path.is_file():
            raise ValueError(f"公開元HTMLが見つからない: {entry.source}")

        try:
            normalized_lastmod = date.fromisoformat(entry.lastmod).isoformat()
        except ValueError as error:
            raise ValueError(f"lastmodが不正: {entry.lastmod}") from error
        if normalized_lastmod != entry.lastmod:
            raise ValueError(f"lastmodはYYYY-MM-DD形式で指定する: {entry.lastmod}")

        try:
            priority = Decimal(entry.priority)
        except InvalidOperation as error:
            raise ValueError(f"priorityが不正: {entry.priority}") from error
        if not Decimal("0.0") <= priority <= Decimal("1.0"):
            raise ValueError(f"priorityが範囲外: {entry.priority}")


def render_sitemap(entries: tuple[SitemapEntry, ...] = SITEMAP_ENTRIES) -> str:
    validate_entries(entries)
    ET.register_namespace("", SITEMAP_NAMESPACE)
    urlset = ET.Element(f"{{{SITEMAP_NAMESPACE}}}urlset")

    for entry in entries:
        url = ET.SubElement(urlset, f"{{{SITEMAP_NAMESPACE}}}url")
        ET.SubElement(url, f"{{{SITEMAP_NAMESPACE}}}loc").text = (
            f"{SITE_ORIGIN}{entry.path}"
        )
        ET.SubElement(url, f"{{{SITEMAP_NAMESPACE}}}lastmod").text = entry.lastmod
        ET.SubElement(url, f"{{{SITEMAP_NAMESPACE}}}priority").text = entry.priority

    ET.indent(urlset, space="  ")
    body = ET.tostring(urlset, encoding="unicode", short_empty_elements=True)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{body}\n'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="sitemap.xmlが現在の設定から生成した内容と一致するか確認する",
    )
    args = parser.parse_args()

    try:
        expected = render_sitemap()
    except ValueError as error:
        print(f"Sitemap configuration error: {error}", file=sys.stderr)
        return 1

    if args.check:
        try:
            current = SITEMAP_PATH.read_bytes().decode("utf-8")
        except (OSError, UnicodeDecodeError) as error:
            print(f"sitemap.xmlをUTF-8で読み込めない: {error}", file=sys.stderr)
            return 1
        if current != expected:
            print(
                "sitemap.xmlが設定と一致しない。\n"
                "python3 scripts/generate_sitemap.pyを実行してください。",
                file=sys.stderr,
            )
            return 1
        print(f"Sitemap is up to date: {len(SITEMAP_ENTRIES)} URLs")
        return 0

    with SITEMAP_PATH.open("w", encoding="utf-8", newline="\n") as sitemap_file:
        sitemap_file.write(expected)
    print(f"Generated sitemap.xml: {len(SITEMAP_ENTRIES)} URLs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
