from __future__ import annotations

import os
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from typing import Tuple


@dataclass(frozen=True)
class MinimalDirStats:
    # Context
    root: Path

    # Structure
    file_count: int
    directory_count: int
    symlink_count: int

    # Size
    total_size_bytes: int
    largest_file_size_bytes: int
    largest_file_path: Path | None

    # Composition
    extension_count: dict[str, int]
    extension_size: dict[str, int]
    top_extensions_by_size: tuple[tuple[str, int], ...]
    top_extensions_by_count: tuple[tuple[str, int], ...]

    # Time
    oldest_mtime: float | None
    newest_mtime: float | None
    files_modified_last_30d: int

    # Hygiene
    empty_directories: int
    zero_byte_files: int
    hidden_files: int
    hidden_directories: int

    # Meta
    errors_count: int


class DirectoryAnalyzer:
    def collect_minimal_dir_stats(
        self,
        root: Path,
        *,
        follow_symlinks: bool = False,
    ):
        now = time.time()

        # Counters
        file_count = 0
        directory_count = 0
        symlink_count = 0
        empty_directories = 0
        zero_byte_files = 0
        hidden_files = 0
        errors_count = 0
        hidden_directories = 0

        # Size tracking
        total_size_bytes = 0
        largest_file_size_bytes = 0
        largest_file_path: Path | None = None

        # Time tracking
        oldest_mtime: float | None = None
        newest_mtime: float | None = None
        files_modified_last_30d = 0

        # Composition
        extension_count = defaultdict(int)
        extension_size = defaultdict(int)

        def scan_dir(path: Path) -> None:
            nonlocal file_count, directory_count, symlink_count
            nonlocal empty_directories, zero_byte_files, hidden_files, hidden_directories
            nonlocal errors_count, total_size_bytes
            nonlocal largest_file_size_bytes, largest_file_path
            nonlocal oldest_mtime, newest_mtime, files_modified_last_30d

            try:
                with os.scandir(path) as it:
                    entries = list(it)
            except OSError:
                errors_count += 1
                return

            directory_count += 1

            if not entries:
                empty_directories += 1

            for entry in entries:
                try:
                    if entry.is_symlink():
                        symlink_count += 1
                        if not follow_symlinks:
                            continue

                    if entry.is_dir(follow_symlinks=follow_symlinks):
                        if entry.name.startswith("."):
                            hidden_directories += 1

                        scan_dir(Path(entry.path))
                        continue

                    if entry.is_file(follow_symlinks=follow_symlinks):
                        file_count += 1

                        if entry.name.startswith("."):
                            hidden_files += 1

                        try:
                            st = entry.stat(follow_symlinks=follow_symlinks)
                        except OSError:
                            errors_count += 1
                            continue

                        size = st.st_size
                        total_size_bytes += size

                        if size == 0:
                            zero_byte_files += 1

                        if size > largest_file_size_bytes:
                            largest_file_size_bytes = size
                            largest_file_path = Path(entry.path)

                        suffix = Path(entry.name).suffix.lower() or "<none>"
                        extension_count[suffix] += 1
                        extension_size[suffix] += size

                        mtime = st.st_mtime
                        oldest_mtime = (
                            mtime if oldest_mtime is None else min(oldest_mtime, mtime)
                        )
                        newest_mtime = (
                            mtime if newest_mtime is None else max(newest_mtime, mtime)
                        )

                        if now - mtime <= 30 * 86400:
                            files_modified_last_30d += 1

                except OSError:
                    errors_count += 1

        scan_dir(root)

        TOP_N = 5

        top_extensions_by_size = sorted(
            extension_size.items(),
            key=lambda kv: kv[1],
            reverse=True,
        )[:TOP_N]

        top_extensions_by_count = sorted(
            extension_count.items(),
            key=lambda kv: kv[1],
            reverse=True,
        )[:TOP_N]

        return MinimalDirStats(
            root=root,

            file_count=file_count,
            directory_count=directory_count,
            symlink_count=symlink_count,
            total_size_bytes=total_size_bytes,
            largest_file_size_bytes=largest_file_size_bytes,
            largest_file_path=largest_file_path,
            extension_count=dict(extension_count),
            extension_size=dict(extension_size),
            top_extensions_by_size=tuple(top_extensions_by_size),
            top_extensions_by_count=tuple(top_extensions_by_count),
            oldest_mtime=oldest_mtime,
            newest_mtime=newest_mtime,
            files_modified_last_30d=files_modified_last_30d,
            empty_directories=empty_directories,
            zero_byte_files=zero_byte_files,
            hidden_files=hidden_files,
            hidden_directories=hidden_directories,
            errors_count=errors_count,
        )


