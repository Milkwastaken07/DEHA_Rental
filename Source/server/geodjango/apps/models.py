from django.contrib.gis.db import models 
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

# Enums as TextChoices
class Highlight(models.TextChoices):
    HighSpeedInternetAccess = 'HighSpeedInternetAccess', 'High Speed Internet Access'
    WasherDryer = 'WasherDryer', 'Washer/Dryer'
    AirConditioning = 'AirConditioning', 'Air Conditioning'
    Heating = 'Heating', 'Heating'
    SmokeFree = 'SmokeFree', 'Smoke Free'
    CableReady = 'CableReady', 'Cable Ready'
    SatelliteTV = 'SatelliteTV', 'Satellite TV'
    DoubleVanities = 'DoubleVanities', 'Double Vanities'
    TubShower = 'TubShower', 'Tub/Shower'
    Intercom = 'Intercom', 'Intercom'
    SprinklerSystem = 'SprinklerSystem', 'Sprinkler System'
    RecentlyRenovated = 'RecentlyRenovated', 'Recently Renovated'
    CloseToTransit = 'CloseToTransit', 'Close to Transit'
    GreatView = 'GreatView', 'Great View'
    QuietNeighborhood = 'QuietNeighborhood', 'Quiet Neighborhood'

class Amenity(models.TextChoices):
    WasherDryer = 'WasherDryer', 'Washer/Dryer'
    AirConditioning = 'AirConditioning', 'Air Conditioning'
    Dishwasher = 'Dishwasher', 'Dishwasher'
    HighSpeedInternet = 'HighSpeedInternet', 'High Speed Internet'
    HardwoodFloors = 'HardwoodFloors', 'Hardwood Floors'
    WalkInClosets = 'WalkInClosets', 'Walk-In Closets'
    Microwave = 'Microwave', 'Microwave'
    Refrigerator = 'Refrigerator', 'Refrigerator'
    Pool = 'Pool', 'Pool'
    Gym = 'Gym', 'Gym'
    Parking = 'Parking', 'Parking'
    PetsAllowed = 'PetsAllowed', 'Pets Allowed'
    WiFi = 'WiFi', 'WiFi'

class PropertyType(models.TextChoices):
    Rooms = 'Rooms', 'Rooms'
    Tinyhouse = 'Tinyhouse', 'Tinyhouse'
    Apartment = 'Apartment', 'Apartment'
    Villa = 'Villa', 'Villa'
    Townhouse = 'Townhouse', 'Townhouse'
    Cottage = 'Cottage', 'Cottage'

class ApplicationStatus(models.TextChoices):
    Pending = 'Pending', 'Pending'
    Denied = 'Denied', 'Denied'
    Approved = 'Approved', 'Approved'

class PaymentStatus(models.TextChoices):
    Pending = 'Pending', 'Pending'
    Paid = 'Paid', 'Paid'
    PartiallyPaid = 'PartiallyPaid', 'Partially Paid'
    Overdue = 'Overdue', 'Overdue'

# Models

class Location(models.Model):
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postalCode = models.CharField(max_length=20, db_column='postalCode')
    coordinates = models.PointField()

    def __str__(self):
        return f"{self.address}, {self.city}, {self.state}"
    
    class Meta:
        db_table = 'Location'
        managed = True

class Manager(models.Model):
    id = models.AutoField(primary_key=True)
    cognitoId = models.CharField(max_length=255, unique=True, db_column='cognitoId')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phoneNumber = models.CharField(max_length=20, db_column='phoneNumber')

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'Manager'
        managed = True

class Tenant(models.Model):
    cognitoId = models.CharField(max_length=255, unique=True, db_column='cognitoId')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phoneNumber = models.CharField(max_length=20, db_column='phoneNumber')

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'Tenant'
        managed = True

class Property(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    name = models.CharField(max_length=255, db_column='name')
    description = models.TextField(db_column='description')
    pricePerMonth = models.FloatField(validators=[MinValueValidator(0.0)], db_column='pricePerMonth')
    securityDeposit = models.FloatField(validators=[MinValueValidator(0.0)], db_column='securityDeposit')
    applicationFee = models.FloatField(validators=[MinValueValidator(0.0)], db_column='applicationFee')
    photoUrls = ArrayField(models.URLField(), default=list, db_column='photoUrls')
    amenities = ArrayField(models.CharField(max_length=50, choices=Amenity.choices), default=list, db_column='amenities')
    highlights = ArrayField(models.CharField(max_length=50, choices=Highlight.choices), default=list, db_column='highlights')
    isPetsAllowed = models.BooleanField(default=False, db_column='isPetsAllowed')
    isParkingIncluded = models.BooleanField(default=False, db_column='isParkingIncluded')
    beds = models.PositiveIntegerField()
    baths = models.FloatField(validators=[MinValueValidator(0.0)])
    squareFeet = models.PositiveIntegerField(db_column='squareFeet')
    propertyType = models.CharField(max_length=20, choices=PropertyType.choices, db_column='propertyType')
    postedDate = models.DateTimeField(auto_now_add=True, db_column='postedDate')
    averageRating = models.FloatField(default=0.0, null=True, db_column='averageRating')
    numberOfReviews = models.PositiveIntegerField(default=0, null=True, db_column='numberOfReviews')
    locationId = models.ForeignKey(Location, on_delete=models.CASCADE, db_column='locationId')
    managerCognitoId = models.ForeignKey(Manager, on_delete=models.CASCADE, to_field='cognitoId', db_column='managerCognitoId')
    favoritedBy = models.ManyToManyField(Tenant, related_name='favorites', blank=True)
    tenants = models.ManyToManyField(Tenant, related_name='properties', blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'Property'
        managed = True

class Lease(models.Model):
    id = models.AutoField(primary_key=True)
    startDate = models.DateTimeField(db_column='startDate')
    endDate = models.DateTimeField(db_column='endDate')
    rent = models.FloatField(validators=[MinValueValidator(0.0)])
    deposit = models.FloatField(validators=[MinValueValidator(0.0)])
    propertyId = models.ForeignKey(Property, on_delete=models.CASCADE, db_column='propertyId')
    tenantCognitoId = models.ForeignKey(Tenant, on_delete=models.CASCADE, to_field='cognitoId', db_column='tenantCognitoId')

    def __str__(self):
        return f"Lease {self.id} for {self.property}"
    
    class Meta:
        db_table = 'Lease'
        managed = True

class Application(models.Model):
    id = models.AutoField(primary_key=True)
    applicationDate = models.DateTimeField()
    status = models.CharField(max_length=20)
    propertyId = models.ForeignKey(Property, on_delete=models.CASCADE)
    tenantCognitoId = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phoneNumber = models.CharField(max_length=20)  # Tăng độ dài để chứa được số điện thoại với dấu +
    message = models.TextField()
    leaseId = models.ForeignKey(Lease, on_delete=models.SET_NULL, null=True, blank=True)
    class Meta:
        db_table = 'Application'
        managed = True

class Payment(models.Model):
    id = models.AutoField(primary_key=True)
    amountDue = models.DecimalField(max_digits=10, decimal_places=2)
    amountPaid = models.DecimalField(max_digits=10, decimal_places=2)
    dueDate = models.DateTimeField()
    paymentDate = models.DateTimeField()
    paymentStatus = models.CharField(max_length=20)  # Paid, Pending, PartiallyPaid
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE)

    def __str__(self):
        return f"Payment {self.id} for Lease {self.lease}"
    
    class Meta:
        db_table = 'Payment'
        managed = True

