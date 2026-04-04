"""
SnapAI — PDF Generator (Pure Python, zero system dependencies)

Generates the contractor-facing PDF estimate using a hand-written PDF writer.
No WeasyPrint, no Cairo, no Pango — works in any Python environment.

Falls back gracefully to WeasyPrint if it happens to be available.
"""

import io
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# ──────────────────────────────────────────────────────────────────────────────
# Pure-Python PDF Writer
# Generates valid PDF 1.4 output using only Python stdlib (io, struct, etc.)
# ──────────────────────────────────────────────────────────────────────────────

class _PdfWriter:
    """
    Minimal PDF 1.4 writer. Supports text, lines, rectangles, and colors.
    Uses built-in Helvetica/Helvetica-Bold fonts (always available in PDF readers).
    Coordinate system: origin bottom-left, y increases upward.
    We flip to top-left internally by subtracting from page height.
    """
    PAGE_W = 612   # US Letter width in points (8.5 in × 72)
    PAGE_H = 792   # US Letter height in points (11 in × 72)

    # Colors (r, g, b) — 0.0-1.0
    GREEN       = (0.102, 0.529, 0.329)  # #1a8754
    GREEN_DARK  = (0.059, 0.361, 0.220)  # #0f5c38
    ORANGE      = (0.769, 0.376, 0.039)  # #c4600a
    RED         = (0.776, 0.157, 0.157)  # #c62828
    BLUE        = (0.086, 0.396, 0.753)  # #1565c0
    GRAY        = (0.420, 0.420, 0.400)  # #6b6b66
    LIGHT_GRAY  = (0.878, 0.867, 0.835)  # #e0ddd5
    BLACK       = (0.098, 0.098, 0.094)  # #1a1a18
    WHITE       = (1.0,   1.0,   1.0)

    def __init__(self):
        self._objects       = []   # list of (obj_id, bytes)
        self._pages         = []   # list of page obj_ids
        self._obj_id        = 1
        self._buf           = None  # current page content buffer
        self._images        = {}    # name -> (obj_id, pixel_w, pixel_h)
        self._cur_page_imgs = []    # image names used on the current page

    # ── Object helpers ────────────────────────────────────────────────────────

    def _new_obj(self) -> int:
        oid = self._obj_id
        self._obj_id += 1
        return oid

    def _add_obj(self, oid: int, content: str):
        self._objects.append((oid, content.encode("latin-1", errors="replace")))

    def _esc(self, s: str) -> str:
        """Escape a string for use inside PDF string literals (Latin-1 safe)."""
        # Replace common Unicode chars that don't exist in Latin-1
        replacements = {
            "\u2014": "-",   # em dash -> hyphen
            "\u2013": "-",   # en dash -> hyphen
            "\u2019": "'",   # right single quote
            "\u2018": "'",   # left single quote
            "\u201c": '"',   # left double quote
            "\u201d": '"',   # right double quote
            "\u2022": "*",   # bullet
            "\u2605": "*",   # black star -> asterisk
            "\u2606": "*",   # white star -> asterisk
            "\u00b7": ".",   # middle dot
            "\u00a0": " ",   # non-breaking space
            "\u2026": "...", # ellipsis
        }
        for uni, asc in replacements.items():
            s = s.replace(uni, asc)
        # Drop any remaining non-latin-1 chars
        s = s.encode("latin-1", errors="replace").decode("latin-1")
        return (
            s.replace("\\", "\\\\")
             .replace("(", "\\(")
             .replace(")", "\\)")
             .replace("\n", "\\n")
             .replace("\r", "\\r")
        )

    # ── Page management ───────────────────────────────────────────────────────

    def new_page(self):
        """Start a new page. Flush any previous page first."""
        self._buf = io.StringIO()
        self._cur_y = self.PAGE_H  # tracks current y for next_line()
        self._cur_page_imgs = []   # reset image list for this page

    def _flush_page(self):
        """Finalize the current page and add it to the PDF."""
        stream = self._buf.getvalue().encode("latin-1", errors="replace")
        # Content stream object
        cs_id = self._new_obj()
        cs_bytes = (
            f"{cs_id} 0 obj\n"
            f"<< /Length {len(stream)} >>\n"
            "stream\n"
        ).encode("latin-1") + stream + b"\nendstream\nendobj\n"
        self._objects.append((cs_id, cs_bytes[cs_bytes.index(b"obj\n")+4:]))
        # Rewrite as raw - store pre-serialized
        self._objects[-1] = (cs_id, cs_bytes)

        # XObject (image) resources for this page
        xobj_str = ""
        if self._cur_page_imgs:
            entries = " ".join(
                f"/{n} {self._images[n][0]} 0 R" for n in self._cur_page_imgs
            )
            xobj_str = f" /XObject << {entries} >>"

        # Page object
        pg_id = self._new_obj()
        page_obj = (
            f"{pg_id} 0 obj\n"
            f"<< /Type /Page\n"
            f"   /MediaBox [0 0 {self.PAGE_W} {self.PAGE_H}]\n"
            f"   /Contents {cs_id} 0 R\n"
            f"   /Resources << /Font << "
            f"/F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> "
            f"/F2 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >> "
            f"/F3 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique >> "
            f">>{xobj_str} >> >>\n"
            "endobj\n"
        )
        self._objects.append((pg_id, page_obj.encode("latin-1")))
        self._pages.append(pg_id)
        self._buf = None

    # ── Drawing primitives (coordinates: top-left origin) ─────────────────────

    def _y(self, y_top: float) -> float:
        """Convert top-left y to PDF bottom-left y."""
        return self.PAGE_H - y_top

    def rect_fill(self, x: float, y: float, w: float, h: float, color):
        r, g, b = color
        self._buf.write(
            f"{r:.3f} {g:.3f} {b:.3f} rg\n"
            f"{x:.2f} {self._y(y+h):.2f} {w:.2f} {h:.2f} re f\n"
        )

    def rect_stroke(self, x: float, y: float, w: float, h: float, color, lw: float = 0.5):
        r, g, b = color
        self._buf.write(
            f"{lw:.2f} w\n"
            f"{r:.3f} {g:.3f} {b:.3f} RG\n"
            f"{x:.2f} {self._y(y+h):.2f} {w:.2f} {h:.2f} re S\n"
        )

    def line(self, x1, y1, x2, y2, color, lw: float = 0.5):
        r, g, b = color
        self._buf.write(
            f"{lw:.2f} w\n"
            f"{r:.3f} {g:.3f} {b:.3f} RG\n"
            f"{x1:.2f} {self._y(y1):.2f} m {x2:.2f} {self._y(y2):.2f} l S\n"
        )

    def add_jpeg_image(self, jpeg_bytes: bytes, width: int, height: int) -> str:
        """
        Embed a JPEG image in the PDF and return its resource name (e.g. 'Im0').
        PDF readers support JPEG natively via /DCTDecode — no re-encoding needed.
        """
        name   = f"Im{len(self._images)}"
        img_id = self._new_obj()
        header = (
            f"{img_id} 0 obj\n"
            f"<< /Type /XObject /Subtype /Image\n"
            f"   /Width {width} /Height {height}\n"
            f"   /ColorSpace /DeviceRGB\n"
            f"   /BitsPerComponent 8\n"
            f"   /Filter /DCTDecode\n"
            f"   /Length {len(jpeg_bytes)}\n"
            f">>\nstream\n"
        ).encode("latin-1")
        raw = header + jpeg_bytes + b"\nendstream\nendobj\n"
        self._objects.append((img_id, raw))
        self._images[name] = (img_id, width, height)
        return name

    def draw_image(self, x: float, y: float, w: float, h: float, name: str):
        """
        Draw a previously-added image at screen position (x, y) with display size (w×h).
        y is the TOP of the image in screen (top-left origin) coordinates.
        """
        if name not in self._cur_page_imgs:
            self._cur_page_imgs.append(name)
        # PDF transform matrix: [sx 0 0 sy tx ty] cm
        # where ty = bottom-left y in PDF (bottom-left origin) space
        y_bottom = self._y(y + h)
        self._buf.write(
            f"q\n"
            f"{w:.2f} 0 0 {h:.2f} {x:.2f} {y_bottom:.2f} cm\n"
            f"/{name} Do\n"
            f"Q\n"
        )

    def text(self, x: float, y: float, s: str, size: float = 10,
             color=None, bold: bool = False, italic: bool = False):
        """Draw text at position (x, y) where y is from top of page."""
        if not s:
            return
        if color is None:
            color = self.BLACK
        r, g, b = color
        font = "F2" if bold else ("F3" if italic else "F1")
        escaped = self._esc(str(s))
        self._buf.write(
            f"BT\n"
            f"/{font} {size:.1f} Tf\n"
            f"{r:.3f} {g:.3f} {b:.3f} rg\n"
            f"{x:.2f} {self._y(y):.2f} Td\n"
            f"({escaped}) Tj\n"
            "ET\n"
        )

    def text_right(self, x_right: float, y: float, s: str, size: float = 10,
                   color=None, bold: bool = False):
        """Draw right-aligned text ending at x_right."""
        if not s:
            return
        # Approximate character width (Helvetica avg ~0.55 × size)
        approx_w = len(str(s)) * size * 0.52
        x = x_right - approx_w
        self.text(x, y, s, size=size, color=color, bold=bold)

    def multiline_text(self, x: float, y: float, s: str, size: float = 10,
                       max_width: float = 400, line_height: float = 14,
                       color=None, bold: bool = False) -> float:
        """Draw wrapped text. Returns new y after last line."""
        words = str(s).split()
        lines, cur = [], []
        for w in words:
            cur.append(w)
            # rough width estimate
            if len(" ".join(cur)) * size * 0.52 > max_width:
                if len(cur) > 1:
                    lines.append(" ".join(cur[:-1]))
                    cur = [w]
                else:
                    lines.append(" ".join(cur))
                    cur = []
        if cur:
            lines.append(" ".join(cur))
        for line in lines:
            self.text(x, y, line, size=size, color=color, bold=bold)
            y += line_height
        return y

    # ── Serialization ─────────────────────────────────────────────────────────

    def save(self, path: str):
        """Finalize and write the PDF to disk."""
        if self._buf is not None:
            self._flush_page()

        buf = io.BytesIO()
        buf.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

        offsets = {}
        for oid, raw in self._objects:
            offsets[oid] = buf.tell()
            if raw.startswith(f"{oid} 0 obj".encode()):
                buf.write(raw)
            else:
                buf.write(f"{oid} 0 obj\n".encode() + raw + b"\nendobj\n")

        # Pages tree
        pages_id = self._new_obj()
        kids = " ".join(f"{p} 0 R" for p in self._pages)
        pages_obj = (
            f"{pages_id} 0 obj\n"
            f"<< /Type /Pages /Kids [{kids}] /Count {len(self._pages)} >>\n"
            "endobj\n"
        ).encode("latin-1")
        offsets[pages_id] = buf.tell()
        buf.write(pages_obj)

        # Update each page's Parent reference (simple approach: re-add as dict inline)
        # (We'll reference pages tree in catalog instead)

        # Catalog
        cat_id = self._new_obj()
        cat_obj = (
            f"{cat_id} 0 obj\n"
            f"<< /Type /Catalog /Pages {pages_id} 0 R >>\n"
            "endobj\n"
        ).encode("latin-1")
        offsets[cat_id] = buf.tell()
        buf.write(cat_obj)

        # Cross-reference table
        xref_pos = buf.tell()
        all_ids = sorted(offsets.keys())
        buf.write(f"xref\n0 {max(all_ids)+1}\n".encode())
        buf.write(b"0000000000 65535 f \n")
        for i in range(1, max(all_ids) + 1):
            if i in offsets:
                buf.write(f"{offsets[i]:010d} 00000 n \n".encode())
            else:
                buf.write(b"0000000000 65535 f \n")

        buf.write(
            f"trailer\n<< /Size {max(all_ids)+1} /Root {cat_id} 0 R >>\n"
            f"startxref\n{xref_pos}\n%%EOF\n".encode()
        )

        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        with open(path, "wb") as f:
            f.write(buf.getvalue())


