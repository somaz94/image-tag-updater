"""Tests for src/logger.py"""
import pytest

from src.logger import ActionError, Logger


class TestLogger:
    def test_print_header(self, capsys):
        logger = Logger()
        logger.print_header("Test Header")
        out = capsys.readouterr().out
        assert "Test Header" in out
        assert "=" in out

    def test_debug_enabled(self, capsys):
        logger = Logger(debug=True)
        logger.debug("debug message")
        assert "debug message" in capsys.readouterr().out

    def test_debug_disabled(self, capsys):
        logger = Logger(debug=False)
        logger.debug("debug message")
        assert capsys.readouterr().out == ""

    def test_info(self, capsys):
        logger = Logger()
        logger.info("info message")
        assert "info message" in capsys.readouterr().out

    def test_success(self, capsys):
        logger = Logger()
        logger.success("done")
        out = capsys.readouterr().out
        assert "[O]" in out
        assert "done" in out

    def test_warning(self, capsys):
        logger = Logger()
        logger.warning("caution")
        out = capsys.readouterr().out
        assert "[!]" in out
        assert "caution" in out

    def test_error(self, capsys):
        logger = Logger()
        with pytest.raises(ActionError, match="fatal"):
            logger.error("fatal")
        err = capsys.readouterr().err
        assert "[X]" in err
        assert "fatal" in err

    def test_action_error_is_runtime_error(self):
        assert issubclass(ActionError, RuntimeError)
