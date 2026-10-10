from django.core.management.base import BaseCommand

from pages.portfolio import build


class Command(BaseCommand):
    help = "Turn the PDFs in portfolio_pdfs/ into high-resolution images for the Portfolio page."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Re-render every PDF, even unchanged ones.")

    def handle(self, *args, **options):
        projects = build(force=options["force"], log=self.stdout.write)
        if not projects:
            self.stdout.write(self.style.WARNING("No PDFs found in portfolio_pdfs/ – add some and run this again."))
            return
        pages = sum(len(p["pages"]) for p in projects)
        self.stdout.write(self.style.SUCCESS(f"Done: {len(projects)} project(s), {pages} page(s)."))
        self.stdout.write("Next: git add . && git commit -m \"Update portfolio\" && git push")
