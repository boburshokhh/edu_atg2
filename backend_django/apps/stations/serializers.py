from rest_framework import serializers

from apps.stations.models import (
    Station,
    StationEquipment,
    StationGasSupplySource,
    StationNormativeDoc,
    StationPhoto,
    StationSafetySystem,
    StationSafetySystemFeature,
    StationSpecification,
)


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = [
            "id",
            "name",
            "short_name",
            "description",
            "image",
            "tech_map_image",
            "power",
            "commission_date",
            "courses_count",
            "status",
            "location",
            "type",
            "design_capacity",
            "gas_pressure",
            "distance_from_border",
            "pipeline_diameter",
            "input_pressure",
            "output_pressure",
            "parallel_lines",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StationEquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StationEquipment
        fields = [
            "id",
            "station",
            "name",
            "model",
            "manufacturer",
            "quantity",
            "power",
            "description",
            "order_index",
        ]
        read_only_fields = ["id", "created_at"]


class StationSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StationSpecification
        fields = [
            "id",
            "station",
            "category",
            "value",
            "unit",
            "description",
            "order_index",
        ]
        read_only_fields = ["id", "created_at"]


class StationSafetySystemFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = StationSafetySystemFeature
        fields = ["id", "safety_system", "feature_name", "order_index"]
        read_only_fields = ["id", "created_at"]


class StationSafetySystemSerializer(serializers.ModelSerializer):
    features = StationSafetySystemFeatureSerializer(many=True, read_only=True)

    class Meta:
        model = StationSafetySystem
        fields = [
            "id",
            "station",
            "name",
            "description",
            "manufacturer",
            "order_index",
            "features",
        ]
        read_only_fields = ["id", "created_at"]


class StationGasSupplySourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StationGasSupplySource
        fields = ["id", "station", "source_name", "order_index"]
        read_only_fields = ["id", "created_at"]


class StationPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StationPhoto
        fields = ["id", "station", "title", "view", "image_url", "order_index"]
        read_only_fields = ["id", "created_at"]


class StationNormativeDocSerializer(serializers.ModelSerializer):
    class Meta:
        model = StationNormativeDoc
        fields = ["id", "station", "title", "file_url"]
        read_only_fields = ["id", "created_at"]
