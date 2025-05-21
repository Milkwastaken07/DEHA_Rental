from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
from .services import *
from .serializers import ManagerSerializer
from core.authMiddleware import jwt_auth
from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework.decorators import api_view

from apps.models import *


class ManagerView(APIView):
    permission_classes = [AllowAny]

    # @jwt_auth(allowed_roles=['manager'])
    def get(self, request, cognitoId):
        try:
            # Remove this line as cognitoId is already in the URL parameters
            # cognitoId = request.GET.get('cognitoId')
            if not cognitoId:
                return Response(
                    {"message": "cognitoId is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            manager = getManager(cognitoId=cognitoId)
            if manager:
                print(manager)
                serializer = ManagerSerializer(manager)
                return Response(
                    {
                        "data": serializer.data,
                        "message": f"Get manager with cognitoId {cognitoId} successfully",
                        "error": None
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"message": f"Manager with cognitoId {cognitoId} not found or has no favorites"},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            logging.error(f"Error retrieving Manager: {e}")
            return Response(
                {"message": f"Error retrieving Manager: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        try:
            data = request.data
            cognitoId = data.get('cognitoId')
            name = data.get('name')
            email = data.get('email')
            phoneNumber = data.get('phoneNumber')

            manager = createManager(
                cognitoId=cognitoId, name=name, email=email, phoneNumber=phoneNumber)
            serializer = ManagerSerializer(manager)
            return Response(
                {
                    "data": serializer.data,
                    "message": f"Manager with cognitoId {cognitoId} created successfully",
                    "error": None
                },
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            logging.error(f"Error creating Manager: {str(e)}")
            return Response(
                {"message": str(e), "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logging.error(f"Unexpected error creating Manager: {str(e)}")
            return Response(
                {"message": f"Error creating Manager: {str(e)}", "error": str(
                    e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request):
        try:
            data = request.data
            cognitoId = request.GET.get("cognitoId")
            name = data.get('name')
            email = data.get('email')
            phoneNumber = data.get('phoneNumber')

            manager = updateManager(
                cognitoId=cognitoId, name=name, email=email, phoneNumber=phoneNumber)
            serializer = ManagerSerializer(manager)
            return Response(
                {
                    "data": serializer.data,
                    "message": f"Manager with cognitoId {cognitoId} updated successfully",
                    "error": None
                },
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            logging.error(f"Error updating Manager: {str(e)}")
            return Response(
                {"message": str(e), "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logging.error(f"Unexpected error creating Manager: {str(e)}")
            return Response(
                {"message": f"Error creating Manager: {str(e)}", "error": str(
                    e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(["GET"])
def getManagerProperties(request):
    try:
        cognitoId = request.GET.get('cognitoId')

        manager = Manager.objects.get(cognitoId=cognitoId)
        serializer = ManagerSerializer(manager)

        properties = Property.objects.select_related('location').filter(managerCognitoId=cognitoId)

        propertiesWithFormattedLocation = []
        for property in properties:
            # Get coordinates from the Point field
            coordinates = property.location.coordinates
            longitude = coordinates.x
            latitude = coordinates.y
            
            # Format the property data
            property_data = {
                'id': property.id,
                'name': property.name,
                'description': property.description,
                'pricePerMonth': property.pricePerMonth,
                'securityDeposit': property.securityDeposit,
                'applicationFee': property.applicationFee,
                'photoUrls': property.photoUrls,
                'amenities': property.amenities,
                'highlights': property.highlights,
                'isPetsAllowed': property.isPetsAllowed,
                'isParkingIncluded': property.isParkingIncluded,
                'beds': property.beds,
                'baths': property.baths,
                'squareFeet': property.squareFeet,
                'propertyType': property.propertyType,
                'postedDate': property.postedDate,
                'averageRating': property.averageRating,
                'numberOfReviews': property.numberOfReviews,
                'location': {
                    'id': property.location.id,
                    'address': property.location.address,
                    'city': property.location.city,
                    'state': property.location.state,
                    'country': property.location.country,
                    'postalCode': property.location.postalCode,
                    'coordinates': {
                        'longitude': longitude,
                        'latitude': latitude
                    }
                }
            }
            propertiesWithFormattedLocation.append(property_data)

        return Response({"data": propertiesWithFormattedLocation}, status=status.HTTP_200_OK)
    except Manager.DoesNotExist:
        return Response(
            {"errors": "Manager not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Property.DoesNotExist:
        return Response(
            {"errors": "Property not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logging.error(f"Error retrieving properties: {str(e)}")
        return Response(
            {"errors": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
