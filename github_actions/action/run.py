"""
This module runs the actions based on GitHub events, specifically for push,
pull_request and pull_request_target events.
"""

import http.client
import json
import os
import subprocess
import sys
from typing import Iterable, Optional

from .event import GitHubEvent
from .utils import get_boolean_input, get_input, write_line_to_file, write_output

# Events
EVENT_PUSH = "push"
EVENT_PULL_REQUEST = "pull_request"
EVENT_PULL_REQUEST_TARGET = "pull_request_target"

# Inputs
INPUT_TOKEN = "token"
INPUT_FAIL_ON_ERROR = "fail_on_error"
INPUT_VERBOSE = "verbose"

# Status
STATUS_SUCCESS = "success"
STATUS_FAILURE = "failure"


def get_push_commit_messages(event: GitHubEvent) -> Iterable[str]:
    """
    Return push commits.

    Args:
        event (GitHubEvent): An instance of the GitHubEvent class representing
            the GitHub event.

    Returns:
        List[str]: List of github commits.
    """
    return (commit_data["message"] for commit_data in event.payload["commits"])


def get_pr_commit_messages(event: GitHubEvent) -> Iterable[str]:
    """
    Return PR commits.

    Args:
        event (GitHubEvent): An instance of the GitHubEvent class representing
            the GitHub event.

    Returns:
        List[str]: List of github commits.
    """
    token = get_input(INPUT_TOKEN)
    repo = event.repository
    pr_number = event.payload["number"]

    try:
        sys.stdout.write("::debug::Fetching commits using GitHub API.\n")
        conn = http.client.HTTPSConnection(host="api.github.com")
        conn.request(
            method="GET",
            url=f"/repos/{repo}/pulls/{pr_number}/commits",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": "commitlint",
            },
        )
        res = conn.getresponse()
        json_data = res.read().decode("utf-8")

        if res.status != 200:
            sys.stdout.write(f"::debug:: {json_data}\n")
            sys.exit(f"::error::Github API failed with status code {res.status}")

        data = json.loads(json_data)
        return (commit_data["commit"]["message"] for commit_data in data)
    except http.client.HTTPException as ex:
        sys.stdout.write(f"::debug::{ex}\n")
        sys.exit("::error::Failed to retrieve data from using Github API")
    except json.JSONDecodeError as ex:
        sys.stdout.write(f"::debug::{ex}\n")
        sys.exit("::error::Unable to parse json from GitHub API response")


def run_commitlint(commit_message: str) -> Optional[str]:
    """
    Run the commitlint for the given commit message.

    Args:
        commit_message (str): A commit message to check with commitlint.

    Returns:
        Optional[str]: Error message. If no error returns None.
    """

    try:
        commands = ["commitlint", commit_message, "--hide-input"]

        verbose = get_boolean_input(INPUT_VERBOSE)
        if verbose:
            commands.append("--verbose")

        output = subprocess.check_output(commands, text=True, stderr=subprocess.PIPE)
        if output:
            sys.stdout.write(f"{output}")

        return None
    except subprocess.CalledProcessError as error:
        if error.stdout:
            sys.stdout.write(f"{error.stdout}")

        return str(error.stderr)


def check_commit_messages(commit_messages: Iterable[str]) -> None:
    """
    Check the commit messages and create outputs for GitHub Actions.

    Args:
        commit_messages (Iterable[str]): List of commit messages to check.

    Raises:
        SystemExit: If any of the commit messages is invalid.
    """
    has_error = False
    failed_commits = 0

    for commit_message in commit_messages:
        commit_message_header = commit_message.split("\n")[0]
        sys.stdout.write(f"\n⧗ {commit_message_header}\n")

        error = run_commitlint(commit_message)
        if not error:
            continue

        error = error.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        sys.stdout.write(f"::error title={commit_message_header}::{error}")
        has_error = True
        failed_commits += 1

    # GitHub step summary path
    github_step_summary = os.environ["GITHUB_STEP_SUMMARY"]

    if not has_error:
        # success
        write_line_to_file(github_step_summary, "commitlint: All commits passed!")
        write_output("status", STATUS_SUCCESS)
        write_output("exit_code", 0)
        return

    # failure
    write_line_to_file(
        github_step_summary, f"commitlint: {failed_commits} commit(s) failed!"
    )
    write_output("status", STATUS_FAILURE)
    write_output("exit_code", 1)
    fail_on_error = get_boolean_input(INPUT_FAIL_ON_ERROR)
    if fail_on_error:
        sys.exit(1)


def _handle_pr_event(event: GitHubEvent) -> None:
    """
    Handle pull_request GitHub event.

    Args:
        event (GitHubEvent): An instance of the GitHubEvent class representing
            the GitHub event.
    """
    commit_messages = get_pr_commit_messages(event)
    check_commit_messages(commit_messages)


def _handle_push_event(event: GitHubEvent) -> None:
    """
    Handle push GitHub event.

    Args:
        event (GitHubEvent): An instance of the GitHubEvent class representing
            the GitHub event.
    """
    commit_messages = get_push_commit_messages(event)
    check_commit_messages(commit_messages)


def run_action() -> None:
    """Run commitlint action"""
    event = GitHubEvent()

    if event.event_name == EVENT_PUSH:
        _handle_push_event(event)
    elif event.event_name in (EVENT_PULL_REQUEST, EVENT_PULL_REQUEST_TARGET):
        _handle_pr_event(event)
    elif event.event_name is None:
        sys.stdout.write("No any events, skipping\n")
    else:
        sys.stdout.write(f"Skipping for event {event.event_name}\n")
