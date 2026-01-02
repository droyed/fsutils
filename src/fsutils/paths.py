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
    
    def list_dir(self, path: PathLike = '.', sort_by: SortByType = None, reverse: bool = False) -> List[pathlib.Path]:
        """List contents of a directory.
        
        Args:
            path: Directory path to list
            sort_by: Sort criteria - 'name' (alphabetically), 'mtime' (modification time),
                     'size' (file size), or None for no sorting (default)
            reverse: If True, reverse the sort order (default: False)
            
        Returns:
            List of Path objects for the directory contents
            
        Raises:
            FileNotFoundError: If the directory does not exist
            NotADirectoryError: If the path is not a directory
        """
        p = self._resolve_path(path)
        if not p.exists():
            raise FileNotFoundError(f"Directory does not exist: {p}")
        if not p.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {p}")
        
        contents = list(p.iterdir())
        
        if sort_by is not None:
            if sort_by == 'name':
                contents.sort(key=lambda x: x.name, reverse=reverse)
            elif sort_by == 'mtime':
                contents.sort(key=lambda x: x.stat().st_mtime, reverse=reverse)
            elif sort_by == 'size':
                contents.sort(key=lambda x: x.stat().st_size if x.is_file() else 0, reverse=reverse)
        
        return contents
    
    def list_files(self, max_depth: Optional[int] = None, 
                   extensions: Optional[List[str]] = None,
                   sort_by: SortByType = None, reverse: bool = False) -> List[pathlib.Path]:
        """List files in a directory recursively with optional filtering.
        
        Args:   
            max_depth: Maximum depth of recursion (None for unlimited)
            extensions: List of file extensions to filter by (e.g., ['.py', '.txt'])
            sort_by: Sort criteria - 'name' (alphabetically), 'mtime' (modification time),
                     'size' (file size), or None for no sorting (default)
            reverse: If True, reverse the sort order (default: False)
            
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
        
        return files
    
    def list_images(self, max_depth: Optional[int] = None,
                    sort_by: SortByType = None, reverse: bool = False) -> List[pathlib.Path]:
        """List all image files in a directory recursively.
        
        This is a convenience method that calls list_files() with the
        IMAGE_EXTENSIONS constant to filter for image files.
        
        Args:
            max_depth: Maximum depth of recursion (None for unlimited)
            sort_by: Sort criteria - 'name' (alphabetically), 'mtime' (modification time),
                     'size' (file size), or None for no sorting (default)
            reverse: If True, reverse the sort order (default: False)
            
        Returns:
            List of pathlib.Path objects for image files
        """
        from fsutils.io import IMAGE_EXTENSIONS
        return self.list_files(max_depth=max_depth, extensions=IMAGE_EXTENSIONS,
                               sort_by=sort_by, reverse=reverse)
    
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
    
    def glob(self, pattern: str) -> List[pathlib.Path]:
        """Find paths matching a glob pattern.
        
        Args:
            pattern: Glob pattern to match
            
        Returns:
            List of matching Path objects
        """
        return list(self.base_dir.glob(pattern))
    
    def walk(self, top: PathLike = '.') -> Iterator[tuple[pathlib.Path, List[pathlib.Path], List[pathlib.Path]]]:
        """Walk a directory tree.
        
        Similar to os.walk, but returns Path objects instead of strings.
        
        Args:
            top: Directory to start walking from
            
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
            yield (
                dir_path,
                [dir_path / d for d in dirnames],
                [dir_path / f for f in filenames]
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
