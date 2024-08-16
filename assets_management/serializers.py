from rest_framework import serializers
from .models import Asset


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['asset_id', 'name', 'asset_type', 'purchase_date', 'owner', 'created_at']
