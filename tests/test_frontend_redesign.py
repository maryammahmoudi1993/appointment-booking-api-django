"""Static smoke coverage for the customer-facing React route and asset contract."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend" / "src"


def test_customer_routes_are_registered():
    app = (FRONTEND / "App.tsx").read_text(encoding="utf-8")
    for route in (
        "/services/:id",
        "/book",
        "/my-bookings",
        "/loyalty",
        "/reviews",
        "/notifications",
        "/profile",
        "/support",
    ):
        assert f'path="{route}"' in app


def test_reference_asset_derivatives_exist_and_are_compact():
    asset_dir = FRONTEND / "assets" / "landing"
    required = (
        "hero-character.webp",
        "icon-book-online.webp",
        "icon-hair-styling.webp",
        "icon-facial-care.webp",
        "icon-nail-polish.webp",
        "icon-makeup.webp",
        "icon-skin-care.webp",
        "icon-spa-relax.webp",
        "service-facial.webp",
        "service-hair.webp",
        "service-manicure.webp",
        "service-massage.webp",
    )
    for filename in required:
        asset = asset_dir / filename
        assert asset.is_file(), f"Missing redesign asset: {filename}"
        assert asset.stat().st_size < 250_000, f"Unoptimized redesign asset: {filename}"


def test_design_system_includes_accessible_states():
    css = (FRONTEND / "index.css").read_text(encoding="utf-8")
    for token in (
        "--color-surface",
        "--color-rose",
        "--color-gold",
        ".beauty-card",
        ".beauty-input",
        ".beauty-toggle",
        ".skip-link",
        ":focus-visible",
        "prefers-reduced-motion",
    ):
        assert token in css


def test_landing_page_ctas_and_sections_are_wired():
    home = (FRONTEND / "pages" / "Home.tsx").read_text(encoding="utf-8")
    header = (
        FRONTEND / "components" / "landing" / "LandingHeader.tsx"
    ).read_text(encoding="utf-8")
    hero = (
        FRONTEND / "components" / "landing" / "HeroSection.tsx"
    ).read_text(encoding="utf-8")
    sections = " ".join(
        path.read_text(encoding="utf-8")
        for path in (FRONTEND / "components" / "landing").glob("*.tsx")
    )

    assert "LandingHeader" not in home  # Layout owns the route-specific header.
    assert 'href: "#home"' in header
    assert 'href: "#services"' in header
    assert 'href: "#about"' in header
    assert 'href: "#reviews"' in header
    assert "bookingTarget" in hero
    assert 'href="#services"' in hero
    for section_id in ('id="home"', 'id="services"', 'id="about"', 'id="reviews"'):
        assert section_id in sections


def test_landing_uses_clean_icon_derivatives_without_removing_sources():
    asset_dir = FRONTEND / "assets" / "landing"
    clean_assets = (
        "icon-book-online-clean.webp",
        "icon-hair-styling-clean.webp",
        "icon-facial-care-clean.webp",
        "icon-nail-polish-clean.webp",
        "icon-makeup-clean.webp",
        "icon-skin-care-clean.webp",
        "icon-spa-relax-clean.webp",
        "icon-all-services-clean.webp",
        "botanical-branch-clean.png",
        "decorative-flower-clean.png",
    )
    for filename in clean_assets:
        assert (asset_dir / filename).is_file()

    # The original project files remain available as requested.
    for filename in (
        "icon-book-online.webp",
        "icon-hair-styling.webp",
        "botanical-branch.webp",
        "decorative-flower.webp",
    ):
        assert (asset_dir / filename).is_file()