# ──────────────────────────────────────────────────────────────────────────────
# Estimate-specific layout helpers
# ──────────────────────────────────────────────────────────────────────────────

def _fmt_money(val) -> str:
    try:
        n = float(val or 0)
        return f"${n:,.0f}"
    except (TypeError, ValueError):
        return str(val or "—")


def _fmt_slug(s: str) -> str:
    """Convert snake_case / kebab-case slugs to Title Case for display.
    e.g. 'evaporator_coil' → 'Evaporator Coil', 'dirty-filter' → 'Dirty Filter'
    """
    if not s:
        return ""
    return s.replace("_", " ").replace("-", " ").title()


def _tier_label(tier: str) -> str:
    return {"good": "Option A - Good", "better": "Option B - Better (Recommended)", "best": "Option C - Best"}.get(
        tier.lower(), tier.title()
    )


def _tier_color(tier: str):
    return {
        "good":   (0.102, 0.529, 0.329),  # green
        "better": (0.086, 0.396, 0.753),  # blue
        "best":   (0.557, 0.267, 0.678),  # purple
    }.get(tier.lower(), (0.4, 0.4, 0.4))


# ──────────────────────────────────────────────────────────────────────────────
# Main public API  (same signature as the old WeasyPrint version)
# ──────────────────────────────────────────────────────────────────────────────

