from rest_framework.exceptions import APIException

class InvalidPayload(APIException):
    status_code = 400
    default_detail = 'Invalid request payload.'
    default_code = 'invalid_payload'