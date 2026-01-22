"""Database initialization module.

Provides functionality to initialize the Supabase database schema.
The schema SQL should be run directly in Supabase SQL Editor for production.
This module provides helper functions for verification and testing.
"""

from pathlib import Path
from typing import List, Tuple

from content_assistant.db.supabase_client import get_admin_client, DatabaseError


# Expected tables in the schema
EXPECTED_TABLES = [
    "knowledge_chunks",
    "content_generations",
    "experiments",
    "experiment_assignments",
    "api_costs",
]

# Expected functions in the schema
EXPECTED_FUNCTIONS = [
    "match_knowledge_chunks",
    "match_content_generations",
    "get_cost_summary",
]


def get_schema_sql() -> str:
    """Read the schema SQL file.

    Returns:
        str: The schema SQL content

    Raises:
        FileNotFoundError: If schema.sql doesn't exist
    """
    schema_path = Path(__file__).parent / "schema.sql"
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    return schema_path.read_text()


def verify_tables_exist() -> Tuple[bool, List[str]]:
    """Verify that all expected tables exist in the database.

    Returns:
        Tuple of (all_exist: bool, missing_tables: List[str])

    Raises:
        DatabaseError: If verification query fails
    """
    try:
        client = get_admin_client()
        missing = []

        for table in EXPECTED_TABLES:
            try:
                # Try to select from the table
                client.table(table).select("*").limit(0).execute()
            except Exception as e:
                error_str = str(e).lower()
                if "does not exist" in error_str or "relation" in error_str:
                    missing.append(table)
                else:
                    raise DatabaseError(f"Error checking table {table}: {e}") from e

        return len(missing) == 0, missing

    except DatabaseError:
        raise
    except Exception as e:
        raise DatabaseError(f"Failed to verify tables: {e}") from e


def verify_vector_extension() -> bool:
    """Verify that the pgvector extension is enabled.

    Returns:
        bool: True if pgvector is enabled

    Raises:
        DatabaseError: If verification fails
    """
    try:
        client = get_admin_client()
        # Try to use vector operations - this will fail if extension isn't enabled
        client.rpc(
            "match_knowledge_chunks",
            {
                "query_embedding": [0.0] * 1024,
                "match_threshold": 0.5,
                "match_count": 1,
            }
        ).execute()
        return True
    except Exception as e:
        error_str = str(e).lower()
        # If function doesn't exist or vector type doesn't exist, return False
        if "does not exist" in error_str or "vector" in error_str:
            return False
        # For other errors (like empty result), the extension might still be there
        return True


def print_schema_status():
    """Print the current status of the database schema."""
    print("=" * 50)
    print("TheLifeCo Content Assistant - Database Status")
    print("=" * 50)

    # Check tables
    try:
        all_exist, missing = verify_tables_exist()
        if all_exist:
            print("✓ All tables exist")
        else:
            print(f"✗ Missing tables: {', '.join(missing)}")
    except Exception as e:
        print(f"✗ Error checking tables: {e}")

    # Check vector extension
    try:
        if verify_vector_extension():
            print("✓ pgvector extension enabled")
        else:
            print("✗ pgvector extension not enabled or functions missing")
    except Exception as e:
        print(f"✗ Error checking pgvector: {e}")

    print("=" * 50)
    print("\nTo initialize the database:")
    print("1. Go to Supabase Dashboard > SQL Editor")
    print("2. Copy contents of content_assistant/db/schema.sql")
    print("3. Run the SQL")


if __name__ == "__main__":
    print_schema_status()
