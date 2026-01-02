"""
I/O module for standalone file operations.

This module provides functions for file I/O operations.

Example:
    >>> from fsutils import io
    >>> data = io.read_json("config.json")
    >>> io.write_json("output.json", data)
    >>> io.exists("file.txt")
    True
"""

import os
import json
import pickle
import pathlib
import hashlib
import datetime
from typing import Any, Dict, List, Union, BinaryIO, TextIO, Literal

# Type aliases
PathLike = Union[str, os.PathLike]
JsonData = Union[Dict[str, Any], List[Any]]

# File extension constants
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico', '.webp']
VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mpeg', '.mpg', '.m4v', '.mkv']
AUDIO_EXTENSIONS = ['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac', '.wma', '.m4b', '.m4p']
DOCUMENT_EXTENSIONS = ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx']


def _resolve_path(path: PathLike) -> pathlib.Path:
    """Resolve a path to an absolute Path object."""
    p = pathlib.Path(path)
    if p.is_absolute():
        return p
    return p.resolve()


# =============================================================================
# Path Existence and Type Checks
# =============================================================================

def exists(path: PathLike) -> bool:
    """Check if a file or directory exists.
    
    Args:
        path: Path to check
        
    Returns:
        True if the path exists, False otherwise
    """
    return _resolve_path(path).exists()


def is_file(path: PathLike) -> bool:
    """Check if a path is a file.
    
    Args:
        path: Path to check
        
    Returns:
        True if the path is a file, False otherwise
    """
    p = _resolve_path(path)
    return p.exists() and p.is_file()


def is_dir(path: PathLike) -> bool:
    """Check if a path is a directory.
    
    Args:
        path: Path to check
        
    Returns:
        True if the path is a directory, False otherwise
    """
    p = _resolve_path(path)
    return p.exists() and p.is_dir()


# =============================================================================
# Text I/O
# =============================================================================

def read_text(path: PathLike, encoding: str = 'utf-8') -> str:
    """Read text from a file.
    
    Args:
        path: Path to the file
        encoding: Text encoding to use
        
    Returns:
        File contents as a string
        
    Raises:
        FileNotFoundError: If the file does not exist
        IsADirectoryError: If the path is a directory
    """
    p = _resolve_path(path)
    if not p.exists():
        raise FileNotFoundError(f"File does not exist: {p}")
    if p.is_dir():
        raise IsADirectoryError(f"Path is a directory: {p}")
    with p.open("r", encoding=encoding) as f:
        return f.read()


def write_text(path: PathLike, content: str, encoding: str = 'utf-8', 
               create_dirs: bool = True) -> int:
    """Write text to a file.
    
    Args:
        path: Path to the file
        content: Text content to write
        encoding: Text encoding to use
        create_dirs: If True, create parent directories if they don't exist
        
    Returns:
        Number of characters written
        
    Raises:
        FileNotFoundError: If parent directory does not exist and create_dirs is False
    """
    p = _resolve_path(path)
    if create_dirs:
        p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding=encoding) as f:
        return f.write(content)


# =============================================================================
# Binary I/O
# =============================================================================

def read_bytes(path: PathLike) -> bytes:
    """Read binary data from a file.
    
    Args:
        path: Path to the file
        
    Returns:
        File contents as bytes
        
    Raises:
        FileNotFoundError: If the file does not exist
        IsADirectoryError: If the path is a directory
    """
    p = _resolve_path(path)
    if not p.exists():
        raise FileNotFoundError(f"File does not exist: {p}")
    if p.is_dir():
        raise IsADirectoryError(f"Path is a directory: {p}")
    with p.open("rb") as f:
        return f.read()


def write_bytes(path: PathLike, content: bytes, 
                create_dirs: bool = True) -> int:
    """Write binary data to a file.
    
    Args:
        path: Path to the file
        content: Binary content to write
        create_dirs: If True, create parent directories if they don't exist
        
    Returns:
        Number of bytes written
        
    Raises:
        FileNotFoundError: If parent directory does not exist and create_dirs is False
    """
    p = _resolve_path(path)
    if create_dirs:
        p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("wb") as f:
        return f.write(content)


# =============================================================================
# JSON I/O
# =============================================================================

