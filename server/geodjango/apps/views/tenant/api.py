from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging
from .services import *
from .serializers import TenantSerializer
from rest_framework.permissions import AllowAny
from core.authMiddleware import jwt_auth
from django.http import JsonResponse
from rest_framework.decorators import permission_classes
from apps.models import Property
from apps.views.property.serializers import PropertySerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def api_get_tenant(request, cognitoId):
    try:
        if not cognitoId:
            return JsonResponse(
                {"message": "cognitoId is required"},
                status=400
            )
        tenant = getTenant(cognitoId=cognitoId)  # Changed from cognito_id to cognitoId
        if tenant:
            serializer = TenantSerializer(tenant)
            return JsonResponse(
                {
                    "data": serializer.data,
                    "message": f"Get tenant with cognitoId {cognitoId} successfully",
                    "error": None
                },
                status=status.HTTP_200_OK
            )
        else:
            return JsonResponse(
                {"message": f"Tenant with cognitoId {cognitoId} not found or has no favorites"},
                status=404
            )
    except Exception as e:
            logging.error(f"Error retrieving Tenant: {e}")
            return JsonResponse(
                {"message": f"Error retrieving Tenant: {str(e)}"},
                status=505
            )
    

@api_view(["POST"])
@permission_classes([AllowAny])
def api_create_tenant(request):  # Remove 'self' parameter
    try:
        data = request.data
        cognitoId = data.get('cognitoId')
        name = data.get('name')
        email = data.get('email')
        phoneNumber = data.get('phoneNumber', '')
        tenant = Tenant.objects.create(
            cognitoId=cognitoId, 
            name=name, 
            email=email, 
            phoneNumber=phoneNumber
        )

        serializer = TenantSerializer(tenant)
        return Response(
            {
                "data": serializer.data,
                "message": f"Tenant with cognitoId {cognitoId} created successfully",
                "error": None
            },
            status=status.HTTP_201_CREATED            )
    except ValueError as e:
        logging.error(f"Error creating Tenant: {str(e)}")
        return Response(
            {"message": str(e), "error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logging.error(f"Unexpected error creating Tenant: {str(e)}")
        return Response(
            {"message": f"Error creating Tenant: {str(e)}", "error": str(e)},
            status=500
        )

@api_view(["PUT"])
@permission_classes(['tenant','manager'])
def put(request):
        try:
            data = request.data
            cognitoId = request.GET.get('cognitoId')
            name = data.get('name')
            email = data.get('email')
            phoneNumber = data.get('phoneNumber')

            updated_tenant = updateTenant(cognitoId=cognitoId, name=name, email=email, phoneNumber=phoneNumber)
            serializer = TenantSerializer(updated_tenant)
            return Response(
                {
                    "data": serializer.data,
                    "message": f"Tenant with cognitoId {cognitoId} updated successfully",
                    "error": None
                },
                status=status.HTTP_202_ACCEPTED
            )
        except ValueError as e:
            logging.error(f"Error creating Tenant: {str(e)}")
            return Response(
                {"message": str(e), "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logging.error(f"Unexpected error creating Tenant: {str(e)}")
            return Response(
                {"message": f"Error creating Tenant: {str(e)}", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(["GET"])
# @permission_classes(['tenant','manager'])
@permission_classes([AllowAny])
def getCurrentResidences(request, cognitoId):
    try:
        # cognito_id = request.GET.get('cognitoId')
        if not cognitoId:
            return Response(
                {"message": "cognitoId is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        properties = Property.objects.select_related('locationId').filter(
            tenants__cognitoId=cognitoId
        )
        
        serializer = PropertySerializer(properties, many=True)
        return Response(
            {"properties": serializer.data},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {"message": f"Error retrieving current residences: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["POST"])
def addFavoriteProperty(request):
    try:
        cognito_id = request.data.get('cognitoId')
        property_id = request.data.get('propertyId')

        if not cognito_id or not property_id:
            return Response(
                {"message": "cognitoId and propertyId are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        tenant = Tenant.objects.get(cognitoId=cognito_id)
        property = Property.objects.get(id=property_id)

        if property in tenant.favorites.all():
            return Response(
                {"message": "Property already added as favorite"},
                status=status.HTTP_409_CONFLICT
            )

        tenant.favorites.add(property)
        serializer = TenantSerializer(tenant)
        return Response(
            {"data": serializer.data},
            status=status.HTTP_200_OK
        )
    except (Tenant.DoesNotExist, Property.DoesNotExist) as e:
        return Response(
            {"message": "Tenant or Property not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"message": f"Error adding favorite property: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["DELETE"])
def removeFavoriteProperty(request):
    try:
        cognito_id = request.data.get('cognitoId')
        property_id = request.data.get('propertyId')

        if not cognito_id or not property_id:
            return Response(
                {"message": "cognitoId and propertyId are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        tenant = Tenant.objects.get(cognitoId=cognito_id)
        property = Property.objects.get(id=property_id)

        if property not in tenant.favorites.all():
            return Response(
                {"message": "Property is not in favorites"},
                status=status.HTTP_404_NOT_FOUND
            )

        tenant.favorites.remove(property)
        serializer = TenantSerializer(tenant)
        return Response(
            {"data": serializer.data},
            status=status.HTTP_200_OK
        )
    except (Tenant.DoesNotExist, Property.DoesNotExist) as e:
        return Response(
            {"message": "Tenant or Property not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"message": f"Error removing favorite property: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )