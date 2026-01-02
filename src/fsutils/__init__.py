"""
fsutils - File system utilities for Python.

This package provides file system utilities for working with files
and directories.

For detailed usage documentation, see:
- USAGE_DirManager.md - DirManager class documentation
- src/fsutils/io.py - io module documentation

Quick Example:
    >>> from fsutils import DirManager, io
    >>> 
    >>> # Directory operations with DirManager
    >>> dm = DirManager("/path/to/project")
    >>> dm.list_files(extensions=['.py'])
    >>> dm.create_dir("output")
    >>> 
    >>> # Simple file I/O with io module
    >>> data = io.read_json("config.json")
    >>> io.write_json("output.json", data)
"""

__version__ = "0.1.0"

# Import the DirManager class from paths (the canonical implementation)
from fsutils.paths import DirManager

# Keep FileSystem as an alias for backward compatibility
FileSystem = DirManager

# Import the io module for standalone file operations
from fsutils import io

# Re-export key functions from io for convenience
from fsutils.io import (
    read_json,
    write_json,
    read_text,
    write_text,
    read_bytes,
    write_bytes,
    read_pickle,
    write_pickle,
    exists,
    is_file,
    is_dir,
    delete_file,
    get_file_size,
    get_modified_time,
    get_file_hash,
    image_extensions,
    video_extensions,
    audio_extensions,
    document_extensions,
    IMAGE_EXTENSIONS,
    VIDEO_EXTENSIONS,
    AUDIO_EXTENSIONS,
    DOCUMENT_EXTENSIONS,
)

__all__ = [
    "DirManager",
    "FileSystem",  # Backward compatibility alias
    "paths",
    "io",
    # Re-exported io functions for convenience
    "read_json",
    "write_json",
    "read_text",
    "write_text",
    "read_bytes",
    "write_bytes",
    "read_pickle",
    "write_pickle",
    "exists",
    "is_file",
    "is_dir",
    "delete_file",
    "get_file_size",
    "get_modified_time",
    "get_file_hash",
    "image_extensions",
    "video_extensions",
    "audio_extensions",
    "document_extensions",
    "IMAGE_EXTENSIONS",
    "VIDEO_EXTENSIONS",
    "AUDIO_EXTENSIONS",
    "DOCUMENT_EXTENSIONS",
]
