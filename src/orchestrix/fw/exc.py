from fastapi import HTTPException

class OrchestrixError(HTTPException):
    """
    Base class for exceptions in this module.
    """

class NotFoundError(OrchestrixError):
    """
    Exception raised when object is not found
    """

    def __init__(self, *, detail = None, headers = None, message=None):
        if message:
            message = f"NotFound: {message}"
        if detail is None and message:
            detail = [{
                "msg": message
            }]
        if isinstance(detail, list):
            detail.append({
                'msg': message
            })
        super().__init__(404, detail, headers)

class AlreadyExistError(OrchestrixError):
    """
    Exception raised when object already exists
    """
    def __init__(self, *, message = None, headers = None):
        status_code = 422
        detail = [{
                "msg": message or "Object already exists",
                "type": "already_exist_error"
        }]
        super().__init__(status_code, detail, headers)


class FieldValidationError(OrchestrixError):
    """
    Exception raised when a field failed validation
    """

    def __init__(self, *, field_location: list[str] = None, message=None, headers = None):
        status_code = 422
        if field_location:
            detail = [{
                "loc": field_location,
                "msg": message or "Unprocessable Entity",
                "type": "value_error"
            }]
        else:
            detail = [{
                "msg": message or "Unprocessable Entity",
                "type": "value_error"
            }]
        super().__init__(status_code, detail, headers)

class ModelValidationError(OrchestrixError):
    """
    Exception raised when a model failed validation
    """
    def __init__(self, *, message = None, headers = None):
        status_code = 422
        detail = [{
                "msg": "Model failed validation" or message,
                "type": "model_validation_error"
        }]
        super().__init__(status_code, detail, headers)