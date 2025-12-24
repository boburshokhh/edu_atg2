from django.db import models


class Station(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    image = models.CharField(max_length=255, null=True, blank=True)
    tech_map_image = models.CharField(max_length=500, null=True, blank=True)
    power = models.CharField(max_length=100, null=True, blank=True)
    commission_date = models.CharField(max_length=20, null=True, blank=True)
    courses_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default="active")
    location = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    design_capacity = models.CharField(max_length=100, null=True, blank=True)
    gas_pressure = models.CharField(max_length=100, null=True, blank=True)
    distance_from_border = models.CharField(max_length=100, null=True, blank=True)
    pipeline_diameter = models.CharField(max_length=100, null=True, blank=True)
    input_pressure = models.CharField(max_length=100, null=True, blank=True)
    output_pressure = models.CharField(max_length=100, null=True, blank=True)
    parallel_lines = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "stations"
        managed = False


class StationEquipment(models.Model):
    id = models.AutoField(primary_key=True)
    station = models.ForeignKey(Station, db_column="station_id", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    model = models.CharField(max_length=255, null=True, blank=True)
    manufacturer = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    power = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "station_equipment"
        managed = False


class StationSpecification(models.Model):
    id = models.AutoField(primary_key=True)
    station = models.ForeignKey(Station, db_column="station_id", on_delete=models.CASCADE)
    category = models.CharField(max_length=255)
    value = models.CharField(max_length=100, null=True, blank=True)
    unit = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "station_specifications"
        managed = False


class StationSafetySystem(models.Model):
    id = models.AutoField(primary_key=True)
    station = models.ForeignKey(Station, db_column="station_id", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    manufacturer = models.CharField(max_length=255, null=True, blank=True)
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "station_safety_systems"
        managed = False


class StationSafetySystemFeature(models.Model):
    id = models.AutoField(primary_key=True)
    safety_system = models.ForeignKey(
        StationSafetySystem, db_column="safety_system_id", on_delete=models.CASCADE
    )
    feature_name = models.CharField(max_length=255)
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "station_safety_system_features"
        managed = False


class StationGasSupplySource(models.Model):
    id = models.AutoField(primary_key=True)
    station = models.ForeignKey(Station, db_column="station_id", on_delete=models.CASCADE)
    source_name = models.CharField(max_length=255)
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "station_gas_supply_sources"
        managed = False


class StationPhoto(models.Model):
    id = models.AutoField(primary_key=True)
    station = models.ForeignKey(Station, db_column="station_id", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    view = models.CharField(max_length=100)
    image_url = models.CharField(max_length=500)
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "station_photos"
        managed = False


class StationNormativeDoc(models.Model):
    id = models.AutoField(primary_key=True)
    station = models.ForeignKey(Station, db_column="station_id", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    file_url = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "station_normative_docs"
        managed = False


class StationPromoVideo(models.Model):
    id = models.AutoField(primary_key=True)
    station = models.ForeignKey(Station, db_column="station_id", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=True, blank=True)
    object_key = models.CharField(max_length=1000)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "station_promo_videos"
        managed = False
