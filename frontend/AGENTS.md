# Frontend – Next.js Bilingual Citizen Portal

## Stack & State

- **Framework**: Next.js 14, `pnpm@10.10.0`
- **Auth**: next-auth v4 (GitHub for dev, UAE PASS sandbox OAuth2/OIDC)
- **i18n**: next.js i18n routing, `en` + `ar`, localeDetection off
- **Style**: water.css + custom `dashboard.css` (body max-width override, status badges, confidence meter, card layout, form label/textarea width fixes)
- **`/api/submit` stub removed** — form now POSTs directly to `NEXT_PUBLIC_API_URL`

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

- All visible strings → `locales/{en,ar}.json` (34 keys each)
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

1. `remarks` — textarea, min 20 chars, required
2. `agreement` — checkbox (deduct up to 20% salary), required
3. Document upload — salary certificate required + optional extras (PDF/JPG/PNG, ≤5 files, ≤15MB each)
4. `applicant_id` — sent from session (`user.id` or `user.email`) as hidden field

**Removed inputs:** `months_delayed`, `overdue_amount`, `current_salary` — values come from database via applicant_id lookup.

All fields have localized labels + help text.

## Submission Flow

1. POST `{NEXT_PUBLIC_API_URL}/api/submit` with multipart FormData: `applicant_id`, `remarks`, `agreement`, `docs`
2. Backend returns `{ application_id, status, explanation, confidence }`
3. Display status + explanation + confidence meter (no raw data)
4. If status = "Additional Information Required", form reappears

## Backend Integration

- `NEXT_PUBLIC_API_URL` env var (default: `http://localhost:8000`)
- CORS whitelisted for frontend origin only
- Status endpoint: `GET {host}/api/applications/{id}`
