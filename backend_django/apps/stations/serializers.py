from rest_framework import serializers

from apps.stations.models import (
    Department,
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


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = [
            "id",
            "name",  # Legacy field
            "short_name",
            "description",  # Legacy field
            "name_ru",
            "name_en",
            "description_ru",
            "description_en",
            "image",
            "status",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        """
        Автоматически заполняем legacy поля name и description
        из name_ru/name_en и description_ru/description_en
        для обратной совместимости с базой данных
        """
        # Заполняем name из name_ru (или name_en, если name_ru нет)
        name_ru = attrs.get('name_ru')
        if name_ru is not None:
            name_ru = str(name_ru).strip() if name_ru else ''
        
        name_en = attrs.get('name_en')
        if name_en is not None:
            name_en = str(name_en).strip() if name_en else ''
        
        if name_ru:
            attrs['name'] = name_ru
        elif name_en:
            attrs['name'] = name_en
        elif 'name' not in attrs or not attrs.get('name'):
            # Если name_ru и name_en не переданы, используем из текущего объекта (при обновлении)
            if self.instance:
                attrs['name'] = self.instance.name_ru or self.instance.name_en or self.instance.name or ''
            else:
                # При создании нового объекта name_ru должно быть обязательно
                # (валидация на фронтенде уже есть, но добавим и здесь для надежности)
                if 'name_ru' not in attrs or not name_ru:
                    raise serializers.ValidationError({
                        'name_ru': 'Поле "Название (RU)" обязательно для заполнения'
                    })
                attrs['name'] = name_ru
        
        # Заполняем description из description_ru (или description_en, если description_ru нет)
        description_ru = attrs.get('description_ru')
        if description_ru is not None:
            description_ru = str(description_ru).strip()
        
        description_en = attrs.get('description_en')
        if description_en is not None:
            description_en = str(description_en).strip()
        
        if description_ru:
            attrs['description'] = description_ru
        elif description_en:
            attrs['description'] = description_en
        elif 'description' not in attrs:
            # Если description_ru и description_en не переданы, используем из текущего объекта или пустую строку
            if self.instance:
                attrs['description'] = self.instance.description_ru or self.instance.description_en or self.instance.description or ''
            else:
                attrs['description'] = ''
        
        return attrs