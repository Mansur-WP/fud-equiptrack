from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from django.db.models import Case, CharField, F, Value, When


from .models import Rental, RentalRequest


@dataclass(frozen=True)
class RequestManagementRow:
    request_id: int
    requester_name: str
    requester_role: str
    equipment_name: str
    equipment_serial: str
    request_date: date
    expected_return_date: date
    status: str
    status_display: str


def annotate_request_management_queryset(qs):
    """Annotate RentalRequest queryset with derived history status.

    Derived statuses:
    - Pending / Approved / Rejected: from RentalRequest.status
    - Issued: Rental exists and Rental.status in (ACTIVE, OVERDUE)
    - Returned: Rental exists and Rental.status == RETURNED

    This keeps business logic untouched; it only maps existing state to
    admin UI-friendly labels.
    """

    qs = qs.select_related("requester", "equipment")

    # reverse relation: RentalRequest -> rental (OneToOne)
    qs = qs.annotate(
        rental_status=F("rental__status"),
    )

    qs = qs.annotate(
        history_status=Case(
            When(
                status=RentalRequest.Status.PENDING,
                then=Value(RentalRequest.Status.PENDING),
            ),
            When(
                status=RentalRequest.Status.APPROVED,
                then=Value(RentalRequest.Status.APPROVED),
            ),
            When(
                status=RentalRequest.Status.REJECTED,
                then=Value(RentalRequest.Status.REJECTED),
            ),
            When(
                rental__status=Rental.Status.RETURNED,
                then=Value("RETURNED"),
            ),
            When(
                rental__status__in=[Rental.Status.ACTIVE, Rental.Status.OVERDUE],
                then=Value("ISSUED"),
            ),

            default=Value("UNKNOWN"),
            output_field=CharField(),
        ),
    )

    # status display derived in template; still provide a stable fallback
    qs = qs.annotate(
        history_status_display=Case(
            When(history_status="PENDING", then=Value("Pending")),
            When(history_status="APPROVED", then=Value("Approved")),
            When(history_status="REJECTED", then=Value("Rejected")),
            When(history_status="ISSUED", then=Value("Issued")),
            When(history_status="RETURNED", then=Value("Returned")),
            default=F("history_status"),
            output_field=CharField(),
        )
    )

    return qs

