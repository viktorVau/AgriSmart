from django.db import models
from django.conf import settings
from PIL import Image
from django.core.exceptions import ValidationError
import os
from accounts.models import CustomUser


def user_profile_picture_path(instance, filename):
    ext = filename.split('.')[-1]
    return f"profile_pictures/{instance.user.id}.{ext}"


def validate_image(image):
    # Restrict file size to 2MB
    max_size = 2 * 1024 * 1024
    if image.size > max_size:
        raise ValidationError("Image file too large ( > 2MB )")
    
    # Allow only JPEG or PNG
    ext = os.path.splitext(image.name)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png']:
        raise ValidationError("Unsupported file extension. Use .jpg, .jpeg or .png.")


class ProfileImageMixin(models.Model):
    profile_image = models.ImageField(
        upload_to=user_profile_picture_path,
        validators=[validate_image],
        null=True,
        blank=True
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.profile_image:
            image = Image.open(self.profile_image.path)
            image = image.convert("RGB")
            image = image.resize((300, 300))
            image.save(self.profile_image.path)

# LANGUAGE_CHOICES = [
#     ('en', 'English'),
#     ('sw', 'Swahili'),
#     ('yo', 'Yoruba'),
#     ('ha', 'Hausa'),
#     ('zu', 'Zulu'),
# ]

class Farmer(ProfileImageMixin):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    location = models.CharField(max_length=255, blank=True)
    farm_size = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    # language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name = "Farmer"
        verbose_name_plural = "Farmers"

    def __str__(self):
        return f"Farmer: {self.user.get_full_name() or self.user.email}"


class Agronomist(ProfileImageMixin):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    qualifications = models.TextField(blank=True)
    years_of_experience = models.PositiveIntegerField(blank=True, null=True)
    specialization = models.CharField(max_length=255, blank=True)
    # language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name = "Agronomist"
        verbose_name_plural = "Agronomists"

    def __str__(self):
        return f"Agronomist: {self.user.get_full_name() or self.user.email}"

class SoilTest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    ph = models.FloatField()
    nitrogen = models.FloatField()
    phosphorus = models.FloatField()
    potassium = models.FloatField()
    test_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SoilTest by {self.user.email} on {self.test_date}"
