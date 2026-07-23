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
