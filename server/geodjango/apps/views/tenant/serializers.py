from rest_framework import serializers
from apps.models import Tenant

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ['cognitoId', 'name', 'email', 'phoneNumber']