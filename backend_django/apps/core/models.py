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


