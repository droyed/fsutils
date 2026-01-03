"""
DirManager utility class for working with directories.

This module provides a class for:
- Directory operations (create, list, delete)
- Path manipulation and validation
- File operations within a directory context
- Safe file operations with error handling
- Recursive file listing with extension filtering

Note: For simple file I/O operations (read, write, exists, etc.) that don't
require a base directory, use the io module instead:
    >>> from fsutils import io
    >>> data = io.read_json("config.json")
"""

import os
import shutil
import pathlib
from typing import Any, Dict, List, Union, Optional, Iterator, Literal
import datetime

# Type aliases
PathLike = Union[str, os.PathLike]
SortByType = Literal[None, 'name', 'mtime', 'size']


class DirManager:
    """A class for managing directories and files within a base directory.
    
    This class provides methods for directory operations with
    built-in error handling and path normalization.
    
    For file I/O operations that don't require a base directory, use
    the io module instead: from fsutils import io
    
    For detailed documentation, see:
    - USAGE_DirManager.md - Comprehensive usage guide
    - help(DirManager) - Quick reference for all methods
    """
    
    def __init__(self, base_dir: Optional[PathLike] = None):
        """Initialize the DirManager with an optional base directory.
        
        Args:
            base_dir: Optional base directory for relative path resolution.
                     If None, the current working directory is used.
        """
        self.base_dir = pathlib.Path(base_dir) if base_dir else pathlib.Path.cwd()
        if not self.base_dir.exists():
            raise ValueError(f"Base directory does not exist: {self.base_dir}")
    
    def __repr__(self) -> str:
        """Return an unambiguous string representation of the DirManager.
        
        Returns:
            String representation showing the class name and base_dir.
        """
        return f"DirManager(base_dir={self.base_dir!r})"
    
    def __str__(self) -> str:
        """Return a user-friendly string representation of the DirManager.
        
        Returns:
            Human-readable string showing the base directory path.
        """
        return f"DirManager({self.base_dir})"
    
    def __eq__(self, other: object) -> bool:
        """Check equality with another DirManager instance.
        
        Args:
            other: Object to compare with.
            
        Returns:
            True if other is a DirManager with the same base_dir, False otherwise.
        """
        if not isinstance(other, DirManager):
            return NotImplemented
        return self.base_dir == other.base_dir
    
    def __hash__(self) -> int:
        """Return a hash value for the DirManager instance.
        
        This allows DirManager instances to be used in sets and as dictionary keys.
        
        Returns:
            Hash value based on the base_dir path.
        """
        return hash(self.base_dir)
    
    def _resolve_path(self, path: PathLike) -> pathlib.Path:
        """Resolve a path relative to the base directory.
        
        Args:
            path: Path to resolve
            
        Returns:
            Resolved Path object
        """
        p = pathlib.Path(path)
        if p.is_absolute():
            return p
        return (self.base_dir / p).resolve()
    
    # =========================================================================
    # Directory Operations
    # =========================================================================
    
    def create_dir(self, path: PathLike, exist_ok: bool = True) -> pathlib.Path:
        """Create a directory.
        
        Args:
            path: Directory path to create
            exist_ok: If True, don't raise an error if directory already exists
            
        Returns:
            Path object for the created directory
            
        Raises:
            FileExistsError: If the directory already exists and exist_ok is False
        """
        p = self._resolve_path(path)
        p.mkdir(parents=True, exist_ok=exist_ok)
        return p

    def _format_path(self, p: pathlib.Path, relative: bool) -> pathlib.Path:
        """Helper to handle the relativity transformation."""
        return p.relative_to(self.base_dir) if relative else p

    def scan(
            self, 
            path: PathLike = '.', 
            sort_by: SortByType = None, 
            reverse: bool = False, 
            relative: bool = False
        ) -> List[pathlib.Path]:
            """
            Scan directory contents with optimized metadata sorting.
            
            Uses a Schwartzian Transform for O(N) metadata retrieval instead of 
            O(N log N) stat calls in traditional sorting approaches.
            
            Args:
                path: Directory path to scan (default: '.')
                sort_by: Sort criteria - 'name' (alphabetically, case-insensitive),
                        'mtime' (modification time), 'size' (file size), or None (default)
                reverse: If True, reverse the sort order (default: False)
                relative: If True, return paths relative to base_dir (default: False)
                
            Returns:
                List of Path objects for the directory contents
                
            Raises:
                NotADirectoryError: If path is not a directory or does not exist
                
            Note:
                This is the canonical method for listing directory contents. 
                The 'list_dir' method is deprecated and calls this method.
            """


            p = self._resolve_path(path)
            if not p.is_dir():
                raise NotADirectoryError(f"Path is not a directory or does not exist: {p}")
            
            # 1. Retrieval (The "Decorate" phase)
            # We fetch the stat object once and store it in a tuple with the path
            if sort_by == 'mtime':
                decorated = [(f.stat().st_mtime, f) for f in p.iterdir()]
            elif sort_by == 'size':
                # Folders don't have 'size' in the traditional sense; default to 0
                decorated = [(f.stat().st_size if f.is_file() else 0, f) for f in p.iterdir()]
            elif sort_by == 'name':
                decorated = [(f.name.lower(), f) for f in p.iterdir()]
            else:
                # No sorting needed, just grab the paths
                results = list(p.iterdir())
                return [self._format_path(f, relative) for f in results]

            # 2. Sort (The "Sort" phase)
            # Python's Timsort is stable and highly optimized for tuples
            decorated.sort(key=lambda x: x[0], reverse=reverse)

            # 3. Extraction (The "Undecorate" phase)
            return [self._format_path(f, relative) for _, f in decorated]
    
    def list_files(self, max_depth: Optional[int] = None, 
                   extensions: Optional[List[str]] = None,
                   sort_by: SortByType = None, reverse: bool = False,
                   relative: bool = False) -> List[pathlib.Path]:
        """List files in a directory recursively with optional filtering.
        
        Args:   
            max_depth: Maximum depth of recursion (None for unlimited)
            extensions: List of file extensions to filter by (e.g., ['.py', '.txt'])
            sort_by: Sort criteria - 'name' (alphabetically), 'mtime' (modification time),
                     'size' (file size), or None for no sorting (default)
            reverse: If True, reverse the sort order (default: False)
            relative: If True, return paths relative to base_dir (default: False)
            
        Returns:
            List of pathlib.Path objects for matching files
        """
        from fsutils.io import (
            IMAGE_EXTENSIONS, VIDEO_EXTENSIONS, 
            AUDIO_EXTENSIONS, DOCUMENT_EXTENSIONS
        )
        
        files = []
        
        # Ensure extensions is a list if provided
        if extensions and not isinstance(extensions, list):
            extensions = [extensions]
        
        def _walk(current_path: pathlib.Path, current_depth: int = 0):
            # Stop recursion if max_depth is reached
            if max_depth is not None and current_depth > max_depth:
                return
                
            # Process all items in the current directory
            try:
                for item in current_path.iterdir():
                    if item.is_file():
                        # If extensions filter is provided, check if file has one of the specified extensions
                        if not extensions or any(item.name.lower().endswith(ext.lower()) for ext in extensions):
                            files.append(item)
                    elif item.is_dir():
                        # Recursively process subdirectories
                        _walk(item, current_depth + 1)
            except PermissionError:
                # Skip directories we don't have permission to access
                pass
        
        # Start recursive walk from base directory
        _walk(self.base_dir)
        
        # Apply sorting if requested
        if sort_by is not None:
            if sort_by == 'name':
                files.sort(key=lambda x: x.name, reverse=reverse)
            elif sort_by == 'mtime':
                files.sort(key=lambda x: x.stat().st_mtime, reverse=reverse)
            elif sort_by == 'size':
                files.sort(key=lambda x: x.stat().st_size, reverse=reverse)
        
        if relative:
            files = [pathlib.Path(x.relative_to(self.base_dir)) for x in files]
        
        return files
    
    def list_images(self, max_depth: Optional[int] = None,
                    sort_by: SortByType = None, reverse: bool = False,
                    relative: bool = False) -> List[pathlib.Path]:
        """List all image files in a directory recursively.
        
        This is a convenience method that calls list_files() with the
        IMAGE_EXTENSIONS constant to filter for image files.
        
        Args:
            max_depth: Maximum depth of recursion (None for unlimited)
            sort_by: Sort criteria - 'name' (alphabetically), 'mtime' (modification time),
                     'size' (file size), or None for no sorting (default)
            reverse: If True, reverse the sort order (default: False)
            relative: If True, return paths relative to base_dir (default: False)
            
        Returns:
            List of pathlib.Path objects for image files
        """
        from fsutils.io import IMAGE_EXTENSIONS
        return self.list_files(max_depth=max_depth, extensions=IMAGE_EXTENSIONS,
                               sort_by=sort_by, reverse=reverse, relative=relative)
    
    @staticmethod
    def _get_dir_size(path: pathlib.Path) -> int:
        """Get total size of a directory.
        
        Args:
            path: Path to the directory
            
        Returns:
            Total size in bytes of all files in the directory
        """
        total_size = 0
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    total_size += item.stat().st_size
        except PermissionError:
            pass
        return total_size
    
    def list_subdirs(self, max_depth: Optional[int] = None,
                     sort_by: SortByType = None, reverse: bool = False,
                     relative: bool = False) -> List[pathlib.Path]:
        """List all subdirectories in a directory recursively.
        
        Args:
            max_depth: Maximum depth of recursion (None for unlimited, 0 = base_dir only)
            sort_by: Sort criteria - 'name' (alphabetically), 'mtime' (modification time),
                     'size' (total directory size), or None for no sorting (default)
            reverse: If True, reverse the sort order (default: False)
            relative: If True, return paths relative to base_dir (default: False)
            
        Returns:
            List of pathlib.Path objects for subdirectories including base_dir at depth 0
        """
        subdirs = []
        
        def _walk(current_path: pathlib.Path, current_depth: int = 0):
            # Add current directory to results (depth 0 = base_dir)
            if current_depth >= 0:
                subdirs.append(current_path)
            
            # Stop recursion if max_depth is reached
            # current_depth + 1 is the next level, so if we've reached max_depth, don't go deeper
            if max_depth is not None and current_depth >= max_depth:
                return
            
            # Process all items in the current directory
            try:
                for item in current_path.iterdir():
                    if item.is_dir():
                        # Recursively process subdirectories
                        _walk(item, current_depth + 1)
            except PermissionError:
                # Skip directories we don't have permission to access
                pass
        
        # Start recursive walk from base directory (depth 0)
        _walk(self.base_dir, 0)
        
        # Apply sorting if requested
        if sort_by is not None:
            if sort_by == 'name':
                subdirs.sort(key=lambda x: x.name, reverse=reverse)
            elif sort_by == 'mtime':
                subdirs.sort(key=lambda x: x.stat().st_mtime, reverse=reverse)
            elif sort_by == 'size':
                subdirs.sort(key=lambda x: self._get_dir_size(x), reverse=reverse)
        
        if relative:
            subdirs = [pathlib.Path(x.relative_to(self.base_dir)) for x in subdirs]
        
        return subdirs
    
    # =========================================================================
    # File Operations (require base_dir for relative paths)
    # =========================================================================
    
    def copy_file(self, src: PathLike, dst: PathLike, create_dirs: bool = True) -> pathlib.Path:
        """Copy a file.
        
        Args:
            src: Source file path
            dst: Destination file path
            create_dirs: If True, create parent directories if they don't exist
            
        Returns:
            Path object for the destination file
            
        Raises:
            FileNotFoundError: If the source file does not exist
            IsADirectoryError: If the source path is a directory
        """
        src_path = self._resolve_path(src)
        dst_path = self._resolve_path(dst)
        
        if not src_path.exists():
            raise FileNotFoundError(f"Source file does not exist: {src_path}")
        if not src_path.is_file():
            raise IsADirectoryError(f"Source path is a directory: {src_path}")
        
        if create_dirs:
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
        return pathlib.Path(shutil.copy2(src_path, dst_path))
    
    def move_file(self, src: PathLike, dst: PathLike, create_dirs: bool = True) -> pathlib.Path:
        """Move a file.
        
        Args:
            src: Source file path
            dst: Destination file path
            create_dirs: If True, create parent directories if they don't exist
            
        Returns:
            Path object for the destination file
            
        Raises:
            FileNotFoundError: If the source file does not exist
            IsADirectoryError: If the source path is a directory
        """
        src_path = self._resolve_path(src)
        dst_path = self._resolve_path(dst)
        
        if not src_path.exists():
            raise FileNotFoundError(f"Source file does not exist: {src_path}")
        if not src_path.is_file():
            raise IsADirectoryError(f"Source path is a directory: {src_path}")
        
        if create_dirs:
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
        return pathlib.Path(shutil.move(src_path, dst_path))
    
    def delete_dir(self, path: PathLike, recursive: bool = False) -> None:
        """Delete a directory.
        
        Args:
            path: Path to the directory to delete
            recursive: If True, recursively delete the directory and its contents
            
        Raises:
            FileNotFoundError: If the directory does not exist
            NotADirectoryError: If the path is not a directory
            OSError: If the directory is not empty and recursive is False
        """
        p = self._resolve_path(path)
        if not p.exists():
            raise FileNotFoundError(f"Directory does not exist: {p}")
        if not p.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {p}")
        
        if recursive:
            shutil.rmtree(p)
        else:
            p.rmdir()
    
    # =========================================================================
    # Path Pattern Matching
    # =========================================================================
    
    def glob(self, pattern: str, relative: bool = False) -> List[pathlib.Path]:
        """Find paths matching a glob pattern.
        
        Args:
            pattern: Glob pattern to match
            relative: If True, return paths relative to base_dir (default: False)
            
        Returns:
            List of matching Path objects
        """
        results = list(self.base_dir.glob(pattern))
        if relative:
            results = [pathlib.Path(x.relative_to(self.base_dir)) for x in results]
        return results
    
    def walk(self, top: PathLike = '.', relative: bool = False) -> Iterator[tuple[pathlib.Path, List[pathlib.Path], List[pathlib.Path]]]:
        """Walk a directory tree.
        
        Similar to os.walk, but returns Path objects instead of strings.
        
        Args:
            top: Directory to start walking from
            relative: If True, return paths relative to base_dir (default: False)
            
        Yields:
            Tuples of (dirpath, dirnames, filenames) where:
                - dirpath is a Path object for the current directory
                - dirnames is a list of Path objects for subdirectories
                - filenames is a list of Path objects for files
                
        Raises:
            FileNotFoundError: If the top directory does not exist
            NotADirectoryError: If the top path is not a directory
        """
        top_path = self._resolve_path(top)
        if not top_path.exists():
            raise FileNotFoundError(f"Directory does not exist: {top_path}")
        if not top_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {top_path}")
        
        for dirpath, dirnames, filenames in os.walk(top_path):
            dir_path = pathlib.Path(dirpath)
            # Convert to Path objects
            dirnames = [pathlib.Path(d) for d in dirnames]
            filenames = [pathlib.Path(f) for f in filenames]
            if relative:
                dir_path = pathlib.Path(dir_path.relative_to(self.base_dir))
                # Compute relative paths from full absolute paths
                dirnames = [pathlib.Path(pathlib.Path(dirpath, d).relative_to(self.base_dir)) for d in dirnames]
                filenames = [pathlib.Path(pathlib.Path(dirpath, f).relative_to(self.base_dir)) for f in filenames]
            yield (
                dir_path,
                dirnames,
                filenames
            )

    # =========================================================================
    # Directory Statistics
    # =========================================================================
    
    def display_stats(self, *, follow_symlinks: bool = False) -> None:
        """Display statistics about the base directory.
        
        This method uses the DirectoryAnalyzer to scan self.base_dir and
        prints directory statistics including:
        - File and directory counts
        - Total size and largest file
        - File extension breakdown
        - Modification time information
        - Empty directories and error counts
        
        Args:
            follow_symlinks: If True, follow symbolic links when scanning.
                           Default is False for safety.
        
        Raises:
            FileNotFoundError: If the base directory no longer exists.
        """
        from fsutils.dir_stats import (
            DirectoryAnalyzer,
            format_minimal_dir_stats_yaml,
        )
        
        analyzer = DirectoryAnalyzer()
        stats = analyzer.collect_minimal_dir_stats(
            self.base_dir,
            follow_symlinks=follow_symlinks,
        )
        print(format_minimal_dir_stats_yaml(stats))
