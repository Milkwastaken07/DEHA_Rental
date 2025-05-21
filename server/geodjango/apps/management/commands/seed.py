from django.core.management.base import BaseCommand
from django.db import transaction
from pathlib import Path
from django.core.exceptions import ObjectDoesNotExist
import json
from apps.models import *
from typing import List

class Command(BaseCommand):
    help = 'Seed database with initial data'

    @staticmethod
    def capitalizeFirstLetter(s: str) -> str:
        return s[0].upper() + s[1:] if s else ""
    
    @staticmethod
    def lowercaseFirstLetter(s: str) -> str:
        return s[0].lower() + s[1:] if s else ""
    
    def insertLocationData(self, locations: List[tuple]) -> str:
        for location in locations:
            id, country, city, state, address, postalCode, coordinates = location
            try:
                Location.objects.create(
                    id=id,
                    country=country,
                    city=city,
                    state=state,
                    address=address,
                    postalCode=postalCode,
                    coordinates=coordinates
                )
            except Exception as e:
                raise e
        return "Insert Location data successfully"

    def insertManagerData(self, managers: List[tuple]) -> str:
        for manager in managers:
            id, cognitoId, name, email, phoneNumber = manager
            try:
                Manager.objects.create(
                    id=id,
                    cognitoId=cognitoId,
                    name=name,
                    email=email,
                    phoneNumber=phoneNumber
                )
            except Exception as e:
                raise e
        return "Insert Manager data successfully"
    
    def insertTenantData(self, tenants: List[tuple]) -> str:
        for tenant in tenants:  
            id, cognitoId, name, email, phoneNumber, properties, favorites = tenant
            try:
                tenant_obj = Tenant.objects.create(
                    id=id,
                    cognitoId=cognitoId,
                    name=name,
                    email=email,
                    phoneNumber=phoneNumber
                )
                            # Gán các quan hệ many-to-many
                if properties in tenant:
                    property_objs = Property.objects.filter(id__in=properties)
                    tenant_obj.properties.set(property_objs)

                if favorites in tenant:
                    favorite_objs = Property.objects.filter(id__in=favorites)
                    tenant_obj.favorites.set(favorite_objs)
            except Exception as e:
                raise e
        return "Insert Tenant data successfully"

    def insertPropertyData(self, properties: List[tuple]) -> str:
        for property in properties:
            id, name, description, pricePerMonth, securityDeposit, applicationFee, photoUrls, amenities, highlights, isPetsAllowed, isParkingIncluded, beds, baths, squareFeet, propertyType, postedDate, averageRating, numberOfReviews, locationId, managerCognitoId = property
            try:
                Property.objects.create(
                    id=id,
                    name=name,
                    description=description,
                    pricePerMonth=pricePerMonth,
                    securityDeposit=securityDeposit,
                    applicationFee=applicationFee,
                    photoUrls=photoUrls,
                    amenities=amenities,
                    highlights=highlights,
                    isPetsAllowed=isPetsAllowed,
                    isParkingIncluded=isParkingIncluded,
                    beds=beds,
                    baths=baths,
                    squareFeet=squareFeet,
                    propertyType=propertyType,
                    postedDate=postedDate,
                    averageRating=averageRating,
                    numberOfReviews=numberOfReviews,
                    locationId=locationId,
                    managerCognitoId=managerCognitoId
                )
            except Exception as e:
                raise e
        return "Insert Property data successfully"
    
    def insertLeaseData(self, leases: List[tuple]) -> str:
        for lease in leases:
            id, startDate, endDate, rent, deposit, propertyId, tenantCognitoId = lease
            try:
                Lease.objects.create(
                    id=id,
                    startDate=startDate,
                    endDate=endDate,
                    rent=rent,
                    deposit=deposit,
                    propertyId=propertyId,
                    tenantCognitoId=tenantCognitoId
                )
            except Exception as e:
                raise e
        return "Insert Lease data successfully"

    def insertApplicationData(self, applications: List[tuple]) -> str:
        for application in applications:
            id, applicationDate, status, propertyId, tenantCognitoId, name, email, phoneNumber, message, leaseId = application
            try:
                Application.objects.create(
                    id=id,
                    applicationDate=applicationDate,
                    status=status,
                    propertyId=propertyId,
                    tenantCognitoId=tenantCognitoId,
                    name=name,
                    email=email,
                    phoneNumber=phoneNumber,
                    message=message,
                    leaseId=leaseId
                )
            except Exception as e:
                raise e
        return "Insert Application data successfully"
    
    def insertPaymentData(self, payments: List[tuple]) -> str:
        for payment in payments:
            amountDue, amountPaid, dueDate, paymentDate, paymentStatus, leaseId = payment
            try:
                Payment.objects.create(
                    amountDue=amountDue,
                    amountPaid=amountPaid,
                    dueDate=dueDate,
                    paymentDate=paymentDate,
                    paymentStatus=paymentStatus,
                    lease_id=leaseId
                )
            except Exception as e:
                raise e
        return "Insert Payment data successfully"

    def handle(self, *args, **options):
        data_directory = Path(__file__).resolve().parent.parent.parent / 'seedData'
        self.stdout.write(self.style.SUCCESS(f'Reading data from directory: {data_directory}'))
        
        # Order of loading data to avoid foreign key issues
        model_files = [
            ('location.json', Location),
            ('manager.json', Manager),
            ('property.json', Property),
            ('tenant.json', Tenant),
            ('lease.json', Lease),
            ('application.json', Application),
            ('payment.json', Payment),
        ]

        try:
            with transaction.atomic():
                for filename, model in model_files:
                    file_path = data_directory / filename
                    self.stdout.write(f'Processing file: {filename} for model: {model.__name__}')
                    
                    if file_path.exists():
                        with open(file_path, 'r') as file:
                            data = json.load(file)
                            self.stdout.write(f'Loaded {len(data)} records from {filename}')
                            
                            # Chuyển đổi data thành tuple để phù hợp với các hàm insert
                            if filename == 'location.json':
                                locations = [(item['id'], item['country'], item['city'], item['state'], 
                                            item['address'], item['postalCode'], item['coordinates']) 
                                           for item in data]
                                self.insertLocationData(locations)
                                
                            elif filename == 'manager.json':
                                managers = [(item['id'], item['cognitoId'], item['name'], 
                                           item['email'], item['phoneNumber']) 
                                          for item in data]
                                self.insertManagerData(managers)
                                
                            elif filename == 'tenant.json':
                                tenants = [(item['id'], item['cognitoId'], item['name'], 
                                          item['email'], item['phoneNumber'], item['properties'], item['favorites']) 
                                         for item in data]
                                self.insertTenantData(tenants)
                                
                            elif filename == 'property.json':
                                properties = []
                                for item in data:
                                    try:
                                        # Lấy instance của Location dựa trên locationId
                                        location = Location.objects.get(id=item['locationId'])
                                        magager = Manager.objects.get(cognitoId=item['managerCognitoId'])
                                    except ObjectDoesNotExist:
                                        print(f"Location with id {item['locationId']} does not exist. Skipping this property.")
                                        continue  # Bỏ qua nếu Location không tồn tại
                                    # Tạo tuple với instance của Location thay vì locationId
                                    property_data = (
                                        item['id'],
                                        item['name'],
                                        item['description'],
                                        item['pricePerMonth'],
                                        item['securityDeposit'],
                                        item['applicationFee'],
                                        item['photoUrls'],
                                        item['amenities'],
                                        item['highlights'],
                                        item['isPetsAllowed'],
                                        item['isParkingIncluded'],
                                        item['beds'],
                                        item['baths'],
                                        item['squareFeet'],
                                        item['propertyType'],
                                        item['postedDate'],
                                        item['averageRating'],
                                        item['numberOfReviews'],
                                        location,  # Gán instance của Location thay vì item['locationId']
                                        magager
                                    )
                                    properties.append(property_data)
                                
                                self.insertPropertyData(properties)
                                
                            elif filename == 'lease.json':
                                leases = []
                                for item in data:
                                    try:
                                        # Lấy instance của Property dựa trên propertyId
                                        property_instance = Property.objects.get(id=item['propertyId'])
                                        tenantCognito = Tenant.objects.get(cognitoId=item['tenantCognitoId'])
                                    except ObjectDoesNotExist:
                                        print(f"Property with id {item['propertyId']} does not exist. Skipping this lease.")
                                        continue  # Bỏ qua nếu Property không tồn tại

                                    # Tạo tuple với instance của Property thay vì propertyId
                                    lease_data = (
                                        item['id'],
                                        item['startDate'],
                                        item['endDate'],
                                        item['rent'],
                                        item['deposit'],
                                        property_instance,  # Gán instance của Property thay vì item['propertyId']
                                        tenantCognito
                                    )
                                    leases.append(lease_data)
                                
                                self.insertLeaseData(leases)
                                
                            elif filename == 'application.json':
                                applications = []
                                for item in data:
                                    try:
                                        # Lấy instance của Property dựa trên propertyId
                                        property_instance = Property.objects.get(id=item['propertyId'])
                                    except ObjectDoesNotExist:
                                        print(f"Property with id {item['propertyId']} does not exist. Skipping this application.")
                                        continue  # Bỏ qua nếu Property không tồn tại

                                    # Lấy instance của Lease dựa trên leaseId (nếu leaseId tồn tại)
                                    lease_instance = None
                                    if 'leaseId' in item and item['leaseId']:  # Kiểm tra xem leaseId có giá trị hay không
                                        try:
                                            lease_instance = Lease.objects.get(id=item['leaseId'])
                                        except ObjectDoesNotExist:
                                            print(f"Lease with id {item['leaseId']} does not exist. Skipping this application.")
                                            continue  # Bỏ qua nếu Lease không tồn tại

                                    # Tạo tuple với instance của Property và Lease thay vì ID
                                    application_data = (
                                        item['id'],
                                        item['applicationDate'],
                                        item['status'],
                                        property_instance,  # Gán instance của Property
                                        item['tenantCognitoId'],
                                        item['name'],
                                        item['email'],
                                        item['phoneNumber'],
                                        item['message'],
                                        lease_instance  # Gán instance của Lease (hoặc None nếu không có)
                                    )
                                    applications.append(application_data)
                                
                                self.insertApplicationData(applications)
                                
                            elif filename == 'payment.json':
                                payments = [(item['amountDue'], item['amountPaid'], item['dueDate'], 
                                          item['paymentDate'], item['paymentStatus'], item['leaseId']) 
                                         for item in data]
                                self.insertPaymentData(payments)

            self.stdout.write(self.style.SUCCESS('Successfully seeded database'))
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error seeding database: {str(e)}\n'
                    f'Error type: {type(e).__name__}'
                )
            )
            raise