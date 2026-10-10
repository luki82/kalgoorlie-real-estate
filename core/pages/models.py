from django.db import models


class Inquiry(models.Model):
    """A quote request or question sent through the Contact page."""

    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    email_sent = models.BooleanField(
        default=False, help_text="Whether the notification email to you went through."
    )
    handled = models.BooleanField(default=False, help_text="Tick once you've replied.")

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "inquiries"

    def __str__(self):
        return f"{self.full_name} - {self.subject or 'Enquiry'}"
