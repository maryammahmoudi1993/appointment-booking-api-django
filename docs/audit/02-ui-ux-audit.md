# 02 — UI/UX Audit

> **Current-state addendum:** The detailed baseline below is retained for traceability, but fabricated marketing content, newsletter dead ends, inconsistent footer branding/placeholders, cosmetic category links, and cancellation-window friction are resolved. Category cards now open active service filters. No reference images were supplied, and the required browser runtime failed initialization, so pixel similarity and seven-viewport results remain **Not verified**. The missing transformation gallery remains optional portfolio scope.

## Method and limitation (read first)

No reference design images and no screenshots of the current implementation were attached to this conversation, and no browser/screenshot tool was available in this environment. **Phase 3's pixel-level comparison at 7 viewport sizes could not be performed** and every "similarity %" that would require a reference image is marked **Not Verified**. What follows instead is a structural, evidence-based audit of the actual landing-page source code (`frontend/src/pages/Home.tsx` and `frontend/src/components/landing/*`), which is enough to determine section existence, data authenticity, and code-level accessibility/responsiveness — the parts of Phase 3/4 that don't require a rendered screenshot.

## Landing page section inventory

`Home.tsx` composes: `HeroSection → ServiceCategoryBar → WhyChooseUs → ServicesGrid → AboutSection → HowItWorks → PromoBanner → GalleryAndTestimonials`, each wrapped in a real IntersectionObserver-based reveal animation (`components/ui/Reveal.tsx`).

| # | Section | Exists | Data source | Status | Evidence |
|---|---|---|---|---|---|
| 1 | Header/nav | Y | Static links | Fully implemented | `LandingHeader.tsx:6-12`. Minor bug: "Prices" and "Services" nav links both point to `#services` (duplicate target). |
| 2 | Hero | Y | Mixed | **Partially implemented / misleading fallback** | `HeroSection.tsx:16` hardcodes `{ average: 4.9, count: 1000 }` shown until (or unless) a real reviews API call succeeds — a fabricated rating number is the default state a visitor sees. |
| 3 | Primary/secondary CTAs | Y | Dynamic, role-aware | Fully implemented | `HeroSection.tsx:17,39-40` branches booking target on `user?.role`. |
| 4 | Customer ratings/avatars | Y | Avatars are static stock images; rating is semi-dynamic (see row 2) | Partially implemented | `HeroSection.tsx:7-12,42-50`. Avatars correctly use `alt=""` (decorative). |
| 5 | Hero illustration | Y | Static image, real descriptive alt text | Fully implemented | `HeroSection.tsx:56-66` |
| 6 | Decorative shapes/botanical assets | Y | Static images, correctly `alt=""` | Fully implemented | `HeroSection.tsx:64` |
| 7 | Service-category icon strip | Y | 100% hardcoded, not backed by a real category taxonomy | Hardcoded / cosmetic | `ServiceCategoryBar.tsx:12-21`. All but one category link to the same generic `/services` route — clicking "Facial Care" does not filter to facials. |
| 8 | Why Choose Us | Y | 100% hardcoded copy | Hardcoded (acceptable for marketing copy) | `WhyChooseUs.tsx:8-33` |
| 9 | Featured services | Y | **Real API data** (`servicesApi.list()`), proper skeleton + empty state | Fully implemented | `ServicesGrid.tsx:8-15,28-36,82-86` — one of the strongest sections in the codebase |
| 10 | About section | Y | Copy + "500+ clients / 15+ stylists / 50+ treatments / 4.9 rating" stats — **all fabricated, no API backing** | Hardcoded, presented as fact | `AboutSection.tsx:7-12,26-30` |
| 11 | Booking steps | Y | 100% hardcoded (3 steps) | Hardcoded (acceptable) | `HowItWorks.tsx:6-10` |
| 12 | Phone booking mockup | Y | Fully fabricated example booking ("Jessica", "$79.00", "Sat 18 May 2026") hardcoded in JSX | Visually mocked, non-interactive | `HowItWorks.tsx:32-49` |
| 13 | Special offer | Y | Real API call with a **misleading hardcoded fallback** | Partially implemented / risk of false advertising | `PromoBanner.tsx:16-24,43-61` — fallback "15% OFF" banner shown when no real promo is active; the booking flow requires a real, validating promo code (`client.ts:348-353`), so a visitor following the fallback banner has nothing to redeem. |
| 14 | Testimonials | Y | Real API call with **fabricated fallback reviews indistinguishable from real ones** | Partially implemented / fake social proof | `GalleryAndTestimonials.tsx:11-15,20-26` — 3 named fake reviewers ("Aisha K.", "Sophia M.", "Priya T.") shown on empty/failed fetch. |
| 15 | Transformations/portfolio gallery | **N — missing** | — | Missing | No before/after gallery or image carousel exists anywhere in `components/landing/`. The component `GalleryAndTestimonials` contains only testimonials — the name is misleading. |
| 16 | Footer | Y | Static, plus two competing implementations | Partially implemented, inconsistent | Two footer components exist: `components/Footer.tsx` (brand: "BloomFlow") and `components/landing/LandingFooter.tsx` (brand: "Beauty Studio") — inconsistent product naming across the same app. |
| 17 | Newsletter | Y (form exists) | **Non-functional** — `preventDefault()` only, no submit logic, no API call | Broken / decorative | `LandingFooter.tsx:12-16`, `Footer.tsx:64-68` |
| 18 | Mobile navigation | Y | Real hamburger menu with `aria-expanded`/`aria-controls`, Escape-to-close | Fully implemented | `LandingHeader.tsx:20-25,42-55` |
| 19 | Responsive layouts | Not verified (no rendered browser) | — | Not verified | Tailwind responsive classes are present throughout, but actual rendered behavior at the 7 requested viewports was not tested. |
| 20 | Motion/interactions | Partially verified | Real `IntersectionObserver` reveal-on-scroll | Fully implemented (code-level); rendered smoothness not verified | `components/ui/Reveal.tsx:13-28` |

