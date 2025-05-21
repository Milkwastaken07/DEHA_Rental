// Enums
export enum HighlightEnum {
    HighSpeedInternetAccess = 'HighSpeedInternetAccess',
    WasherDryer = 'WasherDryer',
    AirConditioning = 'AirConditioning',
    Heating = 'Heating',
    SmokeFree = 'SmokeFree',
    CableReady = 'CableReady',
    SatelliteTV = 'SatelliteTV',
    DoubleVanities = 'DoubleVanities',
    TubShower = 'TubShower',
    Intercom = 'Intercom',
    SprinklerSystem = 'SprinklerSystem',
    RecentlyRenovated = 'RecentlyRenovated',
    CloseToTransit = 'CloseToTransit',
    GreatView = 'GreatView',
    QuietNeighborhood = 'QuietNeighborhood'
}

export enum AmenityEnum {
    WasherDryer = 'WasherDryer',
    AirConditioning = 'AirConditioning',
    Dishwasher = 'Dishwasher',
    HighSpeedInternet = 'HighSpeedInternet',
    HardwoodFloors = 'HardwoodFloors',
    WalkInClosets = 'WalkInClosets',
    Microwave = 'Microwave',
    Refrigerator = 'Refrigerator',
    Pool = 'Pool',
    Gym = 'Gym',
    Parking = 'Parking',
    PetsAllowed = 'PetsAllowed',
    WiFi = 'WiFi'
}

export enum PropertyType {
    Rooms = 'Rooms',
    Tinyhouse = 'Tinyhouse',
    Apartment = 'Apartment',
    Villa = 'Villa',
    Townhouse = 'Townhouse',
    Cottage = 'Cottage'
}

export enum ApplicationStatus {
    Pending = 'Pending',
    Denied = 'Denied',
    Approved = 'Approved'
}

export enum PaymentStatus {
    Pending = 'Pending',
    Paid = 'Paid',
    PartiallyPaid = 'PartiallyPaid',
    Overdue = 'Overdue'
}

// Models
export interface Location {
    id: number;
    address: string;
    city: string;
    state: string;
    country: string;
    postalCode: string;
    coordinates: {
        latitude: number;
        longitude: number;
    };
}

export interface Manager {
    id: number;
    cognitoId: string;
    name: string;
    email: string;
    phoneNumber: string;
}

export interface Tenant {
    id: number;
    cognitoId: string;
    name: string;
    email: string;
    phoneNumber: string;
}

export interface Property {
    id: number;
    name: string;
    description: string;
    pricePerMonth: number;
    securityDeposit: number;
    applicationFee: number;
    photoUrls: string[];
    amenities: AmenityEnum[];
    highlights: HighlightEnum[];
    isPetsAllowed: boolean;
    isParkingIncluded: boolean;
    beds: number;
    baths: number;
    squareFeet: number;
    propertyType: PropertyType;
    postedDate: Date;
    averageRating: number | null;
    numberOfReviews: number | null;
    locationId: number;
    managerCognitoId: string;
    favoritedBy: string[];
    tenants: string[];
}

export interface Lease {
    id: number;
    startDate: Date;
    endDate: Date;
    rent: number;
    deposit: number;
    propertyId: number;
    tenantCognitoId: string;
}

export interface Application {
    id: number;
    applicationDate: string;
    status: ApplicationStatus;
    propertyId: number;
    tenantCognitoId: string;
    name: string;
    email: string;
    phoneNumber: string;
    message: string;
    leaseId?: number;
}

export interface Payment {
    id: number;
    amountDue: number;
    amountPaid: number;
    dueDate: Date;
    paymentDate: Date;
    paymentStatus: PaymentStatus;
    leaseId: number;
}