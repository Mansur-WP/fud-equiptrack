from django.db import transaction
from django.utils.translation import gettext as _

from .models import RentalRequest


class InvalidRequestStateError(Exception):
    """Raised when an operation is performed on a request in an invalid state."""
    pass


class RequestAlreadyProcessedError(InvalidRequestStateError):
    """Raised when a request has already been approved or rejected."""
    pass


@transaction.atomic
def approve_request(rental_request: RentalRequest, remarks: str = "") -> RentalRequest:
    """
    Approve a rental request.
    
    Checks if the request is PENDING, deducts the requested quantity from the 
    equipment's available_quantity, sets status to APPROVED, and saves remarks.
    
    Raises:
        RequestAlreadyProcessedError: If the request is not PENDING.
        InvalidRequestStateError: If the equipment does not have enough available quantity.
    """
    # Lock the rental request and equipment rows to prevent race conditions
    rental_request = RentalRequest.objects.select_for_update().get(pk=rental_request.pk)
    equipment = rental_request.equipment

    if rental_request.status != RentalRequest.Status.PENDING:
        raise RequestAlreadyProcessedError(
            _("Cannot approve request: it has already been processed (Status: %(status)s).") % {"status": rental_request.status}
        )

    if equipment.available_quantity < rental_request.quantity:
        raise InvalidRequestStateError(
            _("Cannot approve request: only %(available)s units of '%(name)s' are available, but %(requested)s were requested.") % {
                "available": equipment.available_quantity,
                "name": equipment.name,
                "requested": rental_request.quantity,
            }
        )

    # Update equipment inventory
    equipment.available_quantity -= rental_request.quantity
    equipment.save(update_fields=["available_quantity", "updated_at"])

    # Update request status
    rental_request.status = RentalRequest.Status.APPROVED
    rental_request.remarks = remarks
    rental_request.save(update_fields=["status", "remarks", "updated_at"])

    return rental_request


@transaction.atomic
def reject_request(rental_request: RentalRequest, remarks: str = "") -> RentalRequest:
    """
    Reject a rental request.
    
    Checks if the request is PENDING, sets status to REJECTED, and saves remarks.
    
    Raises:
        RequestAlreadyProcessedError: If the request is not PENDING.
    """
    # Lock the rental request row
    rental_request = RentalRequest.objects.select_for_update().get(pk=rental_request.pk)

    if rental_request.status != RentalRequest.Status.PENDING:
        raise RequestAlreadyProcessedError(
            _("Cannot reject request: it has already been processed (Status: %(status)s).") % {"status": rental_request.status}
        )

    rental_request.status = RentalRequest.Status.REJECTED
    rental_request.remarks = remarks
    rental_request.save(update_fields=["status", "remarks", "updated_at"])

    return rental_request
