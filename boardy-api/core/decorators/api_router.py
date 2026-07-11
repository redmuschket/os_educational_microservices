from core.exceptions import (
    InternalServerErrorException,
    ServiceRepositoryError,
)
from functools import wraps
from typing import Callable
from fastapi import HTTPException
from fastapi import status
import logging

logger = logging.getLogger(__name__)


def handle_exceptions(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid request data: {str(e)}",
            )
        except ServiceRepositoryError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Storage service temporarily unavailable: {str(e)}",
            )
        except InternalServerErrorException as e:
            logger.error(f"Internal server error in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )
    return wrapper
