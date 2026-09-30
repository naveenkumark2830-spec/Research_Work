class BaseAppException(Exception):
    """Base exception for application errors."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class InvalidStateTransitionError(BaseAppException):
    """Raised when an invalid state transition is requested."""
    def __init__(self, current_status: str, action: str, allowed_states: list[str]):
        message = (
            f"Cannot execute '{action}' action when simulation status is '{current_status}'. "
            f"Allowed states for this action: {allowed_states}"
        )
        super().__init__(message=message, status_code=400)


class ResourceNotFoundError(BaseAppException):
    """Raised when a requested resource is not found."""
    def __init__(self, resource_name: str, resource_id: str):
        message = f"{resource_name} with ID '{resource_id}' was not found."
        super().__init__(message=message, status_code=404)


class UserIsolationError(BaseAppException):
    """Raised when a user attempts to access a session belonging to another user."""
    def __init__(self, user_id: str, session_id: str):
        message = f"User '{user_id}' does not have authorization for session '{session_id}'."
        super().__init__(message=message, status_code=403)
