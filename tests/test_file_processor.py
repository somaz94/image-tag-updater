"""Tests for src/file_processor.py"""
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from src.config import Config
from src.file_processor import FileProcessor
from src.logger import Logger


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def base_kwargs():
    return {
        "target_path": "/tmp",
        "new_tag": "v2.0.0",
        "tag_string": "tag",
        "git_user_name": "test",
        "git_user_email": "test@test.com",
        "github_token": "token",
        "repo": "test/repo",
        "branch": "main",
        "target_values_file": "values.yaml",
    }


@pytest.fixture
def logger():
    return Logger(debug=False)


def _write(directory, filename, content):
    path = os.path.join(directory, filename)
    with open(path, "w") as f:
        f.write(content)
    return path


YAML_CONTENT = 'image:\n  tag: "v1.0.0"\n  pullPolicy: Always\n'


# ---------------------------------------------------------------------------
# validate_file_content
# ---------------------------------------------------------------------------

class TestValidateFileContent:
    def test_tag_found(self, base_kwargs, logger, tmp_path):
        fp = _write(str(tmp_path), "v.yaml", YAML_CONTENT)
        proc = FileProcessor(Config(**base_kwargs), logger)
        proc.validate_file_content(fp)  # should not raise/exit

    def test_tag_not_found(self, base_kwargs, logger, tmp_path):
        fp = _write(str(tmp_path), "v.yaml", "nothing: here\n")
        proc = FileProcessor(Config(**base_kwargs), logger)
        with pytest.raises(SystemExit):
            proc.validate_file_content(fp)

    def test_file_missing(self, base_kwargs, logger):
        proc = FileProcessor(Config(**base_kwargs), logger)
        with pytest.raises(SystemExit):
            proc.validate_file_content("/nonexistent/file.yaml")

    def test_read_error(self, base_kwargs, logger, tmp_path):
        fp = _write(str(tmp_path), "v.yaml", YAML_CONTENT)
        proc = FileProcessor(Config(**base_kwargs), logger)
        with patch("builtins.open", side_effect=PermissionError("denied")):
            with pytest.raises(SystemExit):
                proc.validate_file_content(fp)


# ---------------------------------------------------------------------------
# get_current_tag
# ---------------------------------------------------------------------------

class TestGetCurrentTag:
    def test_match(self, base_kwargs, logger, tmp_path):
        fp = _write(str(tmp_path), "v.yaml", YAML_CONTENT)
        proc = FileProcessor(Config(**base_kwargs), logger)
        assert proc.get_current_tag(fp) == "v1.0.0"

    def test_no_match(self, base_kwargs, logger, tmp_path):
        fp = _write(str(tmp_path), "v.yaml", "nothing: here\n")
        proc = FileProcessor(Config(**base_kwargs), logger)
        assert proc.get_current_tag(fp) == ""

    def test_quoted(self, base_kwargs, logger, tmp_path):
        fp = _write(str(tmp_path), "v.yaml", '  tag: "v3.0.0"\n')
        proc = FileProcessor(Config(**base_kwargs), logger)
        assert proc.get_current_tag(fp) == "v3.0.0"

    def test_read_error(self, base_kwargs, logger, tmp_path):
        proc = FileProcessor(Config(**base_kwargs), logger)
        with patch("builtins.open", side_effect=IOError("fail")):
            with pytest.raises(SystemExit):
                proc.get_current_tag("/tmp/fake.yaml")


# ---------------------------------------------------------------------------
# should_skip_update
# ---------------------------------------------------------------------------

class TestShouldSkipUpdate:
    def _proc(self, base_kwargs, logger, **overrides):
        kw = {**base_kwargs, **overrides}
        return FileProcessor(Config(**kw), logger)

    def test_update_if_contains_skip(self, base_kwargs, logger):
        proc = self._proc(base_kwargs, logger, update_if_contains="v1.")
        skip, reason = proc.should_skip_update("f", "v2.0.0", "v3.0.0")
        assert skip is True
        assert "does not contain" in reason

    def test_update_if_contains_pass(self, base_kwargs, logger):
        proc = self._proc(base_kwargs, logger, update_if_contains="v1.")
        skip, _ = proc.should_skip_update("f", "v1.0.0", "v2.0.0")
        assert skip is False

    def test_skip_if_contains_skip(self, base_kwargs, logger):
        proc = self._proc(base_kwargs, logger, skip_if_contains="latest")
        skip, reason = proc.should_skip_update("f", "latest", "v2.0.0")
        assert skip is True
        assert "contains" in reason

    def test_skip_if_contains_pass(self, base_kwargs, logger):
        proc = self._proc(base_kwargs, logger, skip_if_contains="latest")
        skip, _ = proc.should_skip_update("f", "v1.0.0", "v2.0.0")
        assert skip is False

    def test_same_tag(self, base_kwargs, logger):
        proc = FileProcessor(Config(**base_kwargs), logger)
        skip, reason = proc.should_skip_update("f", "v2.0.0", "v2.0.0")
        assert skip is True
        assert "already set" in reason

    def test_different_tag(self, base_kwargs, logger):
        proc = FileProcessor(Config(**base_kwargs), logger)
        skip, reason = proc.should_skip_update("f", "v1.0.0", "v2.0.0")
        assert skip is False
        assert reason is None


# ---------------------------------------------------------------------------
# _perform_update
# ---------------------------------------------------------------------------

