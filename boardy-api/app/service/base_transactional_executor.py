import time
from typing import TypeVar, Generic, Type, Callable, Any, Optional
from abc import ABC, abstractmethod

import logging

logger = logging.getLogger(__name__)

R = TypeVar("R")  # repository type


class BaseTransactionalExecutor(ABC, Generic[R]):
    """
    An abstract base class for any components that perform operations
    with support for transactions, runtime logging, and error handling.
    """

    def __init__(self, repository: R):
        self.repository = repository