#!/usr/bin/env python3
"""Pull the site's generated content in from the repos that own it.

Four sources, none of them committed here:

  omle/docs/            → docs/spec/        the format specification, hand-written
  omle/docs/reference/  → docs/reference/   registry reference, generated from the
                                            operator and function registries
  omle-convert/docs/    → docs/converters/  per-framework support references
  omle-viewer           → docs/playground/  the self-contained viewer bundle

The first two come from one directory upstream, because omle keeps all its
documentation under docs/ with the generated reference in a subdirectory. They
stay two trees here so the published URLs are unchanged.

Resolution order for each repo, so a local edit can be previewed without a
release and CI needs no extra configuration:

  1. a sibling checkout (../omle, ../omle-convert, ../omle-viewer) or an
     explicit --omle / --omle-convert / --omle-viewer path
  2. OMLE_REPO_REF (default "main") cloned from GitHub

The viewer bundle is a build artifact and is gitignored in its own repo, so it
is taken from a sibling checkout's build output when present, and otherwise
extracted from the published wheel on PyPI. That keeps this script free of any
npm dependency: a site build needs Python only.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
DOCS = SITE / "docs"
REF = "OMLE_REPO_REF"


def log(msg: str) -> None:
    print(f"[sync] {msg}", file=sys.stderr)


def fail(msg: str) -> None:
    print(f"[sync] error: {msg}", file=sys.stderr)
    sys.exit(1)


def resolve_repo(name: str, explicit: str | None, tmp: Path) -> Path:
    """Return a checkout of *name*, preferring a local one."""
    if explicit:
        p = Path(explicit).expanduser().resolve()
        if not p.is_dir():
            fail(f"--{name}: not a directory: {p}")
        log(f"{name}: using {p}")
        return p

    sibling = SITE.parent / name
    if sibling.is_dir():
        log(f"{name}: using sibling checkout {sibling}")
        return sibling

    ref = os.environ.get(REF, "main")
    dest = tmp / name
    log(f"{name}: cloning openmle/{name}@{ref}")
    try:
        subprocess.run(
            ["git", "clone", "--depth=1", "--branch", ref,
             f"https://github.com/openmle/{name}.git", str(dest)],
            check=True, capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        fail(f"{name}: clone failed: {e.stderr.decode(errors='replace').strip()}")
    return dest


def copy_markdown(src_dir: Path, dst_dir: Path, *, rewrite: dict[str, str],
                  exclude: tuple[str, ...] = ()) -> int:
    """Copy *.md from src_dir to dst_dir, rewriting inter-document links.

    *exclude* names top-level subdirectories of src_dir to skip. The spec copy
    needs it: upstream keeps the generated reference inside the same docs/ tree,
    and it is synced separately into its own destination.
    """
    if not src_dir.is_dir():
        fail(f"expected a directory: {src_dir}")
    if dst_dir.exists():
        shutil.rmtree(dst_dir)
    dst_dir.mkdir(parents=True)

    count = 0
    for src in sorted(src_dir.rglob("*.md")):
        rel = src.relative_to(src_dir)
        if rel.parts and rel.parts[0] in exclude:
            continue
        dst = dst_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        text = src.read_text(encoding="utf-8")
        for old, new in rewrite.items():
            text = text.replace(old, new)
        dst.write_text(text, encoding="utf-8")
        count += 1
    return count


# Links in the source repo are relative to the repo, and two kinds of them do
# not survive the move onto the site:
#
#   ../docs/...      the registry reference, which lives under reference/ here
#   ../protobuf/...  source files the site does not publish, so they point at
#                    GitHub instead
#
# `mkdocs build --strict` fails on any link it cannot resolve, which is what
# catches a new one of these being introduced upstream.
def github_blob(repo: str) -> str:
    """Base URL for linking a source file the site does not publish."""
    return f"https://github.com/openmle/{repo}/blob/{os.environ.get(REF, 'main')}"


GITHUB_BLOB = github_blob("omle")

LINK_REWRITES = {
    # Upstream, the spec pages and the reference share one docs/ tree, so they
    # link to it as "reference/...". Here the two are siblings, so the link has
    # to climb out of spec/ first.
    "](reference/": "](../reference/",
    "](../protobuf/": f"]({GITHUB_BLOB}/protobuf/",
}


# The converter pages link up out of docs/ to files at their own repo root, which
# the site does not publish — and that root is omle-convert, not omle, so they
# cannot share GITHUB_BLOB. Their sibling links (sklearn.md and friends) need no
# rewriting: those pages travel together into docs/converters/.
CONVERTERS_LINK_REWRITES = {
    "](../README.md": f"]({github_blob('omle-convert')}/README.md",
    "](../CONTRIBUTING.md": f"]({github_blob('omle-convert')}/CONTRIBUTING.md",
}


def sync_spec(omle: Path) -> None:
    n = copy_markdown(omle / "docs", DOCS / "spec", rewrite=LINK_REWRITES,
                      exclude=("reference",))
    log(f"spec: {n} page(s)")


def sync_reference(omle: Path) -> None:
    n = copy_markdown(omle / "docs" / "reference", DOCS / "reference",
                      rewrite=LINK_REWRITES)
    log(f"reference: {n} page(s)")


def sync_converters(omle_convert: Path) -> None:
    n = copy_markdown(omle_convert / "docs", DOCS / "converters",
                      rewrite=CONVERTERS_LINK_REWRITES)
    log(f"converters: {n} page(s)")


def viewer_from_checkout(repo: Path) -> Path | None:
    """The viewer bundle from a local build, if one has been made."""
    for candidate in (
        repo / "python" / "src" / "omle_viewer" / "static" / "viewer.html",
        repo / "dist-singlefile" / "index.html",
    ):
        if candidate.is_file():
            return candidate
    return None


def viewer_from_pypi(tmp: Path) -> Path:
    """Extract viewer.html from the published omle-viewer wheel."""
    log("viewer: downloading omle-viewer wheel from PyPI")
    out = tmp / "wheel"
    out.mkdir()
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "download", "--no-deps", "--only-binary", ":all:",
             "-d", str(out), "omle-viewer"],
            check=True, capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        fail("viewer: pip download failed: "
             + e.stderr.decode(errors="replace").strip()[-400:])

    wheels = sorted(out.glob("omle_viewer-*.whl"))
    if not wheels:
        fail("viewer: no omle-viewer wheel downloaded")
    with zipfile.ZipFile(wheels[-1]) as z:
        members = [m for m in z.namelist() if m.endswith("static/viewer.html")]
        if not members:
            fail(f"viewer: {wheels[-1].name} has no static/viewer.html")
        z.extract(members[0], out)
        return out / members[0]


def sync_playground(viewer_repo: Path, tmp: Path) -> None:
    src = viewer_from_checkout(viewer_repo)
    if src:
        log(f"viewer: using local build {src}")
    else:
        # Gitignored in its own repo as a build artifact, so a fresh clone has
        # no copy of it; the published wheel does.
        src = viewer_from_pypi(tmp)

    dst_dir = DOCS / "playground"
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / "viewer.html"
    shutil.copyfile(src, dst)
    log(f"viewer: {dst.stat().st_size:,} bytes → {dst.relative_to(SITE)}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--omle", help="path to an omle checkout")
    ap.add_argument("--omle-convert", dest="omle_convert",
                    help="path to an omle-convert checkout")
    ap.add_argument("--omle-viewer", dest="omle_viewer",
                    help="path to an omle-viewer checkout")
    args = ap.parse_args()

    with tempfile.TemporaryDirectory(prefix="omle_site_") as td:
        tmp = Path(td)
        omle = resolve_repo("omle", args.omle, tmp)
        sync_spec(omle)
        sync_reference(omle)
        convert_repo = resolve_repo("omle-convert", args.omle_convert, tmp)
        sync_converters(convert_repo)
        viewer_repo = resolve_repo("omle-viewer", args.omle_viewer, tmp)
        sync_playground(viewer_repo, tmp)

    log("done")


if __name__ == "__main__":
    main()
