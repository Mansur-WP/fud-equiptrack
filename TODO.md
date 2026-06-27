# TODO

## Dashboard audit + live database queries
- [ ] Audit admin dashboard template for KPI placeholders.
- [ ] Audit admin dashboard view (AdminDashboardPlaceholderView) for incorrect/non-live placeholders.
- [ ] Implement required KPI counts:
  - [ ] Pending Requests = RentalRequest(status=PENDING)
  - [ ] Approved Requests (not yet issued) = RentalRequest(status=APPROVED) AND no related Rental exists
  - [ ] Equipment Awaiting Issuance = Approved requests waiting for issuance (same as above unless business rules differ)
  - [ ] Active Rentals = Rental(status=ACTIVE)
  - [ ] Returned Rentals = Rental(status=RETURNED)
- [ ] Replace placeholders with live queries in dashboard context.
- [ ] Implement Recent sections:
  - [ ] Recent Requests = latest RentalRequest rows
  - [ ] Recent Rentals = latest Rental issued (Rental ordered by issued_date/created_at)
  - [ ] Recent Returns = latest Rental returns (Rental(status=RETURNED) or Return rows)
- [ ] Optimize queries using select_related/prefetch_related/annotate/aggregate where appropriate.
- [ ] Update Administrator Dashboard template to render the required cards + tables.
- [ ] Run: python manage.py check
- [ ] Verify dashboard numbers match database records.
