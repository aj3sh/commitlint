"""Utility functions for GitHub Actions"""

import os
from typing import Optional, Union


def get_input(key: str) -> Optional[str]:
    """
    Read the GitHub action input.

    Args:
        key (str): Input key.

    Returns:
        Optional[str]: The value of the input or None if it is not set.
    """
    key = key.upper()
    return os.environ.get(f"INPUT_{key}")


def get_boolean_input(key: str) -> Optional[bool]:
    """
    Parse the input environment key of boolean type in the YAML 1.2
    "core schema" specification.
    Support boolean input list:
    `true | True | TRUE | false | False | FALSE` .
    ref: https://yaml.org/spec/1.2/spec.html#id2804923

    Args:
        key (str): Input key.

    Returns:
        bool: The parsed boolean value.

    Raises:
        TypeError: If the environment variable's value does not meet the
        YAML 1.2 "core schema" specification for booleans.
    """
    val = get_input(key)

    if not val:
        return None

    if val in {"true", "True", "TRUE"}:
        return True
    if val in {"false", "False", "FALSE"}:
        return False

    raise TypeError(
        """
        Input does not meet YAML 1.2 "Core Schema" specification.\n'
        Support boolean input list:
        `true | True | TRUE | false | False | FALSE
        """
    )


def write_line_to_file(filepath: str, data: str) -> None:
    """
    Write data to a specified filepath.

    Args:
        filepath (str): The path of the file.
        data (str): Data to be saved in the file.
    """
    with open(file=filepath, mode="a", encoding="utf-8") as output_file:
        output_file.write(f"{data}\n")


def write_output(name: str, value: Union[str, int]) -> None:
    """
    Write an output to the GitHub Actions environment.

    Args:
        name (str): The name of the output variable.
        value (Union[str, int]): The value to be assigned to the output variable.
    """
    output_filepath = os.environ["GITHUB_OUTPUT"]
    write_line_to_file(output_filepath, f"{name}={value}")
