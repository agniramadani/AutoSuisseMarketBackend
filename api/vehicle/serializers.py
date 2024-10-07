from rest_framework import serializers
from .models import Vehicle, VehicleImage


class VehicleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleImage
        fields = "__all__"

    def validate(self, attrs):
        vehicle = attrs.get('vehicle')
        if vehicle.images.count() >= 10:
            raise serializers.ValidationError("You can only upload a maximum of 10 images.")
        return attrs


class VehicleSerializer(serializers.ModelSerializer):
    images = VehicleImageSerializer(many=True, read_only=True)

    class Meta:
        model = Vehicle
        fields = ["id", "make", "model", "year", "price", "mileage", "color", "fuel_type", 
                  "transmission", "description", "created_at", "owner", "images"]

    def update(self, instance, validated_data):
        # Raise an exception if attempting to update the owner
        if 'owner' in validated_data:
            raise serializers.ValidationError("Owner field cannot be updated.")

        return super().update(instance, validated_data)
