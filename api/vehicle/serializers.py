from rest_framework import serializers
from .models import Vehicle

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = "__all__"

    def update(self, instance, validated_data):
        # Raise an exception if attempting to update the owner
        if 'owner' in validated_data:
            raise serializers.ValidationError("Owner field cannot be updated.")

        return super().update(instance, validated_data)