def _fetch_and_annotate_photo(photo_url: str, issues: list, max_w: int = 516):
    """
    Fetch the inspection photo from storage, draw a severity legend strip at the
    bottom, and return (jpeg_bytes, pixel_width, pixel_height).

    Returns None if anything fails (Bill Gates' fallback contract: never block PDF).
    Quality gate: skips if image is below 400×300 px or any step raises.
    """
    try:
        import urllib.request as _urlreq
        import io as _io

        if not photo_url or not photo_url.startswith("http"):
            return None

        # ── Fetch ─────────────────────────────────────────────────────────────
        req = _urlreq.Request(photo_url, headers={"User-Agent": "SnapAI-PDF/1.0"})
        with _urlreq.urlopen(req, timeout=10) as resp:
            img_bytes = resp.read()

        # ── Load with Pillow ──────────────────────────────────────────────────
        from PIL import Image as _PILImage, ImageDraw as _Draw
        img = _PILImage.open(_io.BytesIO(img_bytes)).convert("RGB")

        # Quality gate
        if img.width < 400 or img.height < 300:
            return None

        # Resize to max_w preserving aspect ratio
        if img.width > max_w:
            ratio = max_w / img.width
            img = img.resize((max_w, int(img.height * ratio)), _PILImage.LANCZOS)

        # ── Severity-legend strip at the bottom ───────────────────────────────
        # Each issue gets a colored square + component label in a dark strip.
        SEV_COLORS = {
            "high":     (198, 40,  40),   # red
            "critical": (198, 40,  40),
            "medium":   (196, 96,  10),   # orange
            "low":      (26,  135, 84),   # green
        }
        STRIP_H = 30
        new_img = _PILImage.new("RGB", (img.width, img.height + STRIP_H), (28, 28, 26))
        new_img.paste(img, (0, 0))
        draw   = _Draw.Draw(new_img)
        x_cur  = 10
        strip_y = img.height

        for iss in (issues or [])[:5]:
            sev   = iss.get("severity", "medium")
            color = SEV_COLORS.get(sev, SEV_COLORS["medium"])
            label = _fmt_slug(iss.get("component", ""))[:16]
            sq_x1, sq_y1 = x_cur, strip_y + 9
            sq_x2, sq_y2 = sq_x1 + 11, sq_y1 + 11
            draw.rectangle([sq_x1, sq_y1, sq_x2, sq_y2], fill=color)
            draw.text((sq_x1 + 14, sq_y1 - 1), label, fill=(210, 210, 205))
            x_cur += 14 + len(label) * 6 + 14
            if x_cur > img.width - 60:
                break

        # ── Encode as JPEG ────────────────────────────────────────────────────
        out = _io.BytesIO()
        new_img.save(out, format="JPEG", quality=82, optimize=True)
        return out.getvalue(), new_img.width, new_img.height

    except Exception:
        # Silently swallow ALL errors — PDF must generate even without the photo
        return None


