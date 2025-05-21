from rest_framework import serializers
from apps.models import Lease, Payment
from apps.views.tenant.serializers import TenantSerializer
from apps.views.property.serializers import PropertySerializer

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amountDue', 'amountPaid', 'dueDate', 'paymentDate', 'paymentStatus']

class LeaseSerializer(serializers.ModelSerializer):
    tenant = TenantSerializer(source='tenantCognitoId')
    property = PropertySerializer(source='propertyId')
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Lease
        fields = ['id', 'startDate', 'endDate', 'rent', 'deposit', 'tenant', 'property', 'payments']