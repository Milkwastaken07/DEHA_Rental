from rest_framework import serializers
from apps.models import Manager

class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = ['cognitoId', 'name', 'email', 'phoneNumber']