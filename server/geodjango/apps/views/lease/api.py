from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from apps.models import Lease, Payment
from .serializer import LeaseSerializer, PaymentSerializer
import logging

@api_view(["GET"])
def getLeases(request):
    try:
        leases = Lease.objects.select_related('tenantCognitoId', 'propertyId').all()
        serializer = LeaseSerializer(leases, many=True)
        return Response(
            {"data": serializer.data},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        logging.error(f"Error retrieving leases: {str(e)}")
        return Response(
            {"message": f"Error retrieving leases: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["GET"])
def getLeasePayments(request, id):
    try:
        payments = Payment.objects.filter(lease_id=id)
        serializer = PaymentSerializer(payments, many=True)
        return Response(
            {"data": serializer.data},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        logging.error(f"Error retrieving lease payments: {str(e)}")
        return Response(
            {"message": f"Error retrieving lease payments: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )