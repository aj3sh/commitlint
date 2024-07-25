# type: ignore
# pylint: disable=all
import os
from unittest.mock import patch

import pytest

from github_actions.action.utils import get_boolean_input


def test__get_boolean_input__return_True_for_True():
    with patch.dict(os.environ, {"INPUT_TEST": "True"}):
        assert get_boolean_input("test") == True


def test__get_boolean_input__return_True_for_TRUE():
    with patch.dict(os.environ, {"INPUT_TEST": "TRUE"}):
        assert get_boolean_input("test") == True


def test__get_boolean_input__return_True_for_true():
    with patch.dict(os.environ, {"INPUT_TEST": "true"}):
        assert get_boolean_input("test") == True


def test__get_boolean_input__return_False_for_False():
    with patch.dict(os.environ, {"INPUT_TEST": "False"}):
        assert get_boolean_input("test") == False


def test__get_boolean_input__return_False_for_FALSE():
    with patch.dict(os.environ, {"INPUT_TEST": "FALSE"}):
        assert get_boolean_input("test") == False


def test__get_boolean_input__return_False_for_false():
    with patch.dict(os.environ, {"INPUT_TEST": "false"}):
        assert get_boolean_input("test") == False


def test__get_boolean_input__raises_type_error_for_unknown():
    with patch.dict(os.environ, {"INPUT_TEST": "random"}):
        with pytest.raises(TypeError):
            get_boolean_input("test")
