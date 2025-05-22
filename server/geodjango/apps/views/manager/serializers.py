from rest_framework import serializers
from apps.models import Manager

class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = ['cognitoId', 'name', 'email', 'phoneNumber']
        extra_kwargs = {
            'name': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
            'phoneNumber': {'required': True, 'allow_blank': False}
        }