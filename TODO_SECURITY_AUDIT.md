# Security Audit Report (Partial / In-Progress)

## Scope Completed
- Environment configuration review is treated as completed already.
- Development vs production settings, SECRET_KEY handling, DEBUG configuration, and README env setup are not revisited.

## 1) File Upload Security
### Upload Fields audited
- `accounts.models.User.profile_image` (`models.ImageField`)
- `equipment.models.Equipment.image` (`models.ImageField`)

### Validators implemented / verified
- `accounts/upload_validation.py`
  - Size limit: `MAX_UPLOAD_SIZE_BYTES = 2 MiB`
  - Extension allowlist: `.jpg/.jpeg/.png/.gif/.webp`
  - MIME hint check: best-effort `content_type.startswith('image/')`
  - Pillow validation:
    - `Image.open(...).verify()`
    - Re-open + `.load()` for decodability
  - Raises `ValidationError` to reject non-images and renamed executables.

### Wired into forms
- `accounts/forms.py`
  - `UserUpdateForm.clean_profile_image()` calls `validate_image_upload(..., field_name="profile_image")`
- `equipment/forms.py`
  - `EquipmentForm.clean_image()` calls `validate_image_upload(..., field_name="image")`

✅ Status: **Fixed / Implemented**

## 2) Image Validation
- Covered by the same validator (`validate_image_upload`) using Pillow `verify()` + re-open.

✅ Status: **Fixed / Implemented**

## 3) Object-Level Permissions (URL-modification resistance)
### Views inspected (partial)
- `accounts/views.py`: profile is scoped to `self.request.user` ✅
- `equipment/views.py`: equipment CRUD uses permission mixins; querysets are not filtered by user (equipment is global) ✅/not applicable
- `rentals/views.py`:
  - Student/staff rentals list/detail filtered by `issued_to=user` ✅
  - Rental request list/detail filtered by `requester=user` (non-admin) ✅
  - Admin actions use `AdminRequiredMixin` ✅

⚠️ Remaining: full matrix for every DetailView/UpdateView/DeleteView/custom view needs confirmation.

## 4) URL Authorization
### Findings
- `accounts/urls.py` endpoints:
  - `admin-dashboard/` protected by `LoginRequiredMixin` + `UserPassesTestMixin` ✅
  - `student-dashboard/` and `staff-dashboard/` are protected only by `LoginRequiredMixin` ❗
    - Any logged-in student/staff could potentially access the other role dashboard.
- `reports/urls.py` placeholder route is unprotected ❗ (future reports may be sensitive)

🛠️ Recommendation (not implemented yet): enforce role checks for the student/staff dashboards and protect reports placeholder.

## 5) XSS Audit
### Templates inspected (partial)
- `templates/accounts/profile.html`
  - Uses `{{ field.help_text|safe }}` ❗
- `templates/accounts/register.html`
  - Uses `{{ field.help_text|safe }}` ❗
- `templates/equipment/equipment_create.html` and `templates/equipment/equipment_update.html`
  - Uses `{{ field.help_text|safe }}` ❗

Risk: `safe` disables auto-escaping. Field `help_text` is typically developer-defined, but should not be marked safe unless it is guaranteed trusted.

🛠️ Recommendation (not implemented yet): remove `|safe` from help text renderings unless proven safe.

## 6) Template Security
- CSRF tokens appear present in form templates (`{% csrf_token %}`) ✅
- Form POST actions appear to rely on default action (current path) ✅

⚠️ Remaining: review all templates for escaping, hidden fields, and sensitive info.

## 7) Security Settings Review
- `config/settings.py` already includes:
  - Secure cookies, HSTS toggles, `SECURE_CONTENT_TYPE_NOSNIFF`, `X_FRAME_OPTIONS = "DENY"`, X-Forwarded proxy settings.

⚠️ Remaining: confirm session/CSRF settings, CSRF trusted origins, and any other recommended production flags.

## 8) Verification
- Attempted `python manage.py check`, but it hangs/interrupts in this environment.

## Files Modified
- `accounts/tests_upload_validation.py` (syntax/format fixes during validator test scaffolding)

## Remaining Work to Reach “Production-Ready After This Audit”
1. Implement fixes for role-based dashboard endpoints (student/staff dashboards).
2. Protect `reports` placeholder route.
3. Remove `|safe` from `field.help_text` in all templates unless there is a trusted reason.
4. Complete XSS audit across all templates.
5. Complete object-level permission audit for every relevant view and custom view.
6. Complete full verification: `python manage.py check` and `python manage.py test`.


