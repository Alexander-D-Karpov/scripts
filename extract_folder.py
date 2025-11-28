#!/usr/bin/env python3
"""
Dump selected repository files into a single text file, honoring .gitignore,
sensible default ignore patterns, and extracting **only text-readable files**
(no binary blobs).

What’s new:
- Much larger default ignore list (build artifacts, caches, lockfiles, etc.).
- Accept kwargs (safe to pass extra keyword arguments).
- Extensions accept "*" to mean "all".
- Excludes can be provided as a space-separated list (CLI) or any of: string with
  commas/whitespace, list/tuple; glob patterns supported (fnmatch).
- **Binary detection**: only text-like files are included (BOM/UTF-8 checks + heuristics).
  You can override with `--include-binary` if ever needed.

Examples:
  # Everything (respecting gitignore + defaults), write to data.txt
  python script.py .

  # Only py,md; space-separated excludes; auto output "data.py"
  python script.py . -e py,md -x migrations tests docs

  # All extensions ("*"), but still allow manual exclude patterns
  python script.py . -e "*" -x "node_modules dist build"

  # With keyword args from another Python module
  from script import structure_directory_content
  structure_directory_content(
      input_dir=".",
      extensions="py,go",
      exclude=["migrations", "node_modules"],
      output_file="repo_dump.txt",
  )
"""
import argparse
import codecs
import fnmatch
import os
import sys
from typing import Iterable, List, Optional, Sequence, Tuple, Union

import pathspec


def _default_garbage_patterns() -> List[str]:
    """
    A broad default set of ignore patterns using gitwildmatch semantics.
    These complement (not replace) patterns found in .gitignore.
    """
    return [
        # VCS
        "**/.git/**",
        "**/.hg/**",
        "**/.svn/**",

        # OS cruft
        "**/.DS_Store",
        "**/Thumbs.db",

        # Node / JS
        "**/node_modules/**",
        "**/package-lock.json",
        "**/yarn.lock",
        "**/pnpm-lock.yaml",
        "**/bun.lockb",
        "**/.yarn/**",
        "**/.pnpm-store/**",
        "**/.parcel-cache/**",
        "**/.next/**",
        "**/.nuxt/**",
        "**/jspm_packages/**",
        "**/bower_components/**",

        # Python
        "**/__pycache__/**",
        "**/*.pyc",
        "**/*.pyo",
        "**/.pytest_cache/**",
        "**/.mypy_cache/**",
        "**/.ruff_cache/**",
        "**/.tox/**",
        "**/.coverage*",
        "**/coverage.xml",
        "**/.cache/**",
        "**/*.egg-info/**",
        "**/.venv/**",
        "uv.lock",
        "**/venv/**",
        "**/env/**",
        "**/.ipynb_checkpoints/**",
        "poetry.lock",
        "Pipfile.lock",

        # Go
        "go.work.sum",
        "go.sum",
        "*_minimock.go",

        # Java / Kotlin / Gradle
        "**/.gradle/**",
        "**/build/**",
        "**/target/**",
        "**/out/**",

        # General IDE / project files
        "**/.idea/**",
        "**/.vscode/**",
        ".next/",
        ".idea/",
        ".gradle/",

        # Web frameworks / uploads
        "static/uploads/*",

        # Terraform / Serverless
        "**/.terraform/**",
        "**/terraform.tfstate*",
        "**/.serverless/**",

        # Compiled / binaries / artifacts
        "**/*.class",
        "**/*.o",
        "**/*.a",
        "**/*.so",
        "**/*.dll",
        "**/*.exe",
        "**/*.dylib",
        "**/*.dSYM/**",
        "**/*.log",

        # Misc build outputs
        "**/dist/**",
        "**/.angular/**",
        "**/.svelte-kit/**",

        # Migrations (from original)
        "migrations/*.py",
        "**/migrations/*.py",

        # Locks from original (explicit)
        "package-lock.json",
    ]


