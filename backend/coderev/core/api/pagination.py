from math import ceil


DEFAULT_MAX_PAGE_SIZE = 50


class PaginationError(ValueError):
    """Raised when pagination query parameters are invalid."""


#======================================
# PAGINATION
#======================================

def paginate_queryset(
    queryset,
    request,
    *,
    default_page_size,
    max_page_size=DEFAULT_MAX_PAGE_SIZE,
):
    """Return one queryset page and stable pagination metadata."""

    page = _parse_positive_int(
        request.GET.get("page"),
        name="page",
        default=1,
    )
    page_size = _parse_positive_int(
        request.GET.get("pageSize"),
        name="pageSize",
        default=default_page_size,
    )

    if page_size > max_page_size:
        raise PaginationError(
            f"pageSize must be less than or equal to {max_page_size}."
        )

    total_items = queryset.count()
    total_pages = max(1, ceil(total_items / page_size))
    page = min(page, total_pages)

    start = (page - 1) * page_size
    end = start + page_size

    return queryset[start:end], {
        "page": page,
        "pageSize": page_size,
        "totalItems": total_items,
        "totalPages": total_pages,
    }


def _parse_positive_int(value, *, name, default):
    if value in (None, ""):
        return default

    try:
        parsed = int(value)
    except (TypeError, ValueError) as error:
        raise PaginationError(
            f"{name} must be a positive integer."
        ) from error

    if parsed < 1:
        raise PaginationError(
            f"{name} must be a positive integer."
        )

    return parsed