## UX friction list

| Journey step | Problem | User impact | Severity | Recommended correction | Acceptance test |
|---|---|---|---|---|---|
| Landing page load | Fake 4.9★/1000-reviews and "500+ clients" stats shown as fact | Erodes trust once discovered; misleading for a portfolio demo being shown to a client who reads the code | P1 | Either wire to real aggregate review data or clearly label as illustrative placeholder content | Rating/stats only render when backed by a real query, or copy explicitly says "sample data" |
| Special offer banner | Hardcoded "15% OFF" fallback with no real backing code | A customer can follow a CTA promising a discount that fails validation at checkout | P1 | Only render the promo banner when a real active `PromoCode` exists; remove the hardcoded fallback | Banner absent when `promotionsApi.list()` returns no active promos |
| Newsletter signup | Form submits nothing | Visible, testable dead end — a reviewer clicking "Subscribe" gets silent failure | P2 | Wire to a real endpoint or remove the form | Submitting shows a real success/error state |
| Whole app | No React ErrorBoundary anywhere | A single unexpected API payload shape can white-screen the entire SPA with no recovery UI | P1 | Add a top-level ErrorBoundary with a friendly fallback and reload action | Simulated render error shows fallback UI, not blank screen |
| Booking cancellation | No minimum-notice window enforced (see backend audit) | Customers can cancel/reschedule seconds before an appointment, undermining the business "management" value proposition | P2 | Enforce `BusinessSettings.cancellation_window_hours` (already modeled, currently unused) | Attempting to cancel inside the window returns a clear error |
| First-time visitor | Product name inconsistency ("BloomFlow" in app chrome vs "Beauty Studio" on the landing page) | Undermines "real SaaS product" perception for a technical reviewer | P2 | Pick one brand name and apply consistently | Grep for both strings returns only one brand across the codebase |

## Direct answers to the UX audit questions

- **Can a new visitor understand the product within 5 seconds?** Likely yes at a glance (hero headline + CTA are clear in code), but **not independently verified** without a rendered screenshot.
- **Can a customer complete a booking without confusion?** The booking flow (`BookAppointment.tsx`, 4-step wizard) is real, API-backed, and covered by backend tests. Not verified in a live browser, but the code path is coherent and has empty/loading/error states.
- **Are there any dead ends / buttons that look functional but aren't?** Yes — the newsletter forms in both footers, and the "15% OFF" fallback promo banner functionally misleads.
- **Is the mobile experience production-quality?** Not verified (no rendered browser testing performed); code shows responsive classes and a working mobile nav, but actual behavior at 390×844 etc. is unconfirmed.
- **Does the design feel like a real SaaS product or a static mockup?** Closer to a real SaaS product than a mockup — real API wiring for services/promos/reviews/admin dashboard — but the fabricated fallback content (testimonials, stats, ratings) reintroduces a "mockup" feel once inspected closely.
- **What prevents the experience from feeling premium?** The mixed brand name, the fabricated-but-undisclosed placeholder content, and the non-functional newsletter form are the main credibility risks; the underlying component/accessibility engineering is actually above-average.
