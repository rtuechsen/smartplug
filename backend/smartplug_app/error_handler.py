"""Contains classes for handling errors.

TODO: more details ???
"""

from rest_framework.response import Response
from rest_framework import status
from .logger import Logger


class BackendError(Exception):
    """A custom exception that should be used to report errors in the backend.

    In addition to a message it also offers to set a HTTP error code and
    an alternative user facing message.
    """

    def __init__(
        self, message: str, status_code: int = None, user_message: str = None
    ):
        """Constructor for the class.

        @param message The main message. Usually includes technical details
        aimed at admins.

        @param status_code An optional HTTP error code that matches the error
        best. Should be used if the error occured while processing a REST API
        request.

        @param user_message An optional user facing message. Should be used if
        the error occured while processing a REST API request and the main
        message might contain either information about the backends
        implementation or contains user input. Sending responses with user
        input might open the door for injection attacks.
        """
        # Calling the base class constructor with the arguments it needs.
        super().__init__(message)

        ## The main message. Usually includes technical details aimed at admins.
        self.message = message

        ## An optional HTTP error code that matches the error best. Should be
        ## used if the error occured while processing a REST API request.
        self.status_code = status_code

        ## An optional user facing message. Should be used if the error occured
        ## while processing a REST API request and the main message might
        ## contain either information about the backends implementation or
        ## contains user input. Sending repsonses with user input might open
        ## the door for injection attacks.
        self.user_message = user_message


class ErrorHandler:
    """A class that logs errors and generates an error response for the REST
    API."""

    def __init__(self):
        """Constructor for the class."""

        ## The logger instance (singleton) to log events and errors.
        self._logger = Logger()

    def response(
        self,
        message: str,
        status_code: int = None,
        user_message: str = None,
        client_ip_address: str = None,
        username: str = None,
    ) -> Response:
        """Generates an error response and logs the error.

        @param message The message that will be logged. If 'user_message' is
        not set, 'message' will also be used for the response. Please formulate
        a complete sentence starting with a capital letter and ending with a
        period.

        @param status_code The desired HTTP status code of the error. Choose a
        fitting one, preferably from 'rest_framework.status'. If not set
        '500 Internal Server Error' will be used.

        @param user_message The message for the response. If not set, 'message'
        will be used for the response. Please formulate a complete sentence
        starting with a capital letter and ending with a period.

        @return Repsonse (from Django Rest Framework) containing the error
        message.
        """

        # in any case log the error
        self._logger.error(message, client_ip_address, username)

        if status_code is None:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        if user_message is None:
            user_message = (
                "The server encountered an internal error, please contact the "
                "admin."
            )

        return Response(
            {"message": "ERROR: " + user_message}, status=status_code
        )
