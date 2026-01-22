"""Test project initialization."""

import content_assistant


def test_version():
    """Test that version is defined."""
    assert content_assistant.__version__ == "0.1.0"


def test_author():
    """Test that author is defined."""
    assert content_assistant.__author__ == "TheLifeCo"
