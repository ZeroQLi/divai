# Frontend – Next.js Bilingual Citizen Portal

## Stack & State

- **Framework**: Next.js 14, `pnpm@10.10.0`
- **Auth**: next-auth v4 (GitHub for dev, UAE PASS sandbox OAuth2/OIDC)
- **i18n**: next.js i18n routing, `en` + `ar`, localeDetection off
- **Style**: water.css + custom `dashboard.css` (body max-width override, status badges, confidence meter, card layout, form label/textarea width fixes)
- **`/api/submit` stub removed** — form now POSTs directly to `NEXT_PUBLIC_API_URL`

## Environment

Create `frontend/.env.local` (committed, dev-only):

```env
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
NEXTAUTH_SECRET=...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Commands

```bash
pnpm dev      # http://localhost:3000
pnpm build
pnpm start
```

## Auth & Routing

- Pages wrapped in `SessionProvider` (`_app.js`)
- `ProtectedRoute` redirects unauthenticated → `/login`
- Login page: GitHub + UAE PASS buttons
- `next-auth` config at `pages/api/auth/[...nextauth].js`

## i18n

- All visible strings → `locales/{en,ar}.json` (37 keys each)
- `_document.js` sets `<html lang>` / `<body dir>` from Next.js i18n
- `LangToggle` component on every page

## Pages & Components

| File | Purpose |
|---|---|
| `pages/login.js` | Auth page, EN/AR |
| `pages/index.js` | Dashboard (protected): status card, confidence meter, rescheduling form, file upload |
| `pages/api/auth/[...nextauth].js` | NextAuth config |
| `styles/dashboard.css` | Dashboard CSS (body max-width override, status badges, confidence bar, cards, form) |
| `components/ProtectedRoute.js` | Auth guard |
| `components/LangToggle.js` | EN/AR toggle |

## Form Fields (rescheduling request)

1. `months_delayed` — number input, min 1, required
2. `overdue_amount` — number input (AED), min 0, required
3. `current_salary` — number input (AED), min 0, required
4. `remarks` — textarea, min 20 chars, required
5. `agreement` — checkbox (deduct up to 20% salary), required
6. Document upload — PDF/JPG/PNG, ≤5 files, ≤15MB each, required
7. `applicant_id` + `email_id` — sent from session as hidden fields

## Submission Flow

1. POST `{NEXT_PUBLIC_API_URL}/api/submit` with multipart FormData: `applicant_id`, `email_id`, `months_delayed`, `overdue_amount`, `current_salary`, `remarks`, `agreement`, `docs`
2. Backend returns `{ application_id, status, explanation, confidence }`
3. Display status + explanation + confidence meter
4. If status = "Additional Information Required", form reappears

## Backend Integration

- `NEXT_PUBLIC_API_URL` env var (default: `http://localhost:8000`)
- CORS whitelisted for frontend origin only
- Status endpoint: `GET {host}/api/applications/{id}`
- Decisions endpoint: `GET {host}/api/decisions` — returns full audit trail (`loan_amount`, `old_emi`, `new_emi`, `extended_months`, `justification`, etc.). **Unprotected — suitable for a future admin dashboard page.**
