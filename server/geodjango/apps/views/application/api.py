from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from datetime import datetime, timedelta
from apps.models import Application, Property, Tenant, Lease
from .serializer import ApplicationSerializer
import logging

def calculate_next_payment_date(start_date):
    today = datetime.now()
    next_payment_date = start_date
    while next_payment_date <= today:
        next_payment_date = next_payment_date + timedelta(days=30)  # Approximating a month
    return next_payment_date

@api_view(["GET"])
def listApplications(request):
    try:
        user_id = request.GET.get('userId')
        user_type = request.GET.get('userType')

        if not user_id or not user_type:
            return Response(
                {"message": "userId and userType are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user_type == "tenant":
            applications = Application.objects.filter(
                tenantCognitoId=user_id
            ).select_related('property', 'property__locationId', 'property__managerCognitoId', 'tenant')
        elif user_type == "manager":
            applications = Application.objects.filter(
                property__managerCognitoId=user_id
            ).select_related('property', 'property__locationId', 'property__managerCognitoId', 'tenant')
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
def createApplication(request):
    try:
        data = request.data
        property_id = data.get('propertyId')
        property = Property.objects.get(id=property_id)

        with transaction.atomic():
            # Create lease first
            lease = Lease.objects.create(
                startDate=datetime.now(),
                endDate=datetime.now() + timedelta(days=365),  # 1 year lease
                rent=property.pricePerMonth,
                deposit=property.securityDeposit,
                propertyId=property,
                tenantCognitoId=Tenant.objects.get(cognitoId=data.get('tenantCognitoId'))
            )

            # Create application
            application = Application.objects.create(
                applicationDate=datetime.now(),
                status=data.get('status'),
                propertyId=property,
                tenantCognitoId=data.get('tenantCognitoId'),
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