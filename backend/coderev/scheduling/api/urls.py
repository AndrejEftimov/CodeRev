from django.urls import path

from .views import (
    host_review_slot_detail,
    host_review_slot_list,
    public_review_slot_book,
    public_review_slot_list,
)


app_name = "scheduling-api"


urlpatterns = [
    path(
        "review-slots/",
        public_review_slot_list,
        name="public-review-slot-list",
    ),
    path(
        "review-slots/<uuid:review_slot_uuid>/book/",
        public_review_slot_book,
        name="public-review-slot-book",
    ),
    path(
        "host/review-slots/",
        host_review_slot_list,
        name="host-review-slot-list",
    ),
    path(
        "host/review-slots/<uuid:review_slot_uuid>/",
        host_review_slot_detail,
        name="host-review-slot-detail",
    ),
]
