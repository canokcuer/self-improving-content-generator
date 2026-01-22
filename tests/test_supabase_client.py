"""Tests for Supabase client module."""

import pytest
from unittest.mock import MagicMock, patch

from content_assistant.db.supabase_client import (
    get_client,
    get_admin_client,
    clear_client_cache,
    check_connection,
    DatabaseError,
)


class TestGetClient:
    """Test get_client function."""

    def setup_method(self):
        """Clear cache before each test."""
        clear_client_cache()

    def teardown_method(self):
        """Clear cache after each test."""
        clear_client_cache()

    def test_get_client_returns_client(self, mock_env_vars):
        """Test that get_client returns a Supabase client."""
        with patch("content_assistant.db.supabase_client.create_client") as mock_create:
            mock_client = MagicMock()
            mock_create.return_value = mock_client

            client = get_client()

            assert client == mock_client
            mock_create.assert_called_once()

    def test_get_client_uses_anon_key(self, mock_env_vars):
        """Test that get_client uses the anon key."""
        with patch("content_assistant.db.supabase_client.create_client") as mock_create:
            mock_create.return_value = MagicMock()

            get_client()

            # Check it was called with anon key (second argument)
            call_args = mock_create.call_args[0]
            assert call_args[1] == "test-anon-key"

    def test_get_client_caches_result(self, mock_env_vars):
        """Test that get_client caches the client instance."""
        with patch("content_assistant.db.supabase_client.create_client") as mock_create:
            mock_client = MagicMock()
            mock_create.return_value = mock_client

            client1 = get_client()
            client2 = get_client()

            assert client1 is client2
            mock_create.assert_called_once()

    def test_get_client_raises_on_error(self, mock_env_vars):
        """Test that get_client raises DatabaseError on failure."""
        with patch("content_assistant.db.supabase_client.create_client") as mock_create:
            mock_create.side_effect = Exception("Connection failed")

            with pytest.raises(DatabaseError) as exc_info:
                get_client()

            assert "Failed to create Supabase client" in str(exc_info.value)


class TestGetAdminClient:
    """Test get_admin_client function."""

    def setup_method(self):
        """Clear cache before each test."""
        clear_client_cache()

    def teardown_method(self):
        """Clear cache after each test."""
        clear_client_cache()

    def test_get_admin_client_returns_client(self, mock_env_vars):
        """Test that get_admin_client returns a Supabase client."""
        with patch("content_assistant.db.supabase_client.create_client") as mock_create:
            mock_client = MagicMock()
            mock_create.return_value = mock_client

            client = get_admin_client()

            assert client == mock_client

    def test_get_admin_client_uses_service_key(self, mock_env_vars):
        """Test that get_admin_client uses the service key."""
        with patch("content_assistant.db.supabase_client.create_client") as mock_create:
            mock_create.return_value = MagicMock()

            get_admin_client()

            # Check it was called with service key (second argument)
            call_args = mock_create.call_args[0]
            assert call_args[1] == "test-service-key"


class TestCheckConnection:
    """Test check_connection function."""

    def setup_method(self):
        """Clear cache before each test."""
        clear_client_cache()

    def teardown_method(self):
        """Clear cache after each test."""
        clear_client_cache()

    def test_check_connection_returns_true_on_success(self, mock_env_vars):
        """Test that check_connection returns True when connection works."""
        with patch("content_assistant.db.supabase_client.create_client") as mock_create:
            mock_client = MagicMock()
            mock_create.return_value = mock_client

            result = check_connection(mock_client)

            assert result is True

    def test_check_connection_returns_true_if_table_missing(self, mock_env_vars):
        """Test that check_connection returns True even if table doesn't exist."""
        with patch("content_assistant.db.supabase_client.create_client") as mock_create:
            mock_client = MagicMock()
            mock_client.table.return_value.select.return_value.limit.return_value.execute.side_effect = Exception(
                "relation does not exist"
            )
            mock_create.return_value = mock_client

            result = check_connection(mock_client)

            assert result is True

    def test_check_connection_raises_on_real_error(self, mock_env_vars):
        """Test that check_connection raises on actual connection errors."""
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.limit.return_value.execute.side_effect = Exception(
            "Network error: connection refused"
        )

        with pytest.raises(DatabaseError) as exc_info:
            check_connection(mock_client)

        assert "Connection check failed" in str(exc_info.value)
