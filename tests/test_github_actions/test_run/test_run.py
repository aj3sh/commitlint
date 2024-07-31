# type: ignore
# pylint: disable=all
"""
Integration test of `run.py` to ensure Github Action full functionality.
"""

import json
import os
import subprocess
from unittest.mock import call, mock_open, patch

import pytest

from github_actions.action.run import run_action


def set_github_env_vars():
    # GitHub Action event env
    os.environ["GITHUB_EVENT_NAME"] = "push"
    os.environ["GITHUB_SHA"] = "commitlint_sha"
    os.environ["GITHUB_REF"] = "refs/heads/main"
    os.environ["GITHUB_WORKFLOW"] = "commitlint_ci"
    os.environ["GITHUB_ACTION"] = "action"
    os.environ["GITHUB_ACTOR"] = "actor"
    os.environ["GITHUB_REPOSITORY"] = "opensource-nepal/commitlint"
    os.environ["GITHUB_JOB"] = "job"
    os.environ["GITHUB_RUN_ATTEMPT"] = "9"
    os.environ["GITHUB_RUN_NUMBER"] = "8"
    os.environ["GITHUB_RUN_ID"] = "7"
    os.environ["GITHUB_EVENT_PATH"] = "/tmp/github_event.json"
    os.environ["GITHUB_STEP_SUMMARY"] = "/tmp/github_step_summary"
    os.environ["GITHUB_OUTPUT"] = "/tmp/github_output"

    # GitHub Action input env
    os.environ["INPUT_TOKEN"] = "token"
    os.environ["INPUT_VERBOSE"] = "false"
    os.environ["INPUT_FAIL_ON_ERROR"] = "true"


@pytest.fixture(autouse=True)
def setup_env():
    set_github_env_vars()


@patch("subprocess.check_output", return_value="success")
@patch.dict(os.environ, {**os.environ, "GITHUB_EVENT_NAME": "push"})
def test__run_action__push_event_full_integration_test_for_valid_commits(
    mock_check_output,
):
    payload = {
        "commits": [
            {"message": "feat: valid message"},
            {"message": "fix(login): fix login message"},
        ]
    }
    with patch("builtins.open", mock_open(read_data=json.dumps(payload))):
        run_action()

    assert mock_check_output.call_count == 2
    expected_calls = [
        call(
            ["commitlint", "feat: valid message", "--hide-input"],
            text=True,
            stderr=subprocess.PIPE,
        ),
        call(
            ["commitlint", "fix(login): fix login message", "--hide-input"],
            text=True,
            stderr=subprocess.PIPE,
        ),
    ]
    mock_check_output.assert_has_calls(expected_calls, any_order=False)


@patch("subprocess.check_output", return_value="success")
@patch.dict(os.environ, {**os.environ, "GITHUB_EVENT_NAME": "push"})
def test__run_action__push_event_full_integration_test_for_invalid_commits(
    mock_check_output,
):
    # mock for commitlint command to return error
    mock_check_output.side_effect = subprocess.CalledProcessError(
        1, ["cmd"], "stdout", "stderr"
    )

    payload = {
        "commits": [
            {"message": "feat: valid message"},
            {"message": "invalid commit message"},
        ]
    }
    with patch("builtins.open", mock_open(read_data=json.dumps(payload))):
        with pytest.raises(SystemExit):
            run_action()

    assert mock_check_output.call_count == 2
    expected_calls = [
        call(
            ["commitlint", "feat: valid message", "--hide-input"],
            text=True,
            stderr=subprocess.PIPE,
        ),
        call(
            ["commitlint", "invalid commit message", "--hide-input"],
            text=True,
            stderr=subprocess.PIPE,
        ),
    ]
    mock_check_output.assert_has_calls(expected_calls, any_order=False)


@patch("github_actions.action.run.request_github_api")
@patch("subprocess.check_output", return_value="success")
@patch.dict(os.environ, {**os.environ, "GITHUB_EVENT_NAME": "pull_request"})
def test__run_action__pr_event_full_integration_test_for_valid_commits(
    mock_check_output,
    mock_request_github_api,
):
    # mock github api request
    mock_request_github_api.return_value = (
        200,
        [
            {
                "commit": {"message": "feat: valid message"},
            },
            {
                "commit": {"message": "fix(login): fix login message"},
            },
        ],
    )

    payload = {"number": 10, "pull_request": {"commits": 2}}
    with patch("builtins.open", mock_open(read_data=json.dumps(payload))):
        run_action()

    assert mock_check_output.call_count == 2
    expected_calls = [
        call(
            ["commitlint", "feat: valid message", "--hide-input"],
            text=True,
            stderr=subprocess.PIPE,
        ),
        call(
            ["commitlint", "fix(login): fix login message", "--hide-input"],
            text=True,
            stderr=subprocess.PIPE,
        ),
    ]
    mock_check_output.assert_has_calls(expected_calls, any_order=False)


@patch("github_actions.action.run.request_github_api")
@patch("subprocess.check_output", return_value="success")
@patch.dict(os.environ, {**os.environ, "GITHUB_EVENT_NAME": "pull_request"})
def test__run_action__pr_event_full_integration_test_for_invalid_commits(
    mock_check_output,
    mock_request_github_api,
):
    # mock for commitlint command to return error
    mock_check_output.side_effect = subprocess.CalledProcessError(
        1, ["cmd"], "stdout", "stderr"
    )

    # mock github api request
    mock_request_github_api.return_value = (
        200,
        [
            {
                "commit": {"message": "feat: valid message"},
            },
            {
                "commit": {"message": "invalid commit message"},
            },
        ],
    )

    payload = {"number": 10, "pull_request": {"commits": 2}}
    with patch("builtins.open", mock_open(read_data=json.dumps(payload))):
        with pytest.raises(SystemExit):
            run_action()

    assert mock_check_output.call_count == 2
    expected_calls = [
        call(
            ["commitlint", "feat: valid message", "--hide-input"],
            text=True,
            stderr=subprocess.PIPE,
        ),
        call(
            ["commitlint", "invalid commit message", "--hide-input"],
            text=True,
            stderr=subprocess.PIPE,
        ),
    ]
    mock_check_output.assert_has_calls(expected_calls, any_order=False)
