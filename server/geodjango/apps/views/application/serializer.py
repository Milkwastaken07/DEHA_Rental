from rest_framework import serializers
from apps.models import Application, Lease, Property
from apps.views.tenant.serializers import TenantSerializer
from apps.views.property.serializers import PropertySerializer
from apps.views.lease.serializer import LeaseSerializer

class ApplicationSerializer(serializers.ModelSerializer):
    property = PropertySerializer(source='propertyId', read_only=True)
    tenant = TenantSerializer(source='tenantCognitoId', read_only=True)
    lease = LeaseSerializer(read_only=True)

    class Meta:
        model = Application
        fields = ['id', 'applicationDate', 'status', 'name', 'email', 'phoneNumber',
                 'message', 'property', 'tenant', 'lease']