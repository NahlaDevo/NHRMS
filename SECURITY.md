# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

Contact the security team at **security@nahrms.com** (placeholder).

Do NOT report security issues via public GitHub issues.

## Security Best Practices

1. Never commit secrets, API keys, or passwords to the repository
2. Use environment variables for all configuration
3. Keep production credentials out of `.env` files — use GitHub Secrets / Render Env Vars
4. Run `python scripts/audit_security.py` before production deployments
5. Ensure ALLOWED_HOSTS and CORS_ORIGINS are properly restricted in production
6. Enable 2FA on all GitHub accounts with write access
7. Rotate secrets and tokens every 90 days
