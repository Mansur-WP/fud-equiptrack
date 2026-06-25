# Deployment hardening task list (Render free + PostgreSQL)

## Implemented
- [x] Added idempotent admin bootstrap command: `accounts/management/commands/ensure_admin.py`
- [x] Created `requirements.txt` (note: versions may need verifying)

## Pending (must complete)
- [ ] Rewrite `config/settings.py` fully for production:
  - [ ] SECRET_KEY / DEBUG / ALLOWED_HOSTS from env
  - [ ] DATABASE_URL -> DATABASES['default'] (PostgreSQL)
  - [ ] WhiteNoise middleware + static storage
  - [ ] Security headers + secure cookies + HTTPS settings
  - [ ] CSRF_TRUSTED_ORIGINS from env
  - [ ] Session/csrf cookie settings
  - [ ] Logging
- [ ] Update `config/urls.py` to stop serving media via `static()` in production
- [ ] Add Render deployment configuration docs (Procfile/commands + env vars)
- [ ] Run verification steps locally (in venv):
  - [ ] `python manage.py check --deploy`
  - [ ] `python manage.py makemigrations` (if needed)
  - [ ] `python manage.py migrate`
  - [ ] `python manage.py collectstatic --noinput`
- [ ] Confirm/clean migrations for custom user model (`accounts.User`)
- [ ] Final checklist gate: only declare ready if all above pass

