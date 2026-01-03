"""Test suite for dirs module (directory operations)."""

import pytest

from fsutils import dirs


class TestMkdirFunction:
    """Test cases for the mkdir() function."""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create a temporary directory for testing."""
        return tmp_path

    def test_mkdir_creates_directory(self, temp_dir):
        """Test that mkdir() creates a directory that doesn't exist."""
        new_dir = temp_dir / "new_directory"

        dirs.mkdir(str(new_dir))

        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_mkdir_skips_existing(self, temp_dir):
        """Test that mkdir() doesn't fail when directory already exists."""
        existing_dir = temp_dir / "existing_directory"
        existing_dir.mkdir()

        # Should not raise an exception
        dirs.mkdir(str(existing_dir))

        assert existing_dir.exists()

    def test_mkdir_creates_nested_directory(self, temp_dir):
        """Test that mkdir() creates nested directories."""
        nested_dir = temp_dir / "parent" / "child"

        dirs.mkdir(str(nested_dir))

        assert nested_dir.exists()
        assert nested_dir.is_dir()


class TestMkdirsFunction:
    """Test cases for the mkdirs() function."""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create a temporary directory for testing."""
        return tmp_path

    def test_mkdirs_creates_multiple_directories(self, temp_dir):
        """Test that mkdirs() creates multiple directories."""
        dir1 = temp_dir / "dir1"
        dir2 = temp_dir / "dir2"
        dir3 = temp_dir / "dir3"

        dirs.mkdirs([str(dir1), str(dir2), str(dir3)])

        assert dir1.exists()
        assert dir2.exists()
        assert dir3.exists()

    def test_mkdirs_creates_nested_directories(self, temp_dir):
        """Test that mkdirs() creates nested directory paths."""
        nested1 = temp_dir / "a" / "b" / "c"
        nested2 = temp_dir / "x" / "y"

        dirs.mkdirs([str(nested1), str(nested2)])

        assert nested1.exists()
        assert nested2.exists()

    def test_mkdirs_handles_partial_existing(self, temp_dir):
        """Test that mkdirs() handles mix of existing and new directories."""
        existing = temp_dir / "existing"
        existing.mkdir()
        new_dir = temp_dir / "new"

        # Should not raise an exception
        dirs.mkdirs([str(existing), str(new_dir)])

        assert existing.exists()
        assert new_dir.exists()


class TestNewmkdirFunction:
    """Test cases for the newmkdir() function."""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create a temporary directory for testing."""
        return tmp_path

    def test_newmkdir_creates_new_directory(self, temp_dir):
        """Test that newmkdir() creates directory when it doesn't exist."""
        new_dir = temp_dir / "brand_new"

        dirs.newmkdir(str(new_dir))

        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_newmkdir_removes_existing_directory(self, temp_dir):
        """Test that newmkdir() removes existing directory and creates fresh one."""
        existing_dir = temp_dir / "to_replace"
        existing_dir.mkdir()
        (existing_dir / "file.txt").write_text("content")

        dirs.newmkdir(str(existing_dir))

        # Directory should still exist
        assert existing_dir.exists()
        # But the file should be gone (fresh directory)
        assert not (existing_dir / "file.txt").exists()

    def test_newmkdir_removes_directory_with_subdirs(self, temp_dir):
        """Test that newmkdir() removes directory with nested contents."""
        parent_dir = temp_dir / "parent"
        child_dir = parent_dir / "child"
        child_dir.mkdir(parents=True)
        (child_dir / "nested.txt").write_text("nested content")

        dirs.newmkdir(str(parent_dir))

        assert parent_dir.exists()
        assert not (parent_dir / "child").exists()


