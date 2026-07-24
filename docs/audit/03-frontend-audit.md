# 03 — Frontend Engineering Audit

> **Current-state addendum:** FE-1, FE-3, FE-4, FE-5, FE-8, the category false affordance, and the unused `ChatWidget` finding are resolved. The revenue panel now consumes backend analytics with matching DTOs and recoverable errors. A structured customer tool-call rendering crash was found by new tests and fixed. Vitest/RTL now runs **11 tests across 4 files** covering ErrorBoundary, PrivateRoute, service filtering/retry, and anonymous/authenticated AI chat. TypeScript and production build pass. Remaining gaps are no browser E2E/a11y/visual suite, large admin components, duplicated error parsing, and no dedicated ESLint rule set (Ruff covers Python only).

Stack: React 19 + TypeScript + Vite 6 + Tailwind CSS v4. Verified by direct execution: `npm run build` (`tsc -b && vite build`) succeeds, producing route-level code-split chunks. No ESLint config exists in the repo. No test script exists in `package.json`.

## Structure

- **Pages** (17, `frontend/src/pages/`): Home, Login, Register, Services, ServiceDetails, Staff, BookAppointment, MyBookings, Loyalty, Reviews, Notifications, Profile, Support, Legal, AdminDashboard, NotFound.
- **Components**: root-level (`ChatWidget`, `CustomerDock`, `Footer`, `Layout`, `Navbar`, `PrivateRoute`, `SupportWidget`), `components/landing/*` (10 + barrel), `components/admin/*` (5), `components/ui/*` (4), `components/icons/*` (3).
- **API client**: single Axios instance, `src/api/client.ts` (437 lines), all endpoint modules typed.
- **Routing**: `App.tsx` — most pages lazy-loaded with a shared `Suspense` skeleton fallback.

## Findings table

| ID | Finding | Evidence | Severity | User impact | Engineering impact | Recommended fix | Effort |
|---|---|---|---|---|---|---|---|
| FE-1 | No React ErrorBoundary anywhere in the app | repo-wide search, zero matches | High | Any render-time exception white-screens the entire SPA | Poor resilience, no error telemetry | Add a top-level `ErrorBoundary` with fallback UI | S |
| FE-2 | Zero frontend test infrastructure | no Vitest/Jest/RTL/Playwright config, no `test` script in `package.json` | High | No regression protection for UI logic | Every frontend change is unverified except by manual click-through | Add Vitest + RTL for critical components, Playwright for one e2e booking flow | M |
| FE-3 | Fabricated content shown as real data (rating, stats, testimonials, promo) | `HeroSection.tsx:16`, `AboutSection.tsx:7-12`, `GalleryAndTestimonials.tsx:11-15`, `PromoBanner.tsx:53-60` | Medium-High | Misleads visitors; credibility risk when a technical reviewer reads source | Remove or clearly label fallback content | S |
| FE-4 | Non-functional newsletter forms (two implementations) | `Footer.tsx:64-68`, `LandingFooter.tsx:12-16` — `preventDefault()` only | Medium | Broken feature visible to any user who tries it | Dead UI code | Wire to a real endpoint or remove | S |
| FE-5 | Two duplicate footer components with conflicting brand names | `components/Footer.tsx` ("BloomFlow") vs `components/landing/LandingFooter.tsx` ("Beauty Studio") | Medium | Inconsistent branding undermines "real product" perception | Duplicated markup/maintenance burden | Consolidate to one footer component/brand | S |
| FE-6 | Dead/unused components | `ChatWidget.tsx` (superseded by `SupportWidget.tsx`, never imported), `landing/FinalCta.tsx`, `landing/BookingWidgetSection.tsx` (exported from barrel, never imported anywhere) | Low-Medium | None directly, but inflates bundle/maintenance surface | Confusing for future contributors | Delete dead files | XS |
| FE-7 | Oversized, multi-responsibility components | `AdminDashboard.tsx` (626 lines, contains 3 inline sub-components), `StaffManager.tsx` (621 lines) | Medium | None directly | Harder to test/maintain | Split into per-panel files under `components/admin/` | M |
| FE-8 | `RevenuePanel.tsx` recomputes analytics client-side instead of calling the already-built `analyticsApi.revenue()/.staff()/.service()` endpoints | `RevenuePanel.tsx:19-67`; `api/client.ts:390-436` (endpoints defined but only `.bookings()` is ever called) | Medium | Risk of frontend/backend numbers silently disagreeing over time | Architectural inconsistency | Consume the backend analytics endpoints instead of re-deriving in the client | S |
| FE-9 | Duplicated `extractErrorMessage` error-parsing helper reimplemented in 4+ files | `PromotionsPanel.tsx:9-13`, `StaffManager.tsx:22-26`, `BookAppointment.tsx:35-42`, `Login.tsx:7-21` | Low-Medium | None directly | DRY violation | Extract to a shared `utils/` helper | S |
| FE-10 | Minimal client-side form validation | `Login.tsx`, `Register.tsx` — only HTML5 `required` + password-match check; no schema validation library in dependencies | Low | Users see server-round-trip errors for things that could be caught instantly | — | Consider `zod` + shared schema if investing further | S |
| FE-11 | Service-category icon strip does not actually filter by category | `ServiceCategoryBar.tsx:12-21` — all but one icon link to the generic `/services` route | Low | Minor false affordance | — | Either implement category filtering or remove the implied functionality | S |

## Strengths (verified, worth stating explicitly)

- Real JWT access/refresh flow with automatic 401-retry (`api/client.ts:8-42`), not a stub.
- `PrivateRoute` genuinely checks `user.role`, not just authentication presence (`PrivateRoute.tsx:22-24`), correctly used for `/book`, `/loyalty`, `/support` (customer-only) and `/admin/*` (admin-only) in `App.tsx`.
- Consistent, meaningful `alt` attributes on every `<img>` (verified via repo-wide grep — zero missing); decorative images correctly use `alt=""`.
- No clickable non-semantic `<div>`/`<span>` substituting for buttons found anywhere.
- Strict TypeScript config (`tsconfig.app.json`: `strict`, `noUnusedLocals`, `noUnusedParameters`, `noFallthroughCasesInSwitch`).
- Lean, fully-used dependency tree — no unused packages found.
- Consistent, correctly-implemented loading skeletons and empty states for the majority of data-driven views (`ServicesGrid`, `Services`, `AdminDashboard`, `RevenuePanel`, `BookAppointment`).
- Admin dashboard's appointment counts, revenue breakdown, and booking completion/cancellation rates are genuinely computed from live API data — no hardcoded placeholder numbers found in the admin surfaces (aside from FE-8's architectural duplication concern).
- Skip-link (`Layout.tsx:14`) and focus-visible styling present on most interactive elements — accessibility practices above the average portfolio project.

## Verdict

Frontend engineering is **above-average for a portfolio project** in accessibility, TypeScript rigor, and API-client architecture, but is let down by zero automated test coverage, an absent error boundary, and a pattern of silently substituting fabricated content for missing real data — all fixable without a rewrite.
