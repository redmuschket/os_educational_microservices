import time
from typing import TypeVar, Generic, Type, Callable, Any, Optional
from abc import ABC, abstractmethod

R = TypeVar("R")  # repository type


class BaseTransactionalExecutor(ABC, Generic[R]):
    """
    An abstract base class for any components that perform operations
    with support for transactions.
    """

    def __init__(self, repository: R):
        self.repository = repository