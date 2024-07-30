# type: ignore
# pylint: disable=all
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
    os.environ["INPUT_VERBOSE"] = "false"
    os.environ["INPUT_FAIL_ON_ERROR"] = "true"


@pytest.fixture(autouse=True)
def setup_env():
    set_github_env_vars()


# integration test of run_action to ensure Github Action full functionality.


@patch("subprocess.check_output", return_value="success")
@patch.dict(os.environ, {**os.environ, "GITHUB_EVENT_NAME": "push"})
def test__run_action__push_event_full_integration_test_for_all_valid_commits(
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


# @patch.dict(os.environ, {**os.environ, "GITHUB_EVENT_NAME": "push"})
# def test__run_action__push_event_full_integration_test_for_partially_invalid_commits():
#     payload = {
#         "commits": [
#             {"message": "feat: valid message"},
#             {"message": "fix login message"},
#         ]
#     }
#     with patch("builtins.open", mock_open(read_data=json.dumps(payload))):
#         with pytest.raises(SystemExit):
#             run_action()


# @patch.dict(os.environ, {**os.environ, "GITHUB_EVENT_NAME": "push"})
# def test__run_action__push_event_full_integration_test_for_all_invalid_commits():
#     payload = {
#         "commits": [
#             {"message": "invalid message"},
#             {"message": "fix login message"},
#         ]
#     }
#     with patch("builtins.open", mock_open(read_data=json.dumps(payload))):
#         with pytest.raises(SystemExit):
#             run_action()


# @patch.dict(os.environ, {**os.environ, "GITHUB_EVENT_NAME": "pull_request"})
# def test__run_action__pr_event_full_integration_test_for_all_valid_commits():
#     payload = {
#         "commits": [
#             {"message": "feat: valid message"},
#             {"message": "fix(login): fix login message"},
#         ]
#     }
#     with patch("builtins.open", mock_open(read_data=json.dumps(payload))):
#         run_action()
