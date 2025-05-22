from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from datetime import datetime, timedelta
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from apps.models import Application, Property, Tenant, Lease
from .serializer import ApplicationSerializer
import logging
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes

def calculate_next_payment_date(start_date):
    today = timezone.now()
    next_payment_date = start_date
    
    # Sử dụng relativedelta để tính toán chính xác theo tháng
    while next_payment_date <= today:
        next_payment_date += relativedelta(months=1)
    
    return next_payment_date

@api_view(["GET"])
@permission_classes([AllowAny])
def listApplications(request):
    try:
        user_id = request.GET.get('userId')
        user_type = request.GET.get('userType')

        if not user_id or not user_type:
            return Response(
                {"message": "userId and userType are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Initialize the queryset with proper select_related
        applications = Application.objects.select_related(
            'propertyId',
            'tenantCognitoId',
            'leaseId'
        )

        # Filter based on user type
        if user_type == "tenant":
            applications = applications.filter(tenantCognitoId__cognitoId=user_id)
        elif user_type == "manager":
            applications = applications.filter(propertyId__managerCognitoId__cognitoId=user_id)
        else:
            return Response(
                {"message": "Invalid userType"},
                status=status.HTTP_400_BAD_REQUEST
            )

        formatted_applications = []
        for app in applications:
            lease = Lease.objects.filter(
                tenantCognitoId=app.tenantCognitoId,
                propertyId=app.propertyId
            ).order_by('-startDate').first()

            app_data = ApplicationSerializer(app).data
            if lease:
                app_data['property']['lease'] = {
                    'id': lease.id,
                    'startDate': lease.startDate,
                    'endDate': lease.endDate,
                    'rent': lease.rent,
                    'deposit': lease.deposit,
                    'nextPaymentDate': calculate_next_payment_date(lease.startDate)
                }
            else:
                app_data['property']['lease'] = None

            formatted_applications.append(app_data)

        return Response(formatted_applications, status=status.HTTP_200_OK)

    except Exception as e:
        logging.error(f"Error retrieving applications: {str(e)}")
        return Response(
            {"message": f"Error retrieving applications: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["POST"])
@permission_classes(['manager'])
def createApplication(request):
    try:
        data = request.data
        property_id = data.get('propertyId')
        property = Property.objects.get(id=property_id)
        tenant = Tenant.objects.get(cognitoId=data.get('tenantCognitoId'))

        with transaction.atomic():
            # Create lease first
            lease = Lease.objects.create(
                startDate=datetime.now(),
                endDate=datetime.now() + timedelta(days=365),  # 1 year lease
                rent=property.pricePerMonth,
                deposit=property.securityDeposit,
                propertyId=property,
                tenantCognitoId=tenant
            )

            # Create application
            application = Application.objects.create(
                applicationDate=datetime.now(),
                status=data.get('status'),
                propertyId=property,
                tenantCognitoId=tenant,  # Now using the Tenant object
                name=data.get('name'),
                email=data.get('email'),
                phoneNumber=data.get('phoneNumber'),
                message=data.get('message'),
                leaseId=lease
            )

        serializer = ApplicationSerializer(application)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Property.DoesNotExist:
        return Response(
            {"message": "Property not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Tenant.DoesNotExist:
        return Response(
            {"message": "Tenant not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logging.error(f"Error creating application: {str(e)}")
        return Response(
            {"message": f"Error creating application: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["PUT"])
def updateApplicationStatus(request, id):
    try:
        status_value = request.data.get('status')
        if not status_value:
            return Response(
                {"message": "Status is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        application = Application.objects.select_related(
            'property', 'tenant'
        ).get(id=id)

        if status_value == "Approved":
            # Create new lease
            lease = Lease.objects.create(
                startDate=datetime.now(),
                endDate=datetime.now() + timedelta(days=365),
                rent=application.property.pricePerMonth,
                deposit=application.property.securityDeposit,
                propertyId=application.property,
                tenantCognitoId=application.tenant
            )

            # Update property tenants
            application.property.tenants.add(application.tenant)

            # Update application
            application.status = status_value
            application.leaseId = lease
            application.save()
        else:
            application.status = status_value
            application.save()

        serializer = ApplicationSerializer(application)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Application.DoesNotExist:
        return Response(
            {"message": f"Application not found with id: {id}"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logging.error(f"Error updating application status: {str(e)}")
        return Response(
            {"message": f"Error updating application status: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )