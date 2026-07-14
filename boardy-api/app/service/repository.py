from ...exceptions import *
import logging
import aiomysql
from typing import Any, Dict, List, Optional, TypeVar, Generic
from contextlib import asynccontextmanager


logger = logging.getLogger(__name__)
ModelType = TypeVar("ModelType", bound=Dict[str, Any])


class RepositoryService:
    """
    Basic class for working with the database using aiomysql.
    Provides transaction management and error handling for query execution.
    """

    def __init__(self, pool: aiomysql.Pool):
        self._pool = pool
        self._current_conn: Optional[aiomysql.Connection] = None

    @staticmethod
    async def _execute_with_handling(coro, error_context: str = ""):
        """Performs a coroutine with general database error handling."""
        try:
            return await coro
        except aiomysql.IntegrityError as e:
            logger.error(f"Integrity error {error_context}: {e}")
            raise DatabaseError("Data integrity violation") from e
        except aiomysql.Error as e:
            logger.error(f"Database error {error_context}: {e}")
            raise DatabaseError(f"DB error: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error {error_context}: {e}")
            raise ServiceRepositoryError(f"Unknown error: {e}") from e

    async def begin_transaction(self) -> None:
        """Start a transaction: get a connection and save."""
        if self._current_conn is not None:
            raise RuntimeError("Transaction already started")
        self._current_conn = await self._pool.acquire()

    @asynccontextmanager
    async def get_connection(self):
        """Get a connection from the pool with automatic closing."""
        conn = await self._pool.acquire()
        try:
            yield conn
        finally:
            await self._pool.release(conn)

    async def commit_transaction(self) -> None:
        conn = self._current_conn
        if conn is None:
            raise RuntimeError("No active transaction")

        try:
            await conn.commit()
        except Exception:
            await self._pool.release(conn)
            self._current_conn = None
            logger.error(f"Failed to commit transaction: {e}")
            raise TransactionError(f"Failed to commit transaction: {e}") from e
        else:
            await self._pool.release(conn)
            self._current_conn = None

    async def rollback_transaction(self) -> None:
        """Roll back the transaction + liberation."""
        conn = self._current_conn
        if conn is None:
            logger.warning("rollback_transaction called with no active connection")
            return

        try:
            await conn.rollback()
        except Exception as e:
            await self._pool.release(conn)
            self._current_conn = None
            logger.error(f"Failed to rollback transaction: {e}")
            raise TransactionError(f"Failed to rollback transaction: {e}") from e
        else:
            await self._pool.release(conn)
            self._current_conn = None

    async def select(
        self,
        query: str,
        params: Optional[tuple] = None,
        fetch_one: bool = False,
        fetch_all: bool = False,
        dict_cursor: bool = False,
        conn: Optional[aiomysql.Connection] = None,
    ) -> Any:
        """Execute a request with error handling.
        - fetch_one=True will return one record (or None)
        - fetch_all=True returns a list of entries
        - otherwise it will return the cursor (for INSERT/UPDATE/DELETE)
        """
        if not query:
            raise RepositoryInputError("Query cannot be empty")

        actual_conn = conn or self._current_conn
        if actual_conn is None:
            async with self.get_connection() as new_conn:
                return await self._execute_select(query, params, fetch_one, fetch_all, dict_cursor, new_conn)
        else:
            return await self._execute_select(query, params, fetch_one, fetch_all, dict_cursor, actual_conn)

    @staticmethod
    async def _execute_select(query, params, fetch_one, fetch_all, dict_cursor, connection):
        cursor_class = aiomysql.DictCursor if dict_cursor else aiomysql.Cursor
        async with connection.cursor(cursor_class) as cur:
            await RepositoryService._execute_with_handling(
                cur.execute(query, params or ()),
                error_context=f"query: {query[:100]}"
            )
            if fetch_one:
                return await cur.fetchone()
            elif fetch_all:
                return await cur.fetchall()
            else:
                return cur

    async def insert_one(
        self,
        table: str,
        data: dict[str, Any],
        conn: Optional[aiomysql.Connection] = None
    ) -> int:
        """Insert one record and return its ID."""

        if not table:
            raise RepositoryInputError("Table name cannot be empty")
        if not data:
            raise RepositoryInputError("No data to insert")

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        actual_conn = conn or self._current_conn
        if actual_conn is None:
            async with self.get_connection() as new_conn:
                return await self._execute_insert(table, data, query, new_conn)
        else:
            return await self._execute_insert(table, data, query, actual_conn)

    @staticmethod
    async def _execute_insert(table, data, query, connection):
        async with connection.cursor() as cur:
            await RepositoryService._execute_with_handling(
                cur.execute(query, list(data.values())),
                error_context=f"insert into {table}"
            )
            return cur.lastrowid

    async def update_one(
        self,
        table: str,
        id_column: str,
        id_value: Any,
        data: dict[str, Any],
        conn: Optional[aiomysql.Connection] = None
    ) -> bool:
        """Update the record by ID."""

        if not table:
            raise RepositoryInputError("Table name cannot be empty")
        if not data:
            raise RepositoryInputError("No data to update")

        set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {id_column} = %s"
        params = list(data.values()) + [id_value]

        actual_conn = conn or self._current_conn
        if actual_conn is None:
            async with self.get_connection() as new_conn:
                return await self._execute_update(table, params, query, id_column, id_value, new_conn)
        else:
            return await self._execute_update(table, params, query, id_column, id_value, actual_conn)

    @staticmethod
    async def _execute_update(table, params, query, id_column, id_value, connection):
        async with connection.cursor() as cur:
            await RepositoryService._execute_with_handling(
                cur.execute(query, params),
                error_context=f"update {table} where {id_column}={id_value}"
            )
            return cur.rowcount > 0

    async def delete_one(
        self,
        table: str,
        id_column: str,
        id_value: Any,
        conn: Optional[aiomysql.Connection] = None
    ) -> bool:
        """Delete an entry by ID."""
        if not table:
            raise RepositoryInputError("Table name cannot be empty")

        query = f"DELETE FROM {table} WHERE {id_column} = %s"

        actual_conn = conn or self._current_conn
        if actual_conn is None:
            async with self.get_connection() as new_conn:
                return await self._execute_delete(table, query, id_column, id_value, new_conn)
        else:
            return await self._execute_delete(table, query, id_column, id_value, actual_conn)

    @staticmethod
    async def _execute_delete(table, query, id_column, id_value, connection):
        async with connection.cursor() as cur:
            await RepositoryService._execute_with_handling(
                cur.execute(query, (id_value,)),
                error_context=f"delete from {table} where {id_column}={id_value}"
            )
            return cur.rowcount > 0