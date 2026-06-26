from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext as _

from equipment.models import Equipment
from .models import RentalRequest, Rental


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


class InvalidRentalRequestError(Exception):
    """Raised when an operation is performed on an invalid rental request."""
    pass


class RequestAlreadyIssuedError(InvalidRentalRequestError):
    """Raised when trying to issue equipment for a request that is already issued."""
    pass


class EquipmentUnavailableError(InvalidRentalRequestError):
    """Raised when equipment available_quantity is less than requested quantity."""
    pass


@transaction.atomic
def issue_equipment(rental_request: RentalRequest, issued_by, notes: str = "") -> Rental:
    """
    Issue equipment for an approved rental request.

    Requirements:
    1. Lock Equipment row
    2. Verify available_quantity >= requested quantity
    3. Create a Rental record
    4. Reduce Equipment.available_quantity
    5. Prevent duplicate issuance
    6. Save issued_by
    7. Save issued_date
    """
    rental_request = RentalRequest.objects.select_for_update().get(pk=rental_request.pk)

    if rental_request.status != RentalRequest.Status.APPROVED:
        raise InvalidRentalRequestError(_("Only APPROVED requests may be issued."))

    if Rental.objects.filter(rental_request=rental_request).exists():
        raise RequestAlreadyIssuedError(_("Equipment for this request has already been issued."))

    equipment = Equipment.objects.select_for_update().get(pk=rental_request.equipment_id)

    if equipment.available_quantity < rental_request.quantity:
        raise EquipmentUnavailableError(
            _("Cannot issue equipment: only %(available)s units available, but %(requested)s requested.")
            % {
                "available": equipment.available_quantity,
                "requested": rental_request.quantity,
            }
        )

    rental = Rental.objects.create(
        rental_request=rental_request,
        equipment=equipment,
        issued_to=rental_request.requester,
        issued_by=issued_by,
        quantity=rental_request.quantity,
        issued_date=timezone.now().date(),
        expected_return_date=rental_request.expected_return_date,
        status=Rental.Status.ACTIVE,
        notes=notes,
    )

    equipment.available_quantity -= rental_request.quantity
    equipment.save(update_fields=["available_quantity", "updated_at"])

    return rental


class RentalAlreadyReturnedError(Exception):
    """Raised when attempting to return equipment for a rental that's already returned."""



class InvalidRentalStateError(Exception):
    """Raised when attempting to return equipment in an invalid rental state."""


@transaction.atomic
def return_equipment(
    rental: Rental,
    returned_by,
    condition_on_return: str,
    notes: str = "",
) -> None:
    """Return equipment for an ACTIVE rental.

    Business rules:
    - Only ACTIVE rentals may be returned.
    - Prevent duplicate returns.
    - Record condition_on_return, returned_by, and return_date.
    - Increment Equipment.available_quantity.
    - Update Rental status to RETURNED.

    Uses:
    - transaction.atomic
    - select_for_update
    """

    # Lock rental + related equipment to avoid race conditions between concurrent returns.
    rental = Rental.objects.select_for_update().select_related("equipment").get(pk=rental.pk)

    if rental.status != Rental.Status.ACTIVE:
        raise InvalidRentalStateError(
            _("Cannot return equipment: rental is not ACTIVE (Status: %(status)s).")
            % {"status": rental.status}
        )

    # Prevent duplicate returns (OneToOneField already enforces this at DB level,
    # but we validate explicitly for business rule clarity).
    if hasattr(rental, "returns_record"):
        raise RentalAlreadyReturnedError(_("This rental has already been returned."))

    # Also handle case where returns_record relation isn't cached.
    if rental.returns_record.exists():  # type: ignore[attr-defined]
        raise RentalAlreadyReturnedError(_("This rental has already been returned."))

    # Lock equipment row as well (even though select_related fetched it, we need DB lock).
    equipment = Equipment.objects.select_for_update().get(pk=rental.equipment_id)

    # Create return record first, then update inventory + rental state.
    Return = __import__("rentals.models", fromlist=["Return"]).Return  # avoid circular/static reordering
    Return.objects.create(
        rental=rental,
        returned_by=returned_by,
        return_date=timezone.now().date(),
        condition_on_return=condition_on_return,
        notes=notes,
    )

    equipment.available_quantity += rental.quantity
    equipment.save(update_fields=["available_quantity", "updated_at"])

    rental.status = Rental.Status.RETURNED
    rental.save(update_fields=["status", "updated_at"])

