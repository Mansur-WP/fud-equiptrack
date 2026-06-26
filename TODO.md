# TODO - Rental lifecycle testing & fixes

- [ ] Add end-to-end rental lifecycle integration tests (Admin create equipment -> Student request -> PENDING -> Admin approve -> issue -> stock decrement -> ACTIVE rental created -> Admin return -> stock increment -> RETURNED status -> returned rentals removed from active list).
- [ ] Add regression tests for:
  - [ ] No duplicate issuance for same RentalRequest
  - [ ] No duplicate returns for same Rental
  - [ ] Stock never goes negative
  - [ ] Returned rentals do not appear in active rentals list
  - [ ] Role-based restrictions on returns (Student/Staff blocked, Admin allowed)
- [ ] Ensure a “process return” workflow exists (view/form/url) and is protected so only ADMIN can return.
- [ ] Fix any failing tests / service bugs (especially in rentals/services.py return_equipment).
- [ ] Confirm Django system check passes: `python manage.py check`.
- [ ] Confirm tests pass: `python manage.py test rentals --verbosity 2`.

