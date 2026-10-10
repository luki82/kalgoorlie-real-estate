"""
Portfolio drawings.

How it works:
  1. Put PDFs in core/portfolio_pdfs/  (one PDF = one project, every page is shown)
  2. Run:  python manage.py build_portfolio
     This turns every PDF page into high-resolution WebP images in
     core/static/portfolio/ and writes core/static/portfolio/manifest.json
  3. Commit and push. The live site serves the images as static files, so
     they never disappear and no AWS or paid disk is needed.

Optional: a .txt file with the same name as a PDF (e.g. 01_House.txt next to
01_House.pdf) is shown as that project's description.
"""
import json
import re
import shutil
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.templatetags.static import static
from django.utils.text import slugify
from PIL import Image

OUTPUT_SUBDIR = "portfolio"          # inside STATICFILES_DIRS[0]
SIZES = [1200, 2400]                 # widths for phones / laptops; the browser picks
FULL_LONG_EDGE = 5000                # tap-to-zoom image, longest side in pixels
MAX_DPI = 300
WEBP_QUALITY = 92                    # keeps thin drafting lines and small text crisp


def output_dir() -> Path:
    return Path(settings.STATICFILES_DIRS[0]) / OUTPUT_SUBDIR


def manifest_path() -> Path:
    return output_dir() / "manifest.json"


def title_from_filename(stem: str) -> str:
    """'01_Two-storey_house - Floor plans' -> 'Two-storey house - Floor plans'"""
    stem = re.sub(r"^\d+[\s._-]*", "", stem)   # leading number only sets the order
    return stem.replace("_", " ").strip() or "Project"


def _save_webp(img, path: Path, width=None):
    if width and img.width > width:
        img = img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)
    img.save(path, "WEBP", quality=WEBP_QUALITY, method=6)
    return img.width, img.height


def render_pdf(pdf_path: Path, dest: Path):
    """Render every page of pdf_path into dest/. Returns the list of page records."""
    import fitz  # PyMuPDF

    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    pages = []
    with fitz.open(pdf_path) as doc:
        for i, page in enumerate(doc, start=1):
            zoom = min(FULL_LONG_EDGE / max(page.rect.width, page.rect.height), MAX_DPI / 72)
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            del pix

            name = f"p{i:02d}"
            full_w, full_h = _save_webp(img, dest / f"{name}-full.webp")
            files = [[f"{name}-full.webp", full_w]]
            for w in SIZES:
                if w < full_w:
                    _save_webp(img, dest / f"{name}-{w}.webp", w)
                    files.insert(-1, [f"{name}-{w}.webp", w])
            pages.append({"files": files, "width": full_w, "height": full_h})
    return pages


def build(force=False, log=print):
    src_dir = Path(settings.PORTFOLIO_PDF_DIR)
    out = output_dir()
    out.mkdir(parents=True, exist_ok=True)

    old = {}
    if manifest_path().exists():
        old = {p["slug"]: p for p in json.loads(manifest_path().read_text(encoding="utf-8"))}

    projects = []
    for pdf in sorted(src_dir.glob("*.pdf"), key=lambda p: p.name.lower()):
        slug = slugify(pdf.stem) or "project"
        stat = pdf.stat()
        signature = f"{stat.st_size}-{int(stat.st_mtime)}"
        txt = pdf.with_suffix(".txt")
        description = txt.read_text(encoding="utf-8").strip() if txt.exists() else ""

        prev = old.get(slug)
        if not force and prev and prev.get("signature") == signature and (out / slug).exists():
            pages = prev["pages"]
            log(f"  unchanged: {pdf.name}")
        else:
            log(f"  rendering: {pdf.name} ...")
            pages = render_pdf(pdf, out / slug)
            log(f"             {len(pages)} page(s) done")

        projects.append({
            "slug": slug,
            "title": title_from_filename(pdf.stem),
            "description": description,
            "signature": signature,
            "pages": pages,
        })

    # Remove images for PDFs that were deleted from the folder
    keep = {p["slug"] for p in projects}
    for folder in out.iterdir():
        if folder.is_dir() and folder.name not in keep:
            shutil.rmtree(folder)
            log(f"  removed: {folder.name}")

    manifest_path().write_text(json.dumps(projects, indent=2), encoding="utf-8")
    return projects


_cache = {"mtime": None, "projects": []}


def load_projects():
    """Projects for the templates, with ready-to-use image URLs."""
    path = manifest_path()
    if not path.exists():
        return []
    mtime = path.stat().st_mtime
    if _cache["mtime"] != mtime:
        raw = json.loads(path.read_text(encoding="utf-8"))
        projects = []
        for p in raw:
            pages = []
            for n, page in enumerate(p["pages"], start=1):
                urls = [(static(f"{OUTPUT_SUBDIR}/{p['slug']}/{f}"), w) for f, w in page["files"]]
                default = urls[-2][0] if len(urls) > 1 else urls[-1][0]   # 2400px if available
                pages.append({
                    "number": n,
                    "src": default,
                    "srcset": ", ".join(f"{u} {w}w" for u, w in urls),
                    "full": urls[-1][0],
                    "width": page["width"],
                    "height": page["height"],
                })
            projects.append({**p, "pages": pages, "page_count": len(pages)})
        _cache.update(mtime=mtime, projects=projects)
    return _cache["projects"]
