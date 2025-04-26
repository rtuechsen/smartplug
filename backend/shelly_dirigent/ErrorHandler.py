from rest_framework.response import Response
from rest_framework import status
from .Logger import Logger


class BackendError(Exception):

    def __init__(self, message: str, status_code: int = None, user_message: str = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.user_message = user_message


class ErrorHandler:

    def __init__(self):
        self.logger = Logger()

    def response(
        self, message: str, status_code: int = None, user_message: str = None
    ) -> Response:
        """
        Generates an error response and logs the error.

        @param message The message that will be logged. If 'user_message' is not set, 'message' will also be used for the response. Please formulate a complete sentence starting with a capital letter and ending with a period.

        @param status_code The desired HTTP status code of the error. Choose a fitting one, preferably from 'rest_framework.status'. If not set '500 Internal Server Error' will be used.

        @param user_message The message for the response. If not set, 'message' will be used for the response. Please formulate a complete sentence starting with a capital letter and ending with a period.

        @return Repsonse (from Django Rest Framework) containing the error message.
        """

        # in any case log the error
        self.logger.log("ERROR: " + message)

        if status_code is None:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        if user_message is None:
            user_message = (
                "The server encountered an internal error, please contact the admin."
            )

        return Response({"message": user_message}, status=status_code)
