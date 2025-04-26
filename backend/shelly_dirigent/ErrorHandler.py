from rest_framework.response import Response


class ErrorHandler:

    def error(self, message: str, status_code: int, user_message: str = None):

        return Response(
            {"message": message},
            status=status_code,
        )
