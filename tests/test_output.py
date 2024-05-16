# type: ignore
# pylint: disable=all

from unittest.mock import MagicMock, patch

from commitlint.output import error, success, verbose


@patch("commitlint.output.config", quiet=False)
@patch("sys.stdout")
def test_success(mock_stdout: MagicMock, _mock_config: MagicMock):
    message = "Success message"
    success(message)
    mock_stdout.write.assert_called_once_with(f"{message}\n")


@patch("commitlint.output.config", quiet=True)
@patch("sys.stdout")
def test_success_for_quiet(mock_stdout: MagicMock, _mock_config: MagicMock):
    message = "Success message"
    success(message)
    mock_stdout.write.assert_not_called()


@patch("commitlint.output.config", quiet=False)
@patch("sys.stderr")
def test_error(mock_stderr: MagicMock, _mock_config: MagicMock):
    message = "Error message"
    error(message)
    mock_stderr.write.assert_called_once_with(f"{message}\n")


@patch("commitlint.output.config", quiet=True)
@patch("sys.stderr")
def test_error_for_quiet(mock_stderr: MagicMock, _mock_config: MagicMock):
    message = "Error message"
    error(message)
    mock_stderr.write.assert_not_called()


@patch("commitlint.output.config", verbose=True)
@patch("sys.stdout")
def test_verbose(mock_stdout: MagicMock, _mock_config: MagicMock):
    message = "Verbose message"
    verbose(message)
    mock_stdout.write.assert_called_once_with(f"{message}\n")


@patch("commitlint.output.config", verbose=False)
@patch("sys.stdout")
def test_verbose_for_non_verbose(mock_stdout: MagicMock, _mock_config: MagicMock):
    message = "Verbose message"
    verbose(message)
    mock_stdout.write.assert_not_called()
