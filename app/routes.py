from flask import Blueprint

api = Blueprint("api", __name__)


# Every response uses one of two shapes:
#   success: {"data": ...}
#   error:   {"error": "some_error_code", "details": {...}}
def success_response(data, status=200):
    return {"data": data}, status


def error_response(error, details, status):
    return {"error": error, "details": details}, status


@api.get("/health")
def health():
    return success_response({"status": "ok"})