def read_json(path: PathLike, encoding: str = 'utf-8') -> JsonData:
    """Read JSON data from a file.
    
    Args:
        path: Path to the JSON file
        encoding: Text encoding to use
        
    Returns:
        Parsed JSON data
        
    Raises:
        FileNotFoundError: If the file does not exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    p = _resolve_path(path)
    with p.open('r', encoding=encoding) as f:
        return json.load(f)


def write_json(path: PathLike, data: JsonData, encoding: str = 'utf-8',
               indent: int = 2, create_dirs: bool = True) -> None:
    """Write JSON data to a file.
    
    Args:
        path: Path to the JSON file
        data: JSON-serializable data to write
        encoding: Text encoding to use
        indent: Number of spaces for indentation
        create_dirs: If True, create parent directories if they don't exist
    """
    p = _resolve_path(path)
    if create_dirs:
        p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', encoding=encoding) as f:
        json.dump(data, f, indent=indent)


# =============================================================================
# Pickle I/O
# =============================================================================

def read_pickle(path: PathLike) -> Any:
    """Read a Python object from a pickle file.
    
    Args:
        path: Path to the pickle file
        
    Returns:
        Unpickled Python object
        
    Raises:
        FileNotFoundError: If the file does not exist
        pickle.UnpicklingError: If the file contains invalid pickle data
    """
    p = _resolve_path(path)
    with p.open('rb') as f:
        return pickle.load(f)


def write_pickle(path: PathLike, data: Any, create_dirs: bool = True) -> None:
    """Write a Python object to a pickle file.
    
    Args:
        path: Path to the pickle file
        data: Python object to pickle
        create_dirs: If True, create parent directories if they don't exist
    """
    p = _resolve_path(path)
    if create_dirs:
        p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('wb') as f:
        pickle.dump(data, f)


# =============================================================================
# File Operations
# =============================================================================

def delete_file(path: PathLike) -> None:
    """Delete a file.
    
    Args:
        path: Path to the file to delete
        
    Raises:
        FileNotFoundError: If the file does not exist
        IsADirectoryError: If the path is a directory
    """
    p = _resolve_path(path)
    if not p.exists():
        raise FileNotFoundError(f"File does not exist: {p}")
    if not p.is_file():
        raise IsADirectoryError(f"Path is a directory: {p}")
    p.unlink()


# =============================================================================
# File Metadata
# =============================================================================

def get_file_size(path: PathLike) -> int:
    """Get the size of a file in bytes.
    
    Args:
        path: Path to the file
        
    Returns:
        File size in bytes
        
    Raises:
        FileNotFoundError: If the file does not exist
        IsADirectoryError: If the path is a directory
    """
    p = _resolve_path(path)
    if not p.exists():
        raise FileNotFoundError(f"File does not exist: {p}")
    if not p.is_file():
        raise IsADirectoryError(f"Path is a directory: {p}")
    return p.stat().st_size


def get_modified_time(path: PathLike) -> datetime.datetime:
    """Get the last modified time of a file or directory.
    
    Args:
        path: Path to the file or directory
        
    Returns:
        Last modified time as a datetime object
        
    Raises:
        FileNotFoundError: If the path does not exist
    """
    p = _resolve_path(path)
    if not p.exists():
        raise FileNotFoundError(f"Path does not exist: {p}")
    return datetime.datetime.fromtimestamp(p.stat().st_mtime)


def get_file_hash(path: PathLike, algorithm: str = 'md5', 
                  buffer_size: int = 65536) -> str:
    """Calculate the hash of a file.
    
    Args:
        path: Path to the file
        algorithm: Hash algorithm to use ('md5', 'sha1', 'sha256', etc.)
        buffer_size: Size of the buffer for reading the file
        
    Returns:
        Hexadecimal hash string
        
    Raises:
        FileNotFoundError: If the file does not exist
        IsADirectoryError: If the path is a directory
        ValueError: If the algorithm is not supported
    """
    p = _resolve_path(path)
    if not p.exists():
        raise FileNotFoundError(f"File does not exist: {p}")
    if not p.is_file():
        raise IsADirectoryError(f"Path is a directory: {p}")
    
    try:
        hash_obj = hashlib.new(algorithm)
    except ValueError:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    with open(p, 'rb') as f:
        while True:
            data = f.read(buffer_size)
            if not data:
                break
            hash_obj.update(data)
            
    return hash_obj.hexdigest()


# =============================================================================
# Extension Helpers
# =============================================================================

def image_extensions() -> List[str]:
    """Get list of common image file extensions.
    
    Returns:
        List of image file extensions
    """
    return IMAGE_EXTENSIONS.copy()


def video_extensions() -> List[str]:
    """Get list of common video file extensions.
    
    Returns:
        List of video file extensions
    """
    return VIDEO_EXTENSIONS.copy()


def audio_extensions() -> List[str]:
    """Get list of common audio file extensions.
    
    Returns:
        List of audio file extensions
    """
    return AUDIO_EXTENSIONS.copy()


def document_extensions() -> List[str]:
    """Get list of common document file extensions.
    
    Returns:
        List of document file extensions
    """
    return DOCUMENT_EXTENSIONS.copy()
