- [ ] Fix Django startup error: missing `AdminRequestManagementListView` in `rentals/views.py` referenced by `rentals/urls.py`.
- [ ] Add `AdminRequestManagementListView` implementation using `annotate_request_management_queryset`.
- [ ] Ensure filters in the view match the template inputs (status, equipment_category, date_from/to, request_id, student_name, equipment_name).
- [ ] Add pagination and template context variables required by `templates/rentals/admin_request_management.html` (status_choices, equipment_categories, query_params).
- [ ] Run `python manage.py runserver` (or `python manage.py check`) to confirm the error is resolved.


