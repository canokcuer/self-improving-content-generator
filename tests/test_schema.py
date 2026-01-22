"""Tests for database schema module."""

from pathlib import Path

from content_assistant.db.init_db import (
    get_schema_sql,
    EXPECTED_TABLES,
    EXPECTED_FUNCTIONS,
)


class TestSchemaSQL:
    """Test schema SQL file."""

    def test_schema_file_exists(self):
        """Test that schema.sql file exists."""
        schema_path = Path(__file__).parent.parent / "content_assistant" / "db" / "schema.sql"
        assert schema_path.exists(), f"Schema file not found: {schema_path}"

    def test_get_schema_sql_returns_content(self):
        """Test that get_schema_sql returns SQL content."""
        sql = get_schema_sql()
        assert isinstance(sql, str)
        assert len(sql) > 0

    def test_schema_contains_expected_tables(self):
        """Test that schema SQL creates all expected tables."""
        sql = get_schema_sql()

        for table in EXPECTED_TABLES:
            assert f"CREATE TABLE IF NOT EXISTS {table}" in sql, f"Missing table: {table}"

    def test_schema_contains_vector_extension(self):
        """Test that schema enables pgvector extension."""
        sql = get_schema_sql()
        assert "CREATE EXTENSION IF NOT EXISTS vector" in sql

    def test_schema_contains_expected_functions(self):
        """Test that schema creates expected functions."""
        sql = get_schema_sql()

        for func in EXPECTED_FUNCTIONS:
            assert f"CREATE OR REPLACE FUNCTION {func}" in sql, f"Missing function: {func}"

    def test_schema_contains_rls_policies(self):
        """Test that schema includes Row Level Security policies."""
        sql = get_schema_sql()
        assert "ENABLE ROW LEVEL SECURITY" in sql
        assert "CREATE POLICY" in sql

    def test_schema_contains_indexes(self):
        """Test that schema creates necessary indexes."""
        sql = get_schema_sql()
        # Check for vector indexes
        assert "ivfflat" in sql
        assert "vector_cosine_ops" in sql

    def test_schema_uses_correct_vector_dimension(self):
        """Test that schema uses 1024-dimensional vectors."""
        sql = get_schema_sql()
        # Should have vector(1024) for embeddings
        assert "vector(1024)" in sql

    def test_schema_has_updated_at_trigger(self):
        """Test that schema includes updated_at timestamp trigger."""
        sql = get_schema_sql()
        assert "update_updated_at_column" in sql
        assert "BEFORE UPDATE" in sql