def read_gitignore(input_dir: str, extra_patterns: Optional[Sequence[str]] = None) -> pathspec.PathSpec:
    """
    Build a PathSpec from .gitignore (if present) + default garbage patterns.
    """
    default_patterns = _default_garbage_patterns()
    if extra_patterns:
        default_patterns.extend(extra_patterns)

    # Deduplicate while preserving order
    seen = set()
    merged_defaults = []
    for p in default_patterns:
        if p not in seen:
            seen.add(p)
            merged_defaults.append(p)

    gitignore_path = os.path.join(input_dir, ".gitignore")
    if os.path.isfile(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8", errors="ignore") as gitignore_file:
            patterns = merged_defaults + list(gitignore_file)
            return pathspec.PathSpec.from_lines("gitwildmatch", patterns)
    else:
        return pathspec.PathSpec.from_lines("gitwildmatch", merged_defaults)


def _parse_extensions(extensions: Optional[Union[str, Iterable[str]]]) -> Optional[List[str]]:
    """
    Normalize extensions.

    Returns:
      None -> accept all
      ["py", "md", ...] -> accept files ending in these extensions (case-insensitive)
    """
    if extensions is None:
        return None

    # If user passed list/tuple/set
    if isinstance(extensions, (list, tuple, set)):
        items = list(extensions)
    else:
        # Accept both comma- and whitespace-separated
        raw = extensions.strip()
        if raw == "" or raw == "*":
            return None
        # split on commas or whitespace
        parts = [p for chunk in raw.split(",") for p in chunk.split()]
        items = [p for p in parts if p]

    # If any item is "*" -> all
    if any(it == "*" for it in items):
        return None

    # Normalize: strip leading dots and lower
    norm = [it.lower().lstrip(".") for it in items if it.strip() != ""]
    return norm or None


def _parse_exclude(exclude: Optional[Union[str, Iterable[str]]]) -> List[str]:
    """
    Normalize exclude patterns. Supports:
    - string with commas and/or whitespace separators
    - list/tuple/set of strings
    Patterns can be substrings or globs (fnmatch).
    """
    if exclude is None:
        return []
    if isinstance(exclude, (list, tuple, set)):
        items = [str(x) for x in exclude]
    else:
        raw = exclude.strip()
        if not raw:
            return []
        # split on commas first, then on whitespace inside each token
        items = [p for chunk in raw.split(",") for p in chunk.split()]
    # remove empties, dedupe preserve order
    seen = set()
    out: List[str] = []
    for it in items:
        if it and it not in seen:
            seen.add(it)
            out.append(it)
    return out


def _matches_extension(filename: str, exts: Optional[Sequence[str]]) -> bool:
    if exts is None:
        return True
    lname = filename.lower()
    for ext in exts:
        if lname.endswith(f".{ext}"):
            return True
    return False


def _nontext_ratio(chunk: bytes) -> float:
    """
    Ratio of control characters (excluding common whitespace).
    Treats bytes 0x20..0xFF as text-like to avoid penalizing non-ASCII.
    """
    if not chunk:
        return 0.0
    allowed = {7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100))
    nontext = sum(1 for b in chunk if b not in allowed)
    return nontext / len(chunk)


def _probe_text_encoding(path: str, blocksize: int = 8192, default: str = "utf-8") -> Tuple[bool, Optional[str]]:
    """
    Heuristically determine if file is text-like and pick a reasonable encoding.

    Strategy:
      - Empty files -> text.
      - NUL byte -> binary.
      - BOMs for UTF-8/16/32 -> text with that encoding.
      - Try UTF-8 decode -> if ok, text (utf-8).
      - Fallback heuristic: control-char ratio < 0.30 -> text (encoding unknown).
    """
    try:
        with open(path, "rb") as f:
            chunk = f.read(blocksize)
    except (PermissionError, IsADirectoryError, FileNotFoundError, OSError):
        return False, None

    if not chunk:
        return True, default

    # Quick binary checks
    if b"\x00" in chunk:
        return False, None

    # BOMs
    if chunk.startswith(codecs.BOM_UTF8):
        return True, "utf-8-sig"
    if chunk.startswith(codecs.BOM_UTF16_LE) or chunk.startswith(codecs.BOM_UTF16_BE):
        return True, "utf-16"
    if chunk.startswith(codecs.BOM_UTF32_LE) or chunk.startswith(codecs.BOM_UTF32_BE):
        return True, "utf-32"

    # Try UTF-8
    try:
        chunk.decode("utf-8")
        return True, "utf-8"
    except UnicodeDecodeError:
        pass

    # Heuristic on control chars
    if _nontext_ratio(chunk) < 0.30:
        return True, None

    return False, None


def _is_excluded(rel_path: str, patterns: Sequence[str]) -> bool:
    """
    Returns True if rel_path should be excluded based on patterns.
    Supports glob-style patterns via fnmatch as well as simple substring checks.
    """
    if not patterns:
        return False
    for pat in patterns:
        # Glob match
        if fnmatch.fnmatch(rel_path, pat):
            return True
        # Substring match
        if pat in rel_path:
            return True
    return False


