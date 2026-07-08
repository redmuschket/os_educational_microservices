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

    async def _execute_with_handling(self, coro, error_context: str = ""):
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

    @asynccontextmanager
    async def get_connection(self):
        """Get a connection from the pool with automatic closing."""
        conn = await self._pool.acquire()
        try:
            yield conn
        finally:
            await self._pool.release(conn)

    async def select(
        self,
        query: str,
        params: Optional[tuple] = None,
        fetch_one: bool = False,
        fetch_all: bool = False,
        dict_cursor: bool = False,
    ) -> Any:
        """Execute a request with error handling.
        - fetch_one=True will return one record (or None)
        - fetch_all=True returns a list of entries
        - otherwise it will return the cursor (for INSERT/UPDATE/DELETE)
        """
        try:
            async with self.get_connection() as conn:
                cursor_class = aiomysql.DictCursor if dict_cursor else aiomysql.Cursor
                async with conn.cursor(cursor_class) as cur:
                    await self._execute_with_handling(
                        cur.execute(query, params or ()),
                        error_context=f"query: {query[:100]}"
                    )
                    if fetch_one:
                        return await cur.fetchone()
                    elif fetch_all:
                        return await cur.fetchall()
                    else:
                        return cur
        except aiomysql.Error as e:
            logger.error(f"Database error (connection): {e}, query: {query[:100]}")
            raise DatabaseError(f"Database connection error: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error (connection): {e}, query: {query[:100]}")
            raise

    async def commit_transaction(self, conn: aiomysql.Connection) -> None:
        """Commit the transaction."""
        try:
            await conn.commit()
        except Exception as e:
            logger.error(f"Failed to commit transaction: {e}")
            await self.rollback_transaction(conn)
            raise TransactionError(f"Failed to commit transaction: {e}") from e

    async def rollback_transaction(self, conn: aiomysql.Connection) -> None:
        """Roll back the transaction."""
        try:
            await conn.rollback()
        except Exception as e:
            logger.error(f"Failed to rollback transaction: {e}")

    async def insert_one(
        self, table: str, data: dict[str, Any], conn: Optional[aiomysql.Connection] = None
    ) -> int:
        """Insert one record and return its ID."""

        if not table:
            raise RepositoryInputError("Table name cannot be empty")
        if not data:
            raise RepositoryInputError("No data to insert")

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        async def _do_insert(connection):
            async with connection.cursor() as cur:
                await self._execute_with_handling(
                    cur.execute(query, list(data.values())),
                    error_context=f"insert into {table}"
                )
                return cur.lastrowid

        if conn:
            return await _do_insert(conn)
        else:
            async with self.get_connection() as conn:
                return await _do_insert(conn)

    async def update_one(
        self, table: str, id_column: str, id_value: Any, data: dict[str, Any],
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

        async def _do_update(connection):
            async with connection.cursor() as cur:
                await self._execute_with_handling(
                    cur.execute(query, params),
                    error_context=f"update {table} where {id_column}={id_value}"
                )
                return cur.rowcount > 0

        if conn:
            return await _do_update(conn)
        else:
            async with self.get_connection() as conn:
                return await _do_update(conn)

    async def delete_one(
        self, table: str, id_column: str, id_value: Any,
        conn: Optional[aiomysql.Connection] = None
    ) -> bool:
        """Delete an entry by ID."""
        if not table:
            raise RepositoryInputError("Table name cannot be empty")

        query = f"DELETE FROM {table} WHERE {id_column} = %s"

        async def _do_delete(connection):
            async with connection.cursor() as cur:
                await self._execute_with_handling(
                    cur.execute(query, (id_value,)),
                    error_context=f"delete from {table} where {id_column}={id_value}"
                )
                return cur.rowcount > 0

        if conn:
            return await _do_delete(conn)
        else:
            async with self.get_connection() as conn:
                return await _do_delete(conn)