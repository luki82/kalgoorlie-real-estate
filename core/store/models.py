from django.db import models
from django.core.validators import FileExtensionValidator

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    # The main "Cover" preview file (shows on the homepage grid)
    preview_file = models.FileField(
        upload_to='product_previews/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        help_text="Upload a high-quality PDF or image file.",
        null=True, 
        blank=True
    )

    # Property to help your HTML template figure out how to display the cover file
    @property
    def is_pdf(self):
        if self.preview_file:
            return self.preview_file.name.lower().endswith('.pdf')
        return False
    
    # The video preview loop (MP4/GIF)
    video_preview = models.FileField(
        upload_to='product_videos/', 
        null=True, 
        blank=True
    )
    
    # This is the actual AutoCAD .dwg, .zip, or PDF file the customer is buying
    digital_file = models.FileField(
        upload_to='digital_products/',
        validators=[FileExtensionValidator(allowed_extensions=['dwg', 'dxf', 'zip', 'pdf', 'rvt'])],
        null=True,
        blank=True
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# The Gallery model for unlimited extra files (Elevations, Site Plans, etc.)
class ProductGallery(models.Model):
    product = models.ForeignKey(Product, related_name='gallery_files', on_delete=models.CASCADE)
    
    # Optional field to label the specific drawing
    title = models.CharField(max_length=100, blank=True, help_text="e.g., Electrical Plan, Site Plan")
    
    # The actual file field for the extra plans
    file = models.FileField(
        upload_to='product_gallery/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
    )

    # Property to help your HTML template render the gallery files correctly
    @property
    def is_pdf(self):
        if self.file:
            return self.file.name.lower().endswith('.pdf')
        return False

    def __str__(self):
        return f"{self.product.title} - {self.title or 'Gallery File'}"