class TestPerformUpdate:
    def test_success(self, base_kwargs, logger, tmp_path):
        fp = _write(str(tmp_path), "v.yaml", YAML_CONTENT)
        proc = FileProcessor(Config(**base_kwargs), logger)
        assert proc._perform_update(fp, "v2.0.0") is True
        with open(fp) as f:
            assert "v2.0.0" in f.read()

    def test_write_error(self, base_kwargs, logger, tmp_path):
        fp = _write(str(tmp_path), "v.yaml", YAML_CONTENT)
        proc = FileProcessor(Config(**base_kwargs), logger)
        # Patch open so reading succeeds but writing fails
        original_open = open
        call_count = 0

        def side_effect_open(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:  # second open is the write
                raise PermissionError("read-only")
            return original_open(*args, **kwargs)

        # logger.error calls sys.exit(1), so return False is unreachable
        with patch("builtins.open", side_effect=side_effect_open):
            with pytest.raises(SystemExit):
                proc._perform_update(fp, "v2.0.0")


# ---------------------------------------------------------------------------
# update_file
# ---------------------------------------------------------------------------

class TestUpdateFile:
    def test_dry_run(self, base_kwargs, logger, tmp_path):
        kw = {**base_kwargs, "dry_run": True}
        fp = _write(str(tmp_path), "v.yaml", YAML_CONTENT)
        proc = FileProcessor(Config(**kw), logger)
        assert proc.update_file(fp) is True
        assert fp in proc.updated_files
        # File content should NOT change in dry run
        with open(fp) as f:
            assert "v1.0.0" in f.read()

    def test_actual_update(self, base_kwargs, logger, tmp_path):
        fp = _write(str(tmp_path), "v.yaml", YAML_CONTENT)
        proc = FileProcessor(Config(**base_kwargs), logger)
        assert proc.update_file(fp) is True
        with open(fp) as f:
            assert "v2.0.0" in f.read()

    def test_skip_same_tag(self, base_kwargs, logger, tmp_path):
        kw = {**base_kwargs, "new_tag": "v1.0.0"}
        fp = _write(str(tmp_path), "v.yaml", YAML_CONTENT)
        proc = FileProcessor(Config(**kw), logger)
        assert proc.update_file(fp) is False

    def test_backup_created(self, base_kwargs, logger, tmp_path):
        kw = {**base_kwargs, "backup": True}
        fp = _write(str(tmp_path), "v.yaml", YAML_CONTENT)
        proc = FileProcessor(Config(**kw), logger)
        proc.update_file(fp)
        assert os.path.exists(f"{fp}.bak")

    def test_backup_failure(self, base_kwargs, logger, tmp_path):
        kw = {**base_kwargs, "backup": True}
        fp = _write(str(tmp_path), "v.yaml", YAML_CONTENT)
        proc = FileProcessor(Config(**kw), logger)
        with patch("shutil.copy2", side_effect=OSError("disk full")):
            with pytest.raises(SystemExit):
                proc.update_file(fp)


# ---------------------------------------------------------------------------
# get_files_to_process
# ---------------------------------------------------------------------------

class TestGetFilesToProcess:
    def test_single_file(self, base_kwargs, logger, tmp_path):
        fp = _write(str(tmp_path), "values.yaml", YAML_CONTENT)
        kw = {**base_kwargs, "target_values_file": fp}
        proc = FileProcessor(Config(**kw), logger)
        files = proc.get_files_to_process()
        assert files == [fp]

    def test_glob_pattern(self, base_kwargs, logger, tmp_path):
        _write(str(tmp_path), "dev1.values.yaml", YAML_CONTENT)
        _write(str(tmp_path), "dev2.values.yaml", YAML_CONTENT)
        _write(str(tmp_path), "prod.values.yaml", YAML_CONTENT)
        kw = {**base_kwargs, "target_values_file": None, "file_pattern": str(tmp_path / "dev*.values.yaml")}
        proc = FileProcessor(Config(**kw), logger)
        files = proc.get_files_to_process()
        assert len(files) == 2

    def test_no_match(self, base_kwargs, logger, tmp_path):
        kw = {**base_kwargs, "target_values_file": None, "file_pattern": str(tmp_path / "nonexistent*.yaml")}
        proc = FileProcessor(Config(**kw), logger)
        with pytest.raises(SystemExit):
            proc.get_files_to_process()

    def test_file_not_found(self, base_kwargs, logger):
        kw = {**base_kwargs, "target_values_file": "/nonexistent/file.yaml"}
        proc = FileProcessor(Config(**kw), logger)
        with pytest.raises(SystemExit):
            proc.get_files_to_process()


# ---------------------------------------------------------------------------
# process_files
# ---------------------------------------------------------------------------

class TestProcessFiles:
    def test_changes_made(self, base_kwargs, logger, tmp_path):
        fp = _write(str(tmp_path), "values.yaml", YAML_CONTENT)
        kw = {**base_kwargs, "target_values_file": fp, "dry_run": True}
        proc = FileProcessor(Config(**kw), logger)
        assert proc.process_files() is True

    def test_no_changes(self, base_kwargs, logger, tmp_path):
        fp = _write(str(tmp_path), "values.yaml", YAML_CONTENT)
        kw = {**base_kwargs, "new_tag": "v1.0.0", "target_values_file": fp}
        proc = FileProcessor(Config(**kw), logger)
        assert proc.process_files() is False
