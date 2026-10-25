from django.middleware.csrf import get_token

from .responses import error_response, json_response


#======================================
# CSRF
#======================================

def csrf_token(request):
    """Return a CSRF token and ensure Django sends the CSRF cookie."""

    if request.method != "GET":
        return error_response(
            code="method_not_allowed",
            message="This endpoint only supports GET requests.",
            status=405,
        )

    return json_response(
        {
            "csrfToken": get_token(request),
        }
    )
