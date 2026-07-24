#!/usr/bin/env python3
"""GitHub Pagesへ配信する公開ファイルだけを_siteへ出力する。"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = ROOT / "_site"
STAGING_DIR = ROOT / "_site.tmp"

# 新しい公開ファイルや公開ディレクトリは、この2か所の一覧へ追加する。
PUBLIC_FILES = (
    Path(".nojekyll"),
    Path("404.html"),
    Path("CNAME"),
    Path("index.html"),
    Path("manifest.webmanifest"),
    Path("privacy.html"),
    Path("robots.txt"),
    Path("sitemap.xml"),
    Path("support.html"),
)
PUBLIC_DIRECTORIES = (
    Path("assets"),
    Path("privacy"),
    Path("releases"),
)

# 公開ディレクトリ内に置く保守資料は、ここで明示的に除外する。
EXCLUDED_PATHS = {
    Path("releases/README.md"),
}
FORBIDDEN_TOP_LEVEL_PATHS = {
    ".git",
    ".github",
    "docs",
    "outputs",
    "qa",
    "scripts",
}


class BuildError(RuntimeError):
    """公開物の構成に問題がある場合のエラー。"""


def remove_generated_path(path: Path) -> None:
    """生成先として許可したパスだけを安全に削除する。"""
    if path.parent != ROOT or path.name not in {"_site", "_site.tmp"}:
        raise BuildError(f"生成先以外は削除できない: {path}")
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def collect_public_files() -> dict[Path, Path]:
    """公開先の相対パスとコピー元を一元的に収集する。"""
    collected: dict[Path, Path] = {}

    for relative_path in PUBLIC_FILES:
        source = ROOT / relative_path
        if not source.is_file() or source.is_symlink():
            raise BuildError(f"公開ファイルが見つからない: {relative_path}")
        collected[relative_path] = source

    for relative_directory in PUBLIC_DIRECTORIES:
        source_directory = ROOT / relative_directory
        if not source_directory.is_dir() or source_directory.is_symlink():
            raise BuildError(
                f"公開ディレクトリが見つからない: {relative_directory}"
            )
        for source in sorted(source_directory.rglob("*")):
            if not source.is_file():
                continue
            relative_path = source.relative_to(ROOT)
            if relative_path in EXCLUDED_PATHS:
                continue
            if source.is_symlink():
                raise BuildError(f"シンボリックリンクは公開できない: {relative_path}")
            if relative_path in collected:
                raise BuildError(f"公開パスが重複している: {relative_path}")
            collected[relative_path] = source

    return collected


def validate_artifact(
    artifact_directory: Path,
    public_files: dict[Path, Path],
) -> list[str]:
    """生成物が公開元と一致し、内部資料を含まないことを検証する。"""
    errors: list[str] = []
    if not artifact_directory.is_dir() or artifact_directory.is_symlink():
        return [f"公開用ディレクトリがない: {artifact_directory.name}"]

    expected_paths = set(public_files)
    actual_paths = {
        path.relative_to(artifact_directory)
        for path in artifact_directory.rglob("*")
        if path.is_file()
    }

    for missing in sorted(expected_paths - actual_paths):
        errors.append(f"公開物に必要なファイルがない: {missing}")
    for unexpected in sorted(actual_paths - expected_paths):
        errors.append(f"公開物に未承認ファイルがある: {unexpected}")

    for relative_path in sorted(expected_paths & actual_paths):
        source = public_files[relative_path]
        artifact = artifact_directory / relative_path
        if artifact.is_symlink():
            errors.append(f"公開物にシンボリックリンクがある: {relative_path}")
        elif source.read_bytes() != artifact.read_bytes():
            errors.append(f"公開元と内容が一致しない: {relative_path}")

    for top_level_path in sorted(FORBIDDEN_TOP_LEVEL_PATHS):
        if (artifact_directory / top_level_path).exists():
            errors.append(f"内部用パスが公開物に含まれている: {top_level_path}")
    for excluded_path in sorted(EXCLUDED_PATHS):
        if (artifact_directory / excluded_path).exists():
            errors.append(f"除外対象が公開物に含まれている: {excluded_path}")

    return errors


def build_site() -> int:
    """公開物を一時ディレクトリへ生成し、検証後に_siteへ置き換える。"""
    try:
        public_files = collect_public_files()
        remove_generated_path(STAGING_DIR)
        STAGING_DIR.mkdir()

        for relative_path, source in public_files.items():
            destination = STAGING_DIR / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

        errors = validate_artifact(STAGING_DIR, public_files)
        if errors:
            raise BuildError("\n".join(errors))

        remove_generated_path(BUILD_DIR)
        STAGING_DIR.replace(BUILD_DIR)
    except (BuildError, OSError) as error:
        print(f"Pages artifact build failed:\n{error}", file=sys.stderr)
        return 1

    print(f"Pages artifact built: {len(public_files)} files")
    return 0


def check_site() -> int:
    """現在の_siteが公開元と完全に一致することを確認する。"""
    try:
        public_files = collect_public_files()
        errors = validate_artifact(BUILD_DIR, public_files)
    except (BuildError, OSError) as error:
        print(f"Pages artifact validation failed:\n{error}", file=sys.stderr)
        return 1

    if errors:
        print("Pages artifact validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Pages artifact validation passed: {len(public_files)} files")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="既存の_siteが公開元と一致するか確認する",
    )
    args = parser.parse_args()
    return check_site() if args.check else build_site()


if __name__ == "__main__":
    raise SystemExit(main())
