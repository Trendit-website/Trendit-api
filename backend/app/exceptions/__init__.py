'''
This module defines custom exceptions for the Trendit³ Flask application.

It includes exceptions for handling situations such as when a user still has a pending task, 
when no unassigned task is found, and when a unique slug cannot be created.

Each exception is a class that inherits from the base `Exception` class and includes a message 
that describes the error condition.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''

class PendingTaskError(Exception):
    """Exception raised when user still has a pending task."""

    def __init__(self, message="There is still a pending task yet to be done.", status_code=409):
        super().__init__(message)
        self.status_code = status_code
        self.message = message


class NoUnassignedTaskError(Exception):
    """Exception raised when no unassigned task is found."""

    def __init__(self, message="No unassigned task found", status_code=200):
        super().__init__(message)
        self.status_code = status_code
        self.message = message


class UniqueSlugError(Exception):
    """
    Exception raised when a unique slug cannot be created.

    Attributes:
        name (str): The name used to generate the slug.
        type (str): The type of the object for which the slug is being generated.
        msg (str, optional): A custom error message. Defaults to None.

    Methods:
        __str__: Returns a string representation of the exception.
    """
    def __init__(self, name, type, msg=None):
        self.name = name
        self.type = type
        self.msg = msg
        super().__init__(f"Unable to create a unique slug for name: {name}, type: {type}")
    
    def __str__(self):
        if self.msg:
            return f"\n\n {self.msg}: <name: {self.name}, type: {self.type}> \n\n"
        else:
            return f"\n\n Unable to create a unique slug for name: {self.name}, type: {self.type} \n\n"

class InvalidTwoFactorMethod(Exception):
    """Exception raised when invalid 2FA method is provided."""

    def __init__(self, message="Invalid 2FA method.", status_code=400):
        super().__init__(message)
        self.status_code = status_code
        self.message = message