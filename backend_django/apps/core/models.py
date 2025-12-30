from django.db import models


class SiteSettings(models.Model):
    """
    Singleton table (id=1) for site-wide settings.
    Stores only MinIO object keys (NOT public URLs).
    """

    id = models.IntegerField(primary_key=True)
    hero_background_image = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "site_settings"
        managed = False


class HeroSliderImage(models.Model):
    """
    Hero slider images table.
    Stores MinIO object keys (NOT public URLs).
    """

    id = models.AutoField(primary_key=True)
    key = models.CharField(max_length=500)  # MinIO object key
    order_index = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "hero_slider_images"
        managed = False
        ordering = ["order_index", "id"]


