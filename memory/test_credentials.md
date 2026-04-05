# Test Credentials for My-AlphaAI

## User Accounts
| Role | Email | Password | Notes |
|------|-------|----------|-------|
| Admin (Elite) | mar-brick@hotmail.com | Martin2026! | Full admin access, admin_key: alphaai_admin_2026 |
| Pro User | demo_test2@my-alpha-ai.com | NewPass1234! | Referral code: KLYYBMTS |
| Free User | test_free_user_iter29@my-alpha-ai.com | TestPass123! | Basic tier |

## App URL
- Preview: https://signal-ui-latest.preview.emergentagent.com

## API Auth
- Login: POST /api/auth/login with {"email": "...", "password": "..."}
- Token field in response: `access_token`
- localStorage key: `alphaai_tokens` (JSON with access_token + refresh_token)

## Admin Access
- Admin key for admin endpoints: `alphaai_admin_2026`
- Stripe test key: `sk_test_emergent` (via Emergent proxy)
