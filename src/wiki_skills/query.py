from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

DEFAULT_QUERY_DB: str | None = None


def query(sql: str, db: str | None = DEFAULT_QUERY_DB) -> None:
    """Execute *sql* against a ``state.db`` and print results to stdout.

    When *db* is ``None``, the default path ``<CWD>/.wiki-skills/state.db``
    is used.  Results are printed as column-separated values with a header
    row.
    """
    db_path = Path(db) if db is not None else Path.cwd() / ".wiki-skills" / "state.db"

    if not db_path.exists():
        print(f"ERROR — database not found: {db_path}", file=sys.stderr)  # noqa: T201
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.execute(sql)
        if cursor.description is None:
            print("(no results)")  # noqa: T201
            return

        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        print("  ".join(columns))  # noqa: T201
        for row in rows:
            print("  ".join(str(v) for v in row))  # noqa: T201
    except sqlite3.OperationalError as exc:
        print(f"ERROR — SQL error: {exc}", file=sys.stderr)  # noqa: T201
        sys.exit(1)
    finally:
        conn.close()