class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"

    BLUE = "\033[34m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    MAGENTA = "\033[35m"
    DIM = "\033[2m"


def ext_icon(ext: str) -> str:
    ext = ext.lower()

    if ext in {".py"}:
        return "🐍"
    if ext in {".pyc"}:
        return "⚙️"
    if ext in {".md"}:
        return "📝"
    if ext in {".txt"}:
        return "📄"
    if ext in {".json", ".yaml", ".yml", ".toml"}:
        return "🧾"
    if ext in {".csv"}:
        return "📊"
    if ext in {".zip", ".tar", ".gz", ".bz2", ".xz"}:
        return "📦"
    if ext in {".so", ".dll"}:
        return "🧩"
    if ext == "<none>":
        return "❓"

    return "📄"  # sensible default


def format_minimal_dir_stats_yaml(stats: MinimalDirStats) -> str:
    def fmt_ext_oneline(
        items: tuple[tuple[str, int], ...],
        *,
        size: bool,
    ) -> str:
        if not items:
            return f"{C.DIM}-{C.RESET}"

        parts: list[str] = []
        for ext, val in items:
            icon = ext_icon(ext)
            value = fmt_bytes(val) if size else f"{val:,}"

            parts.append(
                f"{icon} "
                f"{C.BOLD}{ext:<7}{C.RESET} "
                f"{C.DIM}{value:<8}{C.RESET}"
            )

        # Use triple-space separator for consistent visual gaps
        return "   ".join(parts)

    def fmt_bytes(n: int) -> str:
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if n < 1024:
                return f"{n:.0f} {unit}"
            n /= 1024
        return f"{n:.0f} PB"

    # Severity-aware colors
    error_color = C.GREEN if stats.errors_count == 0 else C.RED
    recent_color = C.GREEN if stats.files_modified_last_30d > 0 else C.DIM

    # Largest file (filename only)
    largest = f"{C.DIM}-{C.RESET}"
    if stats.largest_file_path:
        largest = (
            f"{C.BOLD}{stats.largest_file_path.name}{C.RESET} "
            f"{C.DIM}({fmt_bytes(stats.largest_file_size_bytes)}){C.RESET}"
        )

    indent = "  "

    lines = [
        f"{C.BOLD}{C.BLUE}📁 {stats.root.resolve()}{C.RESET}",

        f"{indent}{C.CYAN}📄 Files:{C.RESET}        {C.BOLD}{stats.file_count:,}{C.RESET}",
        f"{indent}{C.CYAN}📁 Directories:{C.RESET}  {C.BOLD}{stats.directory_count:,}{C.RESET} "
        f"{C.DIM}(hidden: {stats.hidden_directories:,}){C.RESET}",
        f"{indent}{C.CYAN}🔗 Symlinks:{C.RESET}     {C.BOLD}{stats.symlink_count:,}{C.RESET}",

        f"{indent}{C.GREEN}💾 Total size:{C.RESET}   {C.BOLD}{fmt_bytes(stats.total_size_bytes)}{C.RESET}",
        f"{indent}{C.GREEN}📦 Largest file:{C.RESET} {largest}",

        f"{indent}{C.CYAN}📊 Top Extensions:{C.RESET}",

        f"{indent}  📦 By size   : "
        f"{fmt_ext_oneline(stats.top_extensions_by_size, size=True)}",

        f"{indent}  🔢 By count  : "
        f"{fmt_ext_oneline(stats.top_extensions_by_count, size=False)}",

        f"{indent}{C.MAGENTA}🆕 Recent files:{C.RESET} "
        f"{recent_color}{stats.files_modified_last_30d:,} (last 30 days){C.RESET}",

        f"{indent}{C.YELLOW}📭 Empty dirs:{C.RESET}   {stats.empty_directories:,}",
        f"{indent}{error_color}⚠️  Errors:{C.RESET}       {stats.errors_count:,}",
    ]

    return "\n".join(lines)


def _main() -> int:
    analyzer = DirectoryAnalyzer()
    path1 = Path("/home/diva/Projects/pippkgs/path_stats")
    if not path1.exists():
        print(f"Path does not exist: {path1}")
        return 2

    stats = analyzer.collect_minimal_dir_stats(path1)
    print(format_minimal_dir_stats_yaml(stats))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
