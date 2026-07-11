import time
import logging
import asyncio
from functools import wraps
from typing import Callable, Any, Optional, Union

logger = logging.getLogger(__name__)


# ---- Method-level decorator for fine-tuning ----
def timed(
    enabled: bool = True,
    log_exceptions: Optional[bool] = None,
    log_args: bool = False,
    log_result: bool = False,
):
    """
    Method decorator to override logging behaviour for a specific method.

    Args:
        enabled: if False, the method will NOT be wrapped (no timing logs).
        log_exceptions: if True, exceptions will be logged with traceback.
                        If None, uses the class-level default.
        log_args: if True, logs the arguments passed to the method.
        log_result: if True, logs the returned value (be careful with large objects).
    """
    def decorator(func):
        func._timed_enabled = enabled
        if log_exceptions is not None:
            func._timed_log_exceptions = log_exceptions
        func._timed_log_args = log_args
        func._timed_log_result = log_result
        return func
    return decorator


# ---- Internal wrapper that adds timing logic ----
def _timed_method(
    func: Callable,
    log_exceptions_default: bool = True,
    log_args_default: bool = False,
    log_result_default: bool = False,
) -> Callable:
    """
    Wraps a function (sync or async) with timing and logging.

    It respects method-level overrides set by @timed.
    """
    # Read method-specific settings, fallback to class defaults
    enabled = getattr(func, '_timed_enabled', True)
    if not enabled:
        # If explicitly disabled, return the original function unwrapped
        return func

    log_exceptions = getattr(func, '_timed_log_exceptions', log_exceptions_default)
    log_args = getattr(func, '_timed_log_args', log_args_default)
    log_result = getattr(func, '_timed_log_result', log_result_default)

    # Determine if the function is async
    is_async = asyncio.iscoroutinefunction(func)

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start = time.perf_counter()
        # Build log message prefix
        log_msg = f"{func.__qualname__}"
        if log_args:
            log_msg += f" args={args} kwargs={kwargs}"

        logger.info(f"Starting {log_msg}")
        try:
            result = await func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            if log_result:
                logger.info(f"Finished {func.__qualname__} in {elapsed:.4f}s, result={result}")
            else:
                logger.info(f"Finished {func.__qualname__} in {elapsed:.4f}s")
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start
            if log_exceptions:
                logger.exception(f"Exception in {func.__qualname__} after {elapsed:.4f}s: {e}")
            else:
                logger.error(f"Exception in {func.__qualname__} after {elapsed:.4f}s: {e}")
            raise   # re-raise the exception

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start = time.perf_counter()
        log_msg = f"{func.__qualname__}"
        if log_args:
            log_msg += f" args={args} kwargs={kwargs}"

        logger.info(f"Starting {log_msg}")
        try:
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            if log_result:
                logger.info(f"Finished {func.__qualname__} in {elapsed:.4f}s, result={result}")
            else:
                logger.info(f"Finished {func.__qualname__} in {elapsed:.4f}s")
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start
            if log_exceptions:
                logger.exception(f"Exception in {func.__qualname__} after {elapsed:.4f}s: {e}")
            else:
                logger.error(f"Exception in {func.__qualname__} after {elapsed:.4f}s: {e}")
            raise

    return async_wrapper if is_async else sync_wrapper


# ---- Class decorator ----
def timed_class(
    exclude_private: bool = False,
    log_exceptions: bool = True,
    log_args: bool = False,
    log_result: bool = False,
):
    """
    Class decorator that applies timing/logging to all public (and optionally private)
    methods, including staticmethods and classmethods.

    Args:
        exclude_private: if True, methods starting with '_' are not wrapped.
        log_exceptions: default for logging exceptions with traceback.
        log_args: default for logging arguments.
        log_result: default for logging return values.
    """
    def decorator(cls):
        for attr_name, attr_value in list(cls.__dict__.items()):
            if not callable(attr_value) and not isinstance(attr_value, (staticmethod, classmethod)):
                continue

            # Skip special methods (dunder)
            if attr_name.startswith("__") and attr_name.endswith("__"):
                continue

            # Skip private (single underscore) if requested
            if attr_name.startswith("_") and exclude_private:
                continue

            # Handle staticmethod
            if isinstance(attr_value, staticmethod):
                original_func = attr_value.__func__
                wrapped = _timed_method(
                    original_func,
                    log_exceptions_default=log_exceptions,
                    log_args_default=log_args,
                    log_result_default=log_result,
                )
                setattr(cls, attr_name, staticmethod(wrapped))
                continue

            # Handle classmethod
            if isinstance(attr_value, classmethod):
                original_func = attr_value.__func__
                wrapped = _timed_method(
                    original_func,
                    log_exceptions_default=log_exceptions,
                    log_args_default=log_args,
                    log_result_default=log_result,
                )
                setattr(cls, attr_name, classmethod(wrapped))
                continue

            # Regular method (function)
            wrapped = _timed_method(
                attr_value,
                log_exceptions_default=log_exceptions,
                log_args_default=log_args,
                log_result_default=log_result,
            )
            setattr(cls, attr_name, wrapped)

        return cls
    return decorator