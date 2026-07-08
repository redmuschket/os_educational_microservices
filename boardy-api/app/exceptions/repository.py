from .service import ServiceError

class ServiceRepositoryError(ServiceError):
    """Repository service level error"""
    pass


class DatabaseError(ServiceRepositoryError):
    """Database error"""
    pass


class TransactionError(DatabaseError):
    """Transaction error"""
    pass


class RepositoryInputError(ServiceRepositoryError):
    """Error in the input data in the repository service"""
    pass
