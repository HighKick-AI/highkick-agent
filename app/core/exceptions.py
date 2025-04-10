from fastapi import HTTPException, status


class UniqueViolationException(Exception):
    pass


class ForeignKeyViolationException(Exception):
    pass


class NotNullViolationException(Exception):
    pass


class NotFoundException(Exception):
    pass


class DatabaseNotFoundException(NotFoundException):
    pass

class DashboardNotFoundException(NotFoundException):
    pass

class PromptNotFoundException(NotFoundException):
    pass

class ConversationNotFoundException(NotFoundException):
    pass

class TagNotFoundException(NotFoundException):
    pass

class AccountNotFoundException(NotFoundException):
    pass

class DocumentNotFoundException(NotFoundException):
    pass

class FilterNotFoundException(NotFoundException):
    pass

class ResourceProvisionError(Exception):
    pass


class AsyncDBPoolProvisionError(ResourceProvisionError):
    pass


class BadCredentialsException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad credentials"
        )


class RequiresAuthenticationException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Requires authentication",
        )


class UnableCredentialsException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to verify credentials",
        )


class HTTPStatusError(Exception):
    pass


class OktaGetUserException(Exception):
    pass


class OktaClientAccessTokenRetrievalException(Exception):
    pass


class NoDataForUpdateException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data for update",
        )