def generate_contractor_pdf(
    estimate_data: dict,
    output_dir: str = "/tmp/scopesnap_uploads/pdfs",
    filename: Optional[str] = None,
) -> str:
    """
    Generate a contractor PDF estimate — pure Python, no system dependencies.

    Args:
        estimate_data: Estimate dict with company, property, equipment, options, issues.
        output_dir: Directory to save the PDF.
        filename: Optional filename override.

    Returns:
        Absolute path to the generated PDF file.
    """
    os.makedirs(output_dir, exist_ok=True)
    if not filename:
        short_id = estimate_data.get("report_short_id", "est")
        filename = f"estimate-{short_id}.pdf"
    output_path = os.path.join(output_dir, filename)

    company    = estimate_data.get("company") or {}
    prop       = estimate_data.get("property") or {}
    equipment  = estimate_data.get("equipment") or {}
    options    = estimate_data.get("options") or []
    issues     = estimate_data.get("issues") or []
    short_id   = estimate_data.get("report_short_id", "—")
    today      = datetime.now(timezone.utc).strftime("%B %d, %Y")

    p = _PdfWriter()
    M  = 48       # left margin
    RX = 564      # right edge (612 - 48)
    W  = RX - M   # content width

    # ── PAGE 1: Header + Company + Customer + Options ─────────────────────────
    p.new_page()

    # Dark green header bar
    p.rect_fill(0, 0, 612, 72, _PdfWriter.GREEN_DARK)

    # ── Phase 1 Branding: contractor company name/logo in header ─────────────
    co_name    = company.get("name") or "Your HVAC Company"
    co_phone   = company.get("phone") or ""
    co_license = company.get("license_number") or ""
    co_logo    = company.get("logo_url") or ""

    logo_embedded = False
    if co_logo:
        try:
            jpeg_bytes, px_w, px_h = _fetch_photo(co_logo)
            if jpeg_bytes and px_w and px_h:
                # Fit logo into 44×44 square, preserve aspect ratio
                ratio = min(44 / px_w, 44 / px_h)
                logo_w = int(px_w * ratio)
                logo_h = int(px_h * ratio)
                img_name = p.add_jpeg_image(jpeg_bytes, px_w, px_h)
                # Center the logo vertically in the 72pt header bar
                logo_y = (72 - logo_h) // 2
                p.draw_image(M, logo_y, logo_w, logo_h, img_name)
                logo_embedded = True
        except Exception:
            pass  # Fall back to initial letter

    if not logo_embedded:
        # Fallback: colored square with company initial
        initial = co_name[0].upper() if co_name else "?"
        p.rect_fill(M, 14, 38, 38, _PdfWriter.GREEN)
        p.text(M + (12 if len(initial) == 1 else 8), 38, initial, size=22, color=_PdfWriter.WHITE, bold=True)

    # Company name in header (right of logo)
    name_x = M + 50
    # Truncate long names to fit in header
    display_name = co_name[:30] + ("…" if len(co_name) > 30 else "")
    p.text(name_x, 26, display_name, size=15, color=_PdfWriter.WHITE, bold=True)
    p.text(name_x, 44, "HVAC Estimate", size=9, color=(0.6, 0.85, 0.7))

    # Estimate ID + Date (top right)
    p.text_right(RX, 25, f"ESTIMATE  #{short_id}", size=9, color=(0.8, 0.95, 0.85))
    p.text_right(RX, 40, today, size=9, color=(0.6, 0.8, 0.7))

    y = 90

    # ── Company info row ──────────────────────────────────────────────────────
    p.text(M, y, co_name, size=13, bold=True)
    info_parts = [x for x in [co_phone, f"License #{co_license}" if co_license else ""] if x]
    if info_parts:
        p.text(M, y + 16, "  ·  ".join(info_parts), size=9, color=_PdfWriter.GRAY)
    y += 40

    # ── Customer / Property ───────────────────────────────────────────────────
    p.rect_fill(M, y, W, 1, _PdfWriter.LIGHT_GRAY)
    y += 8

    cust_name = prop.get("customer_name") or ""
    addr1 = prop.get("address_line1") or ""
    city_state = ", ".join(filter(None, [prop.get("city"), prop.get("state"), prop.get("zip")]))
    address_line = "  ".join(filter(None, [addr1, city_state]))

    p.text(M, y, "PREPARED FOR", size=8, color=_PdfWriter.GRAY)
    p.text(M, y + 13, cust_name or "Homeowner", size=11, bold=True)
    if address_line:
        p.text(M, y + 27, address_line, size=9, color=_PdfWriter.GRAY)

    # Equipment info (right side of same row)
    eq_brand = equipment.get("brand") or ""
    eq_model = equipment.get("model_number") or ""
    eq_year  = equipment.get("install_year") or ""
    eq_label = " ".join(filter(None, [eq_brand, eq_model]))
    if eq_label:
        p.text_right(RX, y, "EQUIPMENT", size=8, color=_PdfWriter.GRAY)
        p.text_right(RX, y + 13, eq_label, size=11, bold=True)
        if eq_year:
            p.text_right(RX, y + 27, f"Installed {eq_year}", size=9, color=_PdfWriter.GRAY)

    y += 52

    # Issues summary (if any)
    if issues:
        p.rect_fill(M, y, W, 1, _PdfWriter.LIGHT_GRAY)
        y += 10
        p.text(M, y, "ISSUES FOUND", size=8, color=_PdfWriter.ORANGE, bold=True)
        y += 14
        for iss in issues[:4]:
            comp  = _fmt_slug(iss.get("component", ""))
            issue = _fmt_slug(iss.get("issue", ""))
            sev   = iss.get("severity", "medium")
            sev_color = _PdfWriter.RED if sev in ("high", "critical") else (
                _PdfWriter.ORANGE if sev == "medium" else _PdfWriter.GREEN)
            # bullet dot — top of square at y-6 so its center aligns with 9pt cap midpoint
            p.rect_fill(M, y - 6, 5, 5, sev_color)
            label = f"{comp} — {issue}" if issue else comp
            p.text(M + 10, y, label, size=9)
            y += 14
        y += 6

    # ── Annotated inspection photo (Bill Gates fallback: silently skip on any error) ──
    photo_url = estimate_data.get("photo_url") or ""
    if photo_url:
        photo_result = _fetch_and_annotate_photo(photo_url, issues, max_w=int(W))
        if photo_result:
            jpeg_bytes, px_w, px_h = photo_result
            # Scale to fit content width; max height = 180pt to stay on page 1
            draw_w = W
            draw_h = min(180, int(draw_w * px_h / px_w))
            img_name = p.add_jpeg_image(jpeg_bytes, px_w, px_h)
            p.draw_image(M, y, draw_w, draw_h, img_name)
            y += draw_h + 10

    # ── Options table ─────────────────────────────────────────────────────────
    p.rect_fill(M, y, W, 1, _PdfWriter.LIGHT_GRAY)
    y += 10
    p.text(M, y, "YOUR OPTIONS", size=8, color=_PdfWriter.GRAY, bold=True)
    y += 16

    for opt in options:
        tier  = (opt.get("tier") or "").lower()
        name  = opt.get("name") or tier.title()
        desc  = opt.get("description") or ""
        total = opt.get("total") or 0
        five_yr = opt.get("five_year_total")
        color = _tier_color(tier)

        # Option header bar
        p.rect_fill(M, y, W, 26, color)
        label = _tier_label(tier)
        # Center text in 26pt bar: baseline = bar_top + (bar_h + cap_h) / 2
        # size=10 → cap=7.18 → (26+7.18)/2 = 16.6; size=12 → cap=8.6 → (26+8.6)/2 = 17.3
        p.text(M + 10, y + 17, label, size=10, color=_PdfWriter.WHITE, bold=True)
        p.text_right(RX - 8, y + 17, _fmt_money(total), size=12, color=_PdfWriter.WHITE, bold=True)
        y += 26

        # Name + description — baseline at y+10 so 10pt cap (7.2pt) clears bar bottom
        p.text(M + 10, y + 10, name, size=10, bold=True)
        if desc:
            desc_end_y = p.multiline_text(M + 10, y + 18, desc, size=9,
                                          max_width=W - 120, line_height=13,
                                          color=_PdfWriter.GRAY)
            desc_h = max(desc_end_y - (y + 18), 0) + 18
        else:
            desc_h = 18

        # 5-year cost (right side)
        if five_yr:
            p.text_right(RX - 8, y + 5, f"5-yr: {_fmt_money(five_yr)}", size=8, color=_PdfWriter.GRAY)

        # Energy savings
        es = opt.get("energy_savings")
        if es:
            ann = es.get("annual_savings") if isinstance(es, dict) else es
            if ann and float(ann or 0) > 0:
                p.text_right(RX - 8, y + 18, f"Saves ${float(ann):,.0f}/yr", size=8, color=_PdfWriter.GREEN)

        y += desc_h + 6

        # Line items (if present)
        line_items = opt.get("line_items") or []
        if line_items:
            for item in line_items:
                item_label = item.get("description") or item.get("label") or item.get("category") or "Item"
                item_amt   = item.get("total") or item.get("amount") or 0
                p.text(M + 16, y, item_label, size=8, color=_PdfWriter.GRAY)
                p.text_right(RX - 8, y, _fmt_money(item_amt), size=8, color=_PdfWriter.GRAY)
                y += 12
            # Subtotal / Markup / Total breakdown
            subtotal = opt.get("subtotal") or 0
            markup_pct = opt.get("markup_percent") or 0
            if subtotal and markup_pct:
                p.line(M + 16, y - 2, RX - 8, y - 2, _PdfWriter.LIGHT_GRAY)
                p.text(M + 16, y + 4, f"Subtotal", size=8)
                p.text_right(RX - 8, y + 4, _fmt_money(subtotal), size=8)
                y += 14
                p.text(M + 16, y, f"Markup ({markup_pct:.0f}%)", size=8, color=_PdfWriter.GRAY)
                markup_amt = float(total or 0) - float(subtotal or 0)
                p.text_right(RX - 8, y, _fmt_money(markup_amt), size=8, color=_PdfWriter.GRAY)
                y += 14
            # Total line
            p.rect_fill(M + 10, y, W - 20, 22, (0.96, 0.96, 0.94))
            p.text(M + 16, y + 14, "TOTAL", size=10, bold=True)
            p.text_right(RX - 8, y + 14, _fmt_money(total), size=12, bold=True, color=color)
            y += 30
        else:
            y += 6

        y += 4

        # Page break check — leave room for footer at y=750
        if y > 700:
            _draw_footer(p, M, RX, co_name, co_phone, short_id, today)
            p._flush_page()
            p.new_page()
            y = 40

    # ── 5-Year Comparison table ───────────────────────────────────────────────
    # Determine if any option has real annual savings data
    has_savings = False
    for _o in options:
        _es = _o.get("energy_savings")
        if _es:
            _ann = _es.get("annual_savings") if isinstance(_es, dict) else _es
            if _ann and float(_ann or 0) > 0:
                has_savings = True
                break

    if len(options) > 1 and any(o.get("five_year_total") for o in options):
        comparison_height = 36 + 18 * len(options) + 10
        if y + comparison_height > 700:
            _draw_footer(p, M, RX, co_name, co_phone, short_id, today)
            p._flush_page()
            p.new_page()
            y = 40

        p.rect_fill(M, y, W, 1, _PdfWriter.LIGHT_GRAY)
        y += 10
        p.text(M, y, "5-YEAR COST COMPARISON", size=8, color=_PdfWriter.GRAY, bold=True)
        y += 16

        # Header row — only show Annual Savings column if data exists
        p.rect_fill(M, y, W, 20, (0.93, 0.93, 0.91))
        p.text(M + 10, y + 13, "Option", size=9, bold=True)
        p.text(290, y + 13, "Today", size=9, bold=True)
        p.text(370, y + 13, "5-Year Total", size=9, bold=True)
        if has_savings:
            p.text(470, y + 13, "Annual Savings", size=9, bold=True)
        y += 20

        for opt in options:
            tier   = (opt.get("tier") or "").lower()
            total  = opt.get("total") or 0
            five_yr = opt.get("five_year_total")
            es = opt.get("energy_savings")
            ann = None
            if es:
                ann = es.get("annual_savings") if isinstance(es, dict) else es
            color = _tier_color(tier)
            # Use tier label in comparison table so rows are always distinct
            row_label = _tier_label(tier)

            bg = (0.97, 1.0, 0.97) if tier == "better" else (1.0, 1.0, 1.0)
            p.rect_fill(M, y, W, 18, bg)
            p.text(M + 10, y + 11, row_label, size=9, bold=(tier == "better"), color=color)
            p.text(290, y + 11, _fmt_money(total), size=9, bold=True)
            p.text(370, y + 11, _fmt_money(five_yr) if five_yr else "—", size=9, color=_PdfWriter.GRAY)
            if has_savings:
                if ann and float(ann or 0) > 0:
                    p.text(470, y + 11, f"${float(ann):,.0f}/yr", size=9, color=_PdfWriter.GREEN)
                else:
                    p.text(470, y + 11, "—", size=9, color=_PdfWriter.GRAY)
            p.line(M, y + 18, RX, y + 18, _PdfWriter.LIGHT_GRAY)
            y += 18

        y += 14

    # ── Next Steps box ────────────────────────────────────────────────────────
    next_steps_height = 72
    if y + next_steps_height < 730:
        p.rect_fill(M, y, W, 1, _PdfWriter.LIGHT_GRAY)
        y += 10
        p.text(M, y, "NEXT STEPS", size=8, color=_PdfWriter.GRAY, bold=True)
        y += 14
        p.rect_fill(M, y, W, next_steps_height - 24, (0.97, 0.98, 0.97))
        p.rect_stroke(M, y, W, next_steps_height - 24, _PdfWriter.LIGHT_GRAY)
        p.text(M + 14, y + 10, "1.  Review the options above and choose what works best for your budget.", size=9)
        p.text(M + 14, y + 24, "2.  Call or text us to schedule — we'll confirm your appointment within 24 hours.", size=9)
        p.text(M + 14, y + 38, "3.  Your homeowner report is available online at the link in your email.", size=9, color=_PdfWriter.GRAY)
        y += next_steps_height - 24 + 10

    # ── Acceptance / Signature block ──────────────────────────────────────────
    sig_height = 90
    if y + sig_height + 40 < 740:
        y += 8
        p.rect_fill(M, y, W, 1, _PdfWriter.LIGHT_GRAY)
        y += 10
        p.text(M, y, "AUTHORIZATION", size=8, color=_PdfWriter.GRAY, bold=True)
        y += 14
        p.rect_fill(M, y, W, sig_height, (0.99, 0.99, 0.99))
        p.rect_stroke(M, y, W, sig_height, _PdfWriter.LIGHT_GRAY)
        p.text(M + 14, y + 10,
               "I authorize the work described in this estimate. I understand that final pricing may vary",
               size=9, color=_PdfWriter.GRAY)
        p.text(M + 14, y + 23, "based on actual conditions found on-site.", size=9, color=_PdfWriter.GRAY)

        # Signature line
        sig_y = y + 48
        p.line(M + 14, sig_y, M + 200, sig_y, _PdfWriter.LIGHT_GRAY, lw=0.75)
        p.text(M + 14, sig_y + 8, "Homeowner Signature", size=7, color=_PdfWriter.GRAY)

        # Date line
        p.line(M + 230, sig_y, M + 360, sig_y, _PdfWriter.LIGHT_GRAY, lw=0.75)
        p.text(M + 230, sig_y + 8, "Date", size=7, color=_PdfWriter.GRAY)

        # Option chosen line
        p.line(M + 390, sig_y, RX - 14, sig_y, _PdfWriter.LIGHT_GRAY, lw=0.75)
        p.text(M + 390, sig_y + 8, "Option Selected (A / B / C)", size=7, color=_PdfWriter.GRAY)

        y += sig_height + 12

    # ── Disclaimer ────────────────────────────────────────────────────────────
    if y + 20 < 748:
        p.text(M, y + 6,
               "This estimate is valid for 30 days. Prices subject to change based on final on-site inspection.",
               size=7, color=_PdfWriter.GRAY, italic=True)

    # ── Footer (on every page — drawn on the current/last page here) ──────────
    _draw_footer(p, M, RX, co_name, co_phone, short_id, today)

    p.save(output_path)
    return output_path


def _draw_footer(p: _PdfWriter, M: float, RX: float, co_name: str, co_phone: str,
                 short_id: str, today: str):
    """Draw the branded footer bar at the bottom of the current page."""
    footer_y = 762
    p.rect_fill(0, footer_y - 2, 612, 30, (0.102, 0.529, 0.329))  # green bar
    footer_parts = [co_name]
    if co_phone:
        footer_parts.append(co_phone)
    footer_parts.append("Powered by SnapAI")
    p.text(M, footer_y + 15, "  ·  ".join(footer_parts), size=8, color=_PdfWriter.WHITE)
    p.text_right(RX, footer_y + 15, f"#{short_id}  ·  {today}", size=8, color=(0.8, 0.95, 0.85))


# ── Legacy helpers kept for compatibility ─────────────────────────────────────

def build_estimate_context_from_api_response(api_response: dict) -> dict:
    return api_response
