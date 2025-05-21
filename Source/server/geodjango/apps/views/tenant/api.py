from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging
from .services import *
from .serializers import TenantSerializer

class TenantView(APIView):
    def get(self, request):
        try:
            cognito_id = request.GET.get('cognitoId')
            if not cognito_id:
                return Response(
                    {"message": "cognitoId is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            tenant =  getTenant(cognito_id=cognito_id)
            if tenant:
                serializer = TenantSerializer(tenant)
                return Response(
                    {
                        "data": serializer.data,
                        "message": f"Get tenant with cognitoId {cognito_id} successfully",
                        "error": None
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"message": f"Tenant with cognitoId {cognito_id} not found or has no favorites"},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            logging.error(f"Error retrieving Tenant: {e}")
            return Response(
                {"message": f"Error retrieving Tenant: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    def post(self, request):
        try:
            data = request.data
            cognitoId = data.get('cognitoId')
            name = data.get('name')
            email = data.get('email')
            phoneNumber = data.get('phoneNumber')

            tenant = createTenant(cognitoId=cognitoId, name=name, email=email, phoneNumber=phoneNumber)
            serializer = TenantSerializer(tenant)
            return Response(
                {
                    "data": serializer.data,
                    "message": f"Tenant with cognitoId {cognitoId} created successfully",
                    "error": None
                },
                status=status.HTTP_201_CREATED
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
    def put(self, request):
        try:
            data = request.data
            cognitoId = request.GET.get('cognitoId')
            name = data.get('name')
            email = data.get('email')
            phoneNumber = data.get('phoneNumber')

            updateTenant = updateTenant(cognitoId=cognitoId, name=name, email=email, phoneNumber=phoneNumber)
            serializer = TenantSerializer(updateTenant)
            return Response(
                {
                    "data": serializer.data,
                    "message": f"Tenant with cognitoId {cognitoId} created successfully",
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
def getCurrentResidences(request):
    try:
        cognito_id = request.GET.get('cognitoId')
        if not cognito_id:
            return Response(
                {"message": "cognitoId is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        properties = Property.objects.select_related('locationId').filter(
            tenants__cognitoId=cognito_id
        )
        
        serializer = PropertySerializer(properties, many=True)
        return Response(
            {"data": serializer.data},
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