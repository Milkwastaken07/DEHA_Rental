from rest_framework import serializers
from apps.models import Property, Location

class LocationSerializer(serializers.ModelSerializer):
    longitude = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = ['address', 'city', 'state', 'country', 'postalCode', 'longitude', 'latitude']

    def get_longitude(self, obj):
        return obj.coordinates.x if obj.coordinates else None

    def get_latitude(self, obj):
        return obj.coordinates.y if obj.coordinates else None

class PropertySerializer(serializers.ModelSerializer):
    location = LocationSerializer(source='locationId')

    class Meta:
        model = Property
        fields = [
            'id', 'name', 'description', 'pricePerMonth', 'securityDeposit', 'applicationFee',
            'photoUrls', 'amenities', 'highlights', 'isPetsAllowed', 'isParkingIncluded',
            'beds', 'baths', 'squareFeet', 'propertyType', 'postedDate', 'averageRating',
            'numberOfReviews', 'location'
        ]