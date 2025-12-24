from __future__ import annotations

from django.db import models


class VideoTranscodeJob(models.Model):
    id = models.AutoField(primary_key=True)
    target_type = models.CharField(max_length=50)
    target_id = models.IntegerField()
    station_id = models.IntegerField(null=True, blank=True)
    source_object_key = models.CharField(max_length=1000)
    master_object_key = models.CharField(max_length=1000, null=True, blank=True)
    status = models.CharField(max_length=20, default="queued")
    error = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "video_transcode_jobs"
        managed = False


