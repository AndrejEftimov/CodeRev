from django.http import HttpResponse, JsonResponse


#======================================
# SUCCESS RESPONSES
#======================================

def json_response(data, *, status=200):
    """Return a JSON response using a top-level object payload."""

    return JsonResponse(data, status=status)


def empty_response(*, status=204):
    """Return an empty HTTP response."""

    return HttpResponse(status=status)


#======================================
# ERROR RESPONSES
#======================================

def error_response(*, code, message, status, fields=None):
    """Return the standard CodeRev API error envelope."""

    error = {
        "code": code,
        "message": message,
    }

    if fields:
        error["fields"] = fields

    return JsonResponse(
        {
            "error": error,
        },
        status=status,
    )
