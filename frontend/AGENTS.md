# Frontend – Next.js Bilingual Citizen Portal

## Framework Quirks & Gotchas

**Next.js 14 specific behaviors:**
- Pages router (not app router) – `pages/` directory
- i18n: locale detection OFF, manual switching via `LangToggle`
- **Critical**: Form posts directly to `NEXT_PUBLIC_API_URL` (no `/api/submit` stub)
- Water.css + custom `dashboard.css` for responsive overrides

## Critical Commands & Setup

```bash
pnpm dev      # http://localhost:3000
pnpm build
pnpm start
```

## Auth Implementation Details

**NextAuth v4 configuration:**
- Pages wrapped in `SessionProvider` (`_app.js`)
- ProtectedRoute redirects → `/login`
- **Critical**: Two login options: GitHub + UAE PASS (sandbox OAuth2/OIDC)
- No JWT sessions, uses OAuth2 state flow

## i18n Implementation

**Arabic/English support:**
- Manual language switching via `LangToggle` component
- Locale from router: `router.locale === 'ar' ? ar : en`
- `_document.js` sets `<html lang>` / `<body dir="rtl">`
- **No automatic locale detection** – manual only

## Critical File Locations

**Key components and their purposes:**
- `pages/index.js:46` → Dashboard with form + status cards
- `pages/login.js:8` → Auth page with GitHub + UAE PASS
- `components/ProtectedRoute.js` → Auth guard wrapper
- `components/LangToggle.js` → EN/AR language switcher

**Critical CSS overrides in `dashboard.css`:**
- Body max-width override for citizen portal UI
- Status badges with color coding
- Confidence meter visual design
- Form layout fixes for mobile responsiveness

## Form Submission Mechanics

**Critical multipart FormData structure:**
```javascript
const formData = new FormData();
formData.append('applicant_id', session.user.id);
formData.append('email_id', session.user.email);
formData.append('months_delayed', 12);
formData.append('overdue_amount', 5000);
formData.append('current_salary', 8000);
formData.append('remarks', 'Hardship reason...');
formData.append('agreement', true);
for (let i = 0; i < files.length; i++) formData.append('docs', files[i]);
```

**Form validation quirks:**
- Remarks: min 20 characters required
- Agreement: checkbox for 20% salary deduction consent
- Files: max 5, ≤15MB each, PDF/JPG/PNG only

## Component Architecture

**Dashboard flow (frontend/pages/index.js:46):**
1. Protected route check via `ProtectedRoute`
2. Status card with confidence meter
3. Form submission with file upload
4. Real-time polling of decisions via `fetchDecisions()` interval
5. Display recent decisions table with toggle

**Auth flow (frontend/pages/login.js:8):**
1. Session check on mount
2. Redirect to `/` if authenticated
3. GitHub + UAE PASS login buttons
4. Locale handling via `router.locale`

**Language toggle (frontend/components/LangToggle.js):**
- Manual locale switching
- Updates `<html lang>` and `<body dir>`
- Updates all visible strings via JSON locale files

## Backend Integration

**Environment configuration:**
- `NEXT_PUBLIC_API_URL` env var (default: `http://localhost:8000`)
- **Critical**: CORS whitelisted for frontend origin only

**API endpoints:**
- Status polling: `GET {host}/api/applications/{id}`
- Decisions endpoint: `GET {host}/api/decisions` — returns full audit trail
  - **Unprotected** — suitable for future admin dashboard page
  - Includes: `loan_amount`, `old_emi`, `new_emi`, `extended_months`, `justification`

**Submission flow:**
1. POST `{NEXT_PUBLIC_API_URL}/api/submit` with multipart FormData
2. Backend returns `{ application_id, status, explanation, confidence }`
3. Display status + explanation + confidence meter
4. If status = "Additional Information Required", form reappears

## Environment Setup

**Create `frontend/.env.local` (committed, dev-only):**

```env
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
NEXTAUTH_SECRET=...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Framework-Specific Quirks

**Next.js 14 implementation specifics:**
- Uses `pnpm@10.10.0` (not npm)
- No app router – uses pages router
- i18n routing disabled – manual switching only
- FormData posted directly to backend (no API proxy)
- Water.css base theme with custom dashboard.css overrides
- Protected routes via SessionProvider wrapper
- Real-time decisions polling with 30-second intervals