def structure_directory_content(
    input_dir: str,
    output_file: Optional[str] = None,
    extensions: Optional[Union[str, Iterable[str]]] = None,
    exclude: Optional[Union[str, Iterable[str]]] = None,
    *,
    encoding: str = "utf-8",
    include_binary: bool = False,
    **kwargs,
) -> None:
    """
    Walk input_dir, concatenate **text** file contents into output_file.

    Args:
        input_dir: Directory to scan.
        output_file: Path to write collected contents. Defaults to "data.txt"
                     or "data.<ext>" if a single explicit extension is provided.
        extensions: Comma/space-separated string, iterable, or "*" for all.
        exclude: Comma/space-separated string or iterable of patterns (substr or glob).
        encoding: Default encoding used to read files when detection is inconclusive.
        include_binary: If True, include files even when they look binary (NOT recommended).
        **kwargs: Accepted for forward-compatibility; ignored if unknown.
    """
    gitignore_spec = read_gitignore(input_dir)

    exts = _parse_extensions(extensions)
    excl = _parse_exclude(exclude)

    # Decide output filename
    if not output_file:
        if exts and len(exts) == 1:
            output_file = f"data.{exts[0]}"
        else:
            output_file = "data.txt"

    with open(output_file, "w", encoding=encoding, errors="ignore") as outfile:
        for root, dirs, files in os.walk(input_dir):
            # Prune ignored directories
            dirs[:] = [
                d for d in sorted(dirs)
                if not gitignore_spec.match_file(os.path.join(root, str(d)))
            ]
            # Filter files via .gitignore + defaults
            files = [
                f for f in sorted(files)
                if not gitignore_spec.match_file(os.path.join(root, str(f)))
            ]

            for file in files:
                if not _matches_extension(file, exts):
                    continue

                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, input_dir)

                if _is_excluded(relative_path, excl):
                    continue

                is_text, detected_enc = _probe_text_encoding(file_path)
                if not is_text and not include_binary:
                    continue

                enc_to_use = detected_enc or encoding
                try:
                    with open(file_path, "r", encoding=enc_to_use, errors="ignore") as infile:
                        data = infile.read()
                except (UnicodeDecodeError, PermissionError, IsADirectoryError, FileNotFoundError, OSError):
                    continue

                outfile.write(f"# {relative_path}\n")
                outfile.write(data)
                outfile.write("\n\n")


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Concatenate repository TEXT files into a single text file (respects .gitignore and sensible defaults)."
    )
    p.add_argument(
        "input_dir",
        nargs="?",
        default=".",
        help="Directory to scan (default: current directory).",
    )
    p.add_argument(
        "-o", "--output-file",
        dest="output_file",
        default=None,
        help="Output file path (default: data.txt or data.<ext> if single extension given).",
    )
    p.add_argument(
        "-e", "--extensions",
        dest="extensions",
        default=None,
        help='Comma/space-separated list of extensions (e.g., "py,md"). Use "*" for all.',
    )
    p.add_argument(
        "-x", "--exclude",
        dest="exclude",
        nargs="*",
        default=None,
        help="Space-separated exclude patterns (substr or glob). Commas within args are also supported.",
    )
    p.add_argument(
        "--encoding",
        dest="encoding",
        default="utf-8",
        help="Default encoding used to read files (fallback when detection is inconclusive).",
    )
    p.add_argument(
        "--include-binary",
        dest="include_binary",
        action="store_true",
        help="Include files even if they appear binary (NOT recommended).",
    )
    return p


def _from_cli(argv: Sequence[str]) -> None:
    # Backwards-compatible interactive mode if no CLI args
    if len(argv) == 1:
        input_directory = input("directory path: ").strip() or "."
        output_filename = input("output file name (optional): ").strip()
        file_extensions = input('file extensions separated by commas or spaces (optional, "*" for all): ').strip()
        exclude_patterns_input = input("exclude patterns separated by spaces or commas (optional): ").strip()

        structure_directory_content(
            input_dir=input_directory,
            output_file=output_filename if output_filename else None,
            extensions=file_extensions if file_extensions else None,
            exclude=exclude_patterns_input if exclude_patterns_input else None,
        )
        return

    parser = _build_arg_parser()
    args = parser.parse_args(argv[1:])

    # If exclude was provided as multiple space-separated args, join back into one string
    # so it can also accept commas inside tokens transparently.
    exclude_arg: Optional[Union[str, Iterable[str]]]
    if args.exclude is None:
        exclude_arg = None
    elif len(args.exclude) == 1:
        exclude_arg = args.exclude[0]
    else:
        exclude_arg = args.exclude  # already a list; parser will handle both

    structure_directory_content(
        input_dir=args.input_dir,
        output_file=args.output_file,
        extensions=args.extensions,
        exclude=exclude_arg,
        encoding=args.encoding,
        include_binary=args.include_binary,
    )


if __name__ == "__main__":
    _from_cli(sys.argv)

