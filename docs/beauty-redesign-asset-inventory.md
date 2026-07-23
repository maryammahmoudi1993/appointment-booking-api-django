# Beauty redesign asset inventory

The website uses optimized derivatives of the supplied reference imagery. Original assets are preserved. Landing-page components use the `*-clean.webp` and `*-clean.png` siblings where a source contained a baked checkerboard or incorrect crop.

## Landing-page clean derivatives

| Clean asset | Correct mapping | Processing |
|---|---|---|
| `icon-book-online-clean.webp` | 3D calendar | Tight center crop removes checkerboard perimeter |
| `icon-hair-styling-clean.webp` | 3D scissors | Tight center crop removes checkerboard perimeter |
| `icon-facial-care-clean.webp` | 3D cream jar | Tight center crop removes checkerboard perimeter |
| `icon-nail-polish-clean.webp` | 3D nail polish | Tight center crop removes checkerboard perimeter |
| `icon-makeup-clean.webp` | 3D lipstick and brush | Tight center crop removes checkerboard perimeter |
| `icon-skin-care-clean.webp` | 3D skincare jar | Tight center crop removes checkerboard perimeter |
| `icon-spa-relax-clean.webp` | 3D lotus | Tight center crop removes checkerboard perimeter and source caption |
| `icon-all-services-clean.webp` | 3D makeup palette | Tight center crop removes checkerboard perimeter |
| `feature-skilled-team-clean.webp` | 3D salon team | Tight crop removes checkerboard and source caption |
| `feature-hygiene-clean.webp` | 3D shield | Tight crop removes checkerboard and source caption |
| `feature-products-clean.webp` | 3D product jar | Tight crop removes checkerboard and source caption |
| `botanical-branch-clean.png` | Decorative leaf branch | Checkerboard extracted to alpha |
| `decorative-flower-clean.png` | Decorative flower | Checkerboard extracted to alpha |

| Asset | Content and mapping | Dimensions | Ratio | Alpha / checkerboard | Loading and crop |
|---|---|---:|---:|---|---|
| `hero-character.webp` | Illustrated salon client; landing hero | 760×943 | 0.81 | Opaque; clean | Eager, portrait containment |
| `botanical-branch.webp` | Blush botanical branch; page heroes and section corners | 600×327 | 1.83 | Opaque; clean | Decorative, CSS-positioned |
| `decorative-flower.webp` | Large blush flower; landing decoration | 600×327 | 1.83 | Opaque; clean | Decorative, CSS-positioned |
| `promo-products.webp` | Gift and beauty products; promotion banner | 600×502 | 1.20 | Opaque; clean | Lazy, contained |
| `service-facial.webp` | Facial treatment scene; facial service cards/details | 700×700 | 1.00 | Opaque; clean | Lazy below fold, cover crop |
| `service-hair.webp` | Hair styling scene; hair service cards/details | 700×700 | 1.00 | Opaque; clean | Lazy below fold, cover crop |
| `service-manicure.webp` | Manicure scene; nail service cards/details | 700×700 | 1.00 | Opaque; clean | Lazy below fold, cover crop |
| `service-massage.webp` | Massage scene; spa service cards/details | 700×700 | 1.00 | Opaque; clean | Lazy below fold, cover crop |
| `icon-book-online.webp` | 3D calendar; booking category/date step | 256×256 | 1.00 | Opaque; clean | Eager only in above-fold category strip |
| `icon-hair-styling.webp` | 3D scissors; hair category | 256×256 | 1.00 | Opaque; clean | Contained in raised tile |
| `icon-facial-care.webp` | 3D cream jar; facial category | 256×256 | 1.00 | Opaque; clean | Contained in raised tile |
| `icon-nail-polish.webp` | 3D nail polish; nail category | 256×256 | 1.00 | Opaque; clean | Contained in raised tile |
| `icon-makeup.webp` | 3D makeup palette; makeup/all-services category | 256×256 | 1.00 | Opaque; clean | Contained in raised tile |
| `icon-skin-care.webp` | 3D skincare jar; skincare category | 256×256 | 1.00 | Opaque; clean | Contained in raised tile |
| `icon-spa-relax.webp` | 3D spa object; spa category | 256×210 | 1.22 | Opaque; clean | `object-fit: contain` |
| `feature-skilled-team.webp` | 3D people; skilled-team benefit | 320×262 | 1.22 | Opaque; clean | Lazy, contained |
| `feature-hygiene.webp` | 3D shield; hygiene benefit | 320×262 | 1.22 | Opaque; clean | Lazy, contained |
| `feature-products.webp` | 3D product; premium-products benefit | 320×262 | 1.22 | Opaque; clean | Lazy, contained |
| `avatar-1.webp`…`avatar-4.webp` | Client/staff portraits; social proof and reviews | 200×200 | 1.00 | Opaque; clean | Lazy outside hero, circular crop |

## Source reference mapping

- Landing composition reference: proportions, soft peach canvas, serif/sans pairing, raised category rail, benefit grid, service cards, booking steps, offer, testimonials, and dusty-rose footer.
- Salon interior and product still lifes: palette, material, lighting, and surface reference.
- Mobile booking screenshots: progress flow, calendar/time selection, booking review, confirmation, bookings, loyalty, and profile hierarchy.
- Dashboard screenshot: practical card density and dusty-rose admin navigation reference.
- Uploaded icon sheets: source of the 3D service-category visual language. The project derivatives use matching solid backgrounds, so no baked checkerboard is visible.

The larger uploaded originals remain external references rather than runtime payloads; the compact derivatives prevent multi-megabyte downloads and layout shifts.
