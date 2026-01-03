"""Test suite for io module (file I/O operations)."""

import datetime
import json
import pickle

import pytest

from fsutils import DirManager, io


class TestIoModule:
    """Test cases for the io module functions (file I/O operations)."""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create a temporary directory for testing."""
        return tmp_path

    def test_exists_file(self, temp_dir):
        """Test checking if a file exists."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("hello")

        assert io.exists(str(test_file)) is True
        assert io.exists(str(temp_dir / "nonexistent.txt")) is False

    def test_exists_directory(self, temp_dir):
        """Test checking if a directory exists."""
        subdir = temp_dir / "subdir"
        subdir.mkdir()

        assert io.exists(str(subdir)) is True
        assert io.exists(str(temp_dir / "nonexistent")) is False

    def test_is_file(self, temp_dir):
        """Test checking if path is a file."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("hello")
        (temp_dir / "subdir").mkdir()

        assert io.is_file(str(test_file)) is True
        assert io.is_file(str(temp_dir / "subdir")) is False
        assert io.is_file(str(temp_dir / "nonexistent.txt")) is False

    def test_is_dir(self, temp_dir):
        """Test checking if path is a directory."""
        (temp_dir / "subdir").mkdir()
        test_file = temp_dir / "test.txt"
        test_file.write_text("hello")

        assert io.is_dir(str(temp_dir / "subdir")) is True
        assert io.is_dir(str(test_file)) is False
        assert io.is_dir(str(temp_dir / "nonexistent")) is False

    def test_read_text(self, temp_dir):
        """Test reading text from a file."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Hello, World!")

        content = io.read_text(str(test_file))
        assert content == "Hello, World!"

    def test_read_text_with_encoding(self, temp_dir):
        """Test reading text with specific encoding."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Hello", encoding="utf-16")

        content = io.read_text(str(test_file), encoding="utf-16")
        assert content == "Hello"

    def test_write_text(self, temp_dir):
        """Test writing text to a file."""
        output_file = temp_dir / "output.txt"
        chars_written = io.write_text(str(output_file), "Hello, World!")
        assert chars_written == len("Hello, World!")

    def test_read_bytes(self, temp_dir):
        """Test reading binary data."""
        test_file = temp_dir / "test.bin"
        test_file.write_bytes(b"\x00\x01\x02\x03")

        data = io.read_bytes(str(test_file))
        assert data == b"\x00\x01\x02\x03"

    def test_write_bytes(self, temp_dir):
        """Test writing binary data."""
        output_file = temp_dir / "output.bin"
        bytes_written = io.write_bytes(str(output_file), b"\x00\x01\x02\x03")
        assert bytes_written == 4

    def test_read_json(self, temp_dir):
        """Test reading JSON files."""
        test_file = temp_dir / "data.json"
        test_file.write_text('{"key": "value", "number": 42}')

        data = io.read_json(str(test_file))
        assert data == {"key": "value", "number": 42}

    def test_write_json(self, temp_dir):
        """Test writing JSON files."""
        output_file = temp_dir / "data.json"
        data = {"key": "value", "list": [1, 2, 3]}
        io.write_json(str(output_file), data)

        with open(output_file) as f:
            loaded = json.load(f)
        assert loaded == data

    def test_read_pickle(self, temp_dir):
        """Test reading pickle files."""
        test_data = {"key": "value", "list": [1, 2, 3]}
        test_file = temp_dir / "data.pkl"
        pickle.dump(test_data, open(test_file, "wb"))

        loaded = io.read_pickle(str(test_file))
        assert loaded == test_data

    def test_write_pickle(self, temp_dir):
        """Test writing pickle files."""
        output_file = temp_dir / "data.pkl"
        test_data = {"key": "value"}
        io.write_pickle(str(output_file), test_data)

        loaded = pickle.load(open(output_file, "rb"))
        assert loaded == test_data

    def test_delete_file(self, temp_dir):
        """Test deleting a file."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        io.delete_file(str(test_file))
        assert not test_file.exists()

    def test_get_file_size(self, temp_dir):
        """Test getting file size."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Hello")

        size = io.get_file_size(str(test_file))
        assert size == 5

    def test_get_modified_time(self, temp_dir):
        """Test getting modified time."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        mtime = io.get_modified_time(str(test_file))
        assert isinstance(mtime, datetime.datetime)

    def test_get_file_hash_md5(self, temp_dir):
        """Test getting MD5 file hash."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        hash_value = io.get_file_hash(str(test_file), algorithm="md5")
        assert len(hash_value) == 32  # MD5 produces 32 hex chars
        assert all(c in "0123456789abcdef" for c in hash_value)

    def test_get_file_hash_sha256(self, temp_dir):
        """Test getting SHA-256 file hash."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")

        hash_value = io.get_file_hash(str(test_file), algorithm="sha256")
        assert len(hash_value) == 64  # SHA-256 produces 64 hex chars

    def test_image_extensions(self):
        """Test image extensions constant."""
        exts = io.image_extensions()
        assert ".jpg" in exts
        assert ".png" in exts
        assert ".gif" in exts

    def test_video_extensions(self):
        """Test video extensions constant."""
        exts = io.video_extensions()
        assert ".mp4" in exts
        assert ".avi" in exts

    def test_audio_extensions(self):
        """Test audio extensions constant."""
        exts = io.audio_extensions()
        assert ".mp3" in exts
        assert ".wav" in exts

    def test_document_extensions(self):
        """Test document extensions constant."""
        exts = io.document_extensions()
        assert ".pdf" in exts
        assert ".docx" in exts


class TestErrorHandling:
    """Test error handling in io module and DirManager."""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create a temporary directory for testing."""
        return tmp_path

    def test_read_nonexistent_file(self, temp_dir):
        """Test reading a non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            io.read_text(str(temp_dir / "nonexistent.txt"))

    def test_read_directory_as_file(self, temp_dir):
        """Test reading a directory as a file raises IsADirectoryError."""
        (temp_dir / "subdir").mkdir()

        with pytest.raises(IsADirectoryError):
            io.read_text(str(temp_dir / "subdir"))

    def test_delete_nonexistent_file(self, temp_dir):
        """Test deleting a non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            io.delete_file(str(temp_dir / "nonexistent.txt"))

    def test_delete_file_as_directory(self, temp_dir):
        """Test trying to delete a file as a directory raises NotADirectoryError."""
        dm = DirManager(str(temp_dir))
        (temp_dir / "file.txt").write_text("content")

        with pytest.raises(NotADirectoryError):
            dm.delete_dir("file.txt")

    def test_list_nonexistent_directory(self, temp_dir):
        """Test listing a non-existent directory raises NotADirectoryError via scan."""
        dm = DirManager(str(temp_dir))

        with pytest.raises(NotADirectoryError):
            dm.scan("nonexistent")

    def test_invalid_hash_algorithm(self, temp_dir):
        """Test using an invalid hash algorithm raises ValueError."""
        (temp_dir / "file.txt").write_text("content")

        with pytest.raises(ValueError, match="Unsupported hash algorithm"):
            io.get_file_hash(str(temp_dir / "file.txt"), algorithm="invalid")
