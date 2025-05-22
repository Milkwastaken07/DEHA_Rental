from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from core.authMiddleware import jwt_auth
from apps.models import Property, Lease, Location
from .serializers import *
from dateutil import parser
from django.db.models import Exists, OuterRef
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from rest_framework.response import Response
import logging
from rest_framework import status
from rest_framework import generics
import requests
from django.core.files.storage import FileSystemStorage
from rest_framework.permissions import IsAuthenticated
import json


from django.http import JsonResponse
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.db.models import Q
from django.views.decorators.http import require_GET
from apps.models import Property, Location, Lease
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes

@api_view(["GET"])
@permission_classes([AllowAny])
def get_properties(request):
    try:
        # Lấy tham số truy vấn
        favorite_ids = request.GET.get('favoriteIds', '')
        price_min = request.GET.get('priceMin', 0)
        price_max = request.GET.get('priceMax', 0)
        beds = request.GET.get('beds', 0)
        baths = request.GET.get('baths', 0)
        property_type = request.GET.get('propertyType', 'any')
        square_feet_min = request.GET.get('squareFeetMin', 0)
        square_feet_max = request.GET.get('squareFeetMax', 0)
        amenities = request.GET.get('amenities', 'any')
        available_from = request.GET.get('availableFrom', 'any')
        latitude = request.GET.get('latitude', 0)
        longitude = request.GET.get('longitude', 0)

        # Bắt đầu với tất cả bất động sản
        queryset = Property.objects.select_related('locationId')  # Changed from 'location' to 'locationId'

        # Lọc dữ liệu
        if favorite_ids:
            favorite_ids_array = [int(id) for id in favorite_ids.split(',') if id.isdigit()]
            queryset = queryset.filter(id__in=favorite_ids_array)

        if price_min:
            queryset = queryset.filter(price_per_month__gte=float(price_min))

        if price_max:
            queryset = queryset.filter(price_per_month__lte=float(price_max))

        if beds and beds != 'any':
            queryset = queryset.filter(beds__gte=int(beds))

        if baths and baths != 'any':
            queryset = queryset.filter(baths__gte=int(baths))

        if square_feet_min:
            queryset = queryset.filter(square_feet__gte=int(square_feet_min))

        if square_feet_max:
            queryset = queryset.filter(square_feet__lte=int(square_feet_max))

        if property_type and property_type != 'any':
            queryset = queryset.filter(property_type=property_type)

        if amenities and amenities != 'any':
            amenities_array = amenities.split(',')
            queryset = queryset.filter(amenities__contains=amenities_array)

        if available_from and available_from != 'any':
            try:
                date = datetime.strptime(available_from, '%Y-%m-%d').date()
                queryset = queryset.filter(lease__start_date__lte=date).distinct()
            except ValueError:
                pass

        if latitude and longitude:
            try:
                lat = float(latitude)
                lng = float(longitude)
                # Convert kilometers to degrees (approximately 1 degree = 111 kilometers at the equator)
                radius_in_degrees = 1000 / 111.0  # Convert 1000km to degrees
                reference_point = Point(float(longitude), float(latitude), srid=4326)
                queryset = queryset.filter(
                    locationId__coordinates__dwithin=(reference_point, radius_in_degrees)  # Use degrees instead of Distance(km=)
                )
            except ValueError:
                pass

        # Chuẩn bị dữ liệu trả về
        properties = Property.objects.all()
        serializer = PropertySerializer(properties, many=True).data
        # properties = PropertySerializer(data)
        # for property in queryset:
        #     location = property.locationId  # Changed from location to locationId
        #     properties.append({
        #         'id': property.id,
        #         'pricePerMonth': float(property.price_per_month),
        #         'beds': property.beds,
        #         'baths': property.baths,
        #         'squareFeet': property.square_feet,
        #         'propertyType': property.property_type,
        #         'amenities': property.amenities,
        #         'location': {
        #             'id': location.id,
        #             'address': location.address,
        #             'city': location.city,
        #             'state': location.state,
        #             'country': location.country,
        #             'postalCode': location.postal_code,
        #             'coordinates': {
        #                 'longitude': location.coordinates.x,
        #                 'latitude': location.coordinates.y,
        #             }
        #         }
        #     })

        # Return the formatted properties list instead of the queryset
        return JsonResponse({'properties': serializer}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

class PropertyViewDetails(generics.RetrieveAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = Property.objects.select_related('locationId').get(id=self.kwargs['id'])
            serializer = self.get_serializer(instance)

            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        except Property.DoesNotExist:
            return Response(
                {"errors": "Property not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logging.error(f"Error retrieving property: {str(e)}")
            return Response(
                {"errors": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# @permission_classes(['manager'])
@api_view(["POST"])
@permission_classes([AllowAny])
def perform_create(request):
        try:
            # Lấy dữ liệu từ request
            data = request.data
            files = request.FILES.getlist('photos')  # Nhiều file ảnh
            address = data.get('address')
            city = data.get('city')
            state = data.get('state')
            country = data.get('country')
            postalCode = data.get('postalCode')
            managerCognitoId = data.get('managerCognitoId')
            # Upload ảnh vào thư mục upload
            fs = FileSystemStorage(location='upload/')
            photo_urls = []
            for file in files:
                filename = fs.save(file.name, file)
                photo_urls.append(fs.url(filename))

            # Gọi Nominatim API để lấy tọa độ
            geocoding_url = (
                f"https://nominatim.openstreetmap.org/search?"
                f"street={address}&city={city}&country={country}&postalcode={postalCode}"
                f"&format=json&limit=1"
            )
            headers = {"User-Agent": "RealEstateApp (justsomedummyemail@gmail.com)"}
            response = requests.get(geocoding_url, headers=headers)
            response.raise_for_status()
            geocoding_data = response.json()

            longitude = float(geocoding_data[0]['lon']) if geocoding_data else 0
            latitude = float(geocoding_data[0]['lat']) if geocoding_data else 0

            # Tạo Location
            location = Location.objects.create(
                address=address,
                city=city,
                state=state,
                country=country,
                postalCode=postalCode,
                coordinates=Point(longitude, latitude, srid=4326)
            )

            # Lưu Property
            property = Property.objects.create(
                photoUrls=photo_urls,
                locationId=location,
                managerCognitoId=managerCognitoId,  # Giả sử user có manager
                isPetsAllowed=str(data.get('isPetsAllowed', 'false')).lower() == 'true',
                isParkingIncluded=str(data.get('isParkingIncluded', 'false')).lower() == 'true',
                pricePerMonth=float(data.get('pricePerMonth', 0)),
                securityDeposit=float(data.get('securityDeposit', 0)),
                applicationFee=float(data.get('applicationFee', 0)),
                beds=int(data.get('beds', 0)),
                baths=float(data.get('baths', 0)),
                squareFeet=int(data.get('squareFeet', 0))
            )
            serializer = PropertySerializer(property).data
            return Response({"data": serializer}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logging.error(f"Error creating property: {str(e)}")
            raise serializers.ValidationError({"errors": str(e)})
      
# class PropertyCreateView(generics.CreateAPIView):
#     queryset = Property.objects.all()
#     serializer_class = PropertySerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         try:
#             # Lấy dữ liệu từ request
#             data = self.request.data
#             files = self.request.FILES.getlist('photos')  # Nhiều file ảnh
#             address = data.get('address')
#             city = data.get('city')
#             state = data.get('state')
#             country = data.get('country')
#             postalCode = data.get('postalCode')
#             managerCognitoId = data.get('managerCognitoId')
#             # Upload ảnh vào thư mục upload
#             fs = FileSystemStorage(location='upload/')
#             photo_urls = []
#             for file in files:
#                 filename = fs.save(file.name, file)
#                 photo_urls.append(fs.url(filename))

#             # Gọi Nominatim API để lấy tọa độ
#             geocoding_url = (
#                 f"https://nominatim.openstreetmap.org/search?"
#                 f"street={address}&city={city}&country={country}&postalcode={postalCode}"
#                 f"&format=json&limit=1"
#             )
#             headers = {"User-Agent": "RealEstateApp (justsomedummyemail@gmail.com)"}
#             response = requests.get(geocoding_url, headers=headers)
#             response.raise_for_status()
#             geocoding_data = response.json()

#             longitude = float(geocoding_data[0]['lon']) if geocoding_data else 0
#             latitude = float(geocoding_data[0]['lat']) if geocoding_data else 0

#             # Tạo Location
#             location = Location.objects.create(
#                 address=address,
#                 city=city,
#                 state=state,
#                 country=country,
#                 postalCode=postalCode,
#                 coordinates=Point(longitude, latitude, srid=4326)
#             )

#             # Lưu Property
#             serializer.save(
#                 photoUrls=photo_urls,
#                 locationId=location,
#                 managerCognitoId=managerCognitoId,  # Giả sử user có manager
#                 isPetsAllowed=data.get('isPetsAllowed', 'false').lower() == 'true',
#                 isParkingIncluded=data.get('isParkingIncluded', 'false').lower() == 'true',
#                 pricePerMonth=float(data.get('pricePerMonth', 0)),
#                 securityDeposit=float(data.get('securityDeposit', 0)),
#                 applicationFee=float(data.get('applicationFee', 0)),
#                 beds=int(data.get('beds', 0)),
#                 baths=float(data.get('baths', 0)),
#                 squareFeet=int(data.get('squareFeet', 0))
#             )
#         except Exception as e:
#             logging.error(f"Error creating property: {str(e)}")
#             raise serializers.ValidationError({"errors": str(e)})
        
# const storage = multer.memoryStorage()
# const upload = multer({storage: storage})

# router.post(
#     "/",
#     authMiddleware(["manager"]),
#     upload.array("photos"),
#     createProperty
# )

# let whereConditions: Prisma.Sql[] = []
# if(favoriteIds){
#     const favoriteIdsArray = (favoriteIds as string).split(",").map(Number);
#     whereConditions.push(
#         Prisma.sql`p.id IN (${Prisma.join(favoriteIdsArray)})`
#     )
# }

# if (propertyType && propertyType !== "any"){
#     whereConditions.push(
#         Prisma.sql`p."propertyType" = ${propertyType}::"propertyType"`
#     )
# }

# if (amenities && amenities !== "any"){
#     const amenitiesArray = (amenities as string).split(",");
#     whereConditions.push(
#         Prisma.sql`p."amenities" @> ${amenitiesArray}`
#     )
# }

# const date = new Date(availabelFromDate)
# if(!isNaN(date.getTime())){
#    whereConditions.push(
#        Prisma.sql`EXISTS(
#            SELECT 1 FROM "Lease" l
#            WHERE l."propertyId" = p.id
#            AND l."startDate" <= ${date.toISOString()}
#        )`
#    )
# }

# if (latitude && longitude){
#     const lat = parseFloat(latitude as string);
#     const lng = parseFloat(longitude as string);
#     const radiusInKilometers = 1000;
#     const degress = radiusInKilometers / 111;

#     whereConditions.push(
#         Prisma.sql`ST_DWithin(
#             l.coordinates::geometry,
#             ST_SetSRID(ST_MakePoint(${lng}, ${lat}, 4326),
#             ${degress}
#             )
#         )`
#     )
# }

