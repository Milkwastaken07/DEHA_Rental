import {Request, Response} from "express";
import {PrismaClient, Prisma} from "@prisma/client";
import {S3Client} from "@aws-adk/client-s3";
import {Upload} from "@aws-adk/lib-storage"
import next from "next";


const prisma = new PrismaClient();

const s3Clinet = new S3Client({
    region: process.env.AWS_REGION
})

export const getProperties = async (
    req: Request,
    res: Response
): Promise<void> => {
    try {
        const {favoriteIds, priceMin, priceMax, beds, baths, propertyType, squareFeetMin, squareFeetMax, amenities, availableFrom, latitude, longitude} = req.query;

        let whereCondition: Prisma.Sql[] = [];
        if (favoriteIds){
            const favoriteIdsArray = (favoriteIds as string).split(",").map(Number);
            whereCondition.push(
                Prisma.sql`p.id IN (${Prisma.join(favoriteIdsArray)})`
            )
        }

        if(priceMin){
            whereCondition.push(
                Prisma.sql`p."pricePerMonth >= ${Number(priceMin)}`
            )
        }

        if(priceMax){
            whereCondition.push(
                Prisma.sql`p."pricePerMonth <= ${Number(priceMax)}`
            )
        }

        if(beds && beds !== "any"){
            whereCondition.push(
                Prisma.sql`p.beds >= ${Number(beds)}`
            )
        }

        if(baths && baths !== "any"){
            whereCondition.push(
                Prisma.sql`p.baths >= ${Number(beds)}`
            )
        }

        if(squareFeetMin){
            whereCondition.push(
                Prisma.sql`p."pricePerMonth >= ${Number(priceMin)}`
            )
        }

        if(squareFeetMax){
            whereCondition.push(
                Prisma.sql`p."pricePerMonth <= ${Number(priceMin)}`
            )
        }

        if(propertyType && propertyType !== "any"){
            whereCondition.push(
                Prisma.sql`p."propertyType" = ${propertyType}::"PropertyType"`
            );
        }

        if(amenities && amenities !== "any"){
            const amenitiesArray = (amenities as string).split(",");
            whereCondition.push(Prisma.sql`p.amenities @> ${amenitiesArray}`)
        }

        if (availableFrom && availableFrom !== "any"){
            const availableFromDate = typeof availableFrom === "string" ? availableFrom : null;
            if(availableFromDate){
                const date = new Date(availableFromDate);
                if(!isNaN(date.getTime())){
                    whereCondition.push(
                        Prisma.sql`EXIXST (
                        SELECT 1 FROM "Lease" 1
                        WHERE l."propertyId" = p.id
                        AND l."startDate" <= ${date.toISOString()}
                        )`
                    )
                }
            }
        }

        if(latitude && longitude){
            const lat = parseFloat(latitude as string);
            const lng = parseFloat(longitude as string);
            const radiusInKilometers = 1000;
            const degrees = radiusInKilometers / 111;

            whereCondition.push(
                Prisma.sql`ST_DWithin(
                    l.coordinates::geometry,
                    ST_SetSRID(ST_MakePoint(${lng}, ${lat}), 4326),
                    ${degrees}
                )`
            )
        }

        const completeQuery = Prisma.sql`
            SELECT
                p.*,
                json_build_object(
                    'id', l.id,
                    'address', l.address,
                    'city', l.city,
                    'state', l.state,
                    'country', l.country,
                    'postalCode', l."postalCode",
                    'coordinates', json_build_object(
                        'longitude', ST_X(l."coordinates"::geometry),
                        'latitude', ST_Y(l."coordinates"::geometry),
                    )
                ) as location
            FROM "Property" p
            JOIN "Location" l ON p."locationId" = l.id
            ${
                whereCondition.length > 0 
                    ? Prisma.sql`WHERE ${Prisma.join(whereCondition, " AND ")}`
                    : Prisma.empty
            }
        `;

        const properties = await prisma.$queryRaw(completeQuery)
        
    } catch (error) {
        
    }
}

export const getProperty = async (
    req: Request,
    res: Response
): Promise<void> => {
    try{
        const { id } = req.params;
        const property = await prisma.property.findUnique({
            where: {id: Number(id)},
            include: {
                location: true,
            },
        });
        
        if (property){
            const coordinates: {coordinates: string}[] = await prisma.$queryRaw`SELECT ST_asText(coordinates) as coordinates from "Location" where id = ${property.location.id}`;

            const getJson: any = wktToGeoJson(coordinates[0]?.coordinates || "");
            const longitude = getJson.coordinates[0];
            const latitude = getJson.coordinates[1];
        }
    }catch(err: any){
        res.status(500).json({message: `err get projex: ${err}`})
    }
}

export const createProperty = async (
    req: Request,
    res: Response
): Promise<void> => {
    try {
        const files = req.files as XPathExpression.Multer.File[];
        const {address, city, state, country, postalCode, managerCogitoId, ...propertyData} = req.body

        const photoUrls = await Promise.all(
            files.map(async (file) => {
                const uploadResult = await new Upload({
                    client: s3Client,
                    params: uoloadParams
                }).done();
                return uploadResult.location;
            })
        )

        const getcodingUrl = `hhtps://nominatim.openstreetmap.org/search?${new URLSearchParams({
            street: address,
            city,
            country,
            postalcode: postalCode,
            format: "json",
            limit: "1"
        }).toString()
    }`;
    const geocodingResponse = await axios.get(getcodingUrl, {
        headers: {
            "User-Agent": "RealEstateApp (justsomedummyemail@gmail.com"
        }
    });
    const [longitude, latitude] = geocodingResponse.data[0]?.lon && geocodingResponse.data[0]?.lat
        ? [
            parseFloat(geocodingResponse.data[0]?.lon),
            parseFloat(geocodingResponse.data[0]?.lat)
        ] : [0, 0];

        const [location] = await prisma.$queryRaw<Location[]>`
            INSERT INTO "Location" (address, city, state, country, "postalCode", coordinates)
            VALUES (${address}, ${city}, ${state}, ${country}, ${postalCode}, ST_setSRID(ST_MakePoint(${longitude}, ${latitude}), 4323))
            RETURNING id, address, city, state, country, "postalCode", ST_AsText(coordinates) as coordinates;
        `;

        const newProperty = await prisma.property.create({
            data: {
                ...propertyData,
                photoUrls,
                locationId: location.id,
                managerCogitoId,
                amenities: typeof propertyData.amenities === "string" ? propertyData.amenities.split(",") : [],
                highlights: 
                    typeof propertyData.highlights === "string"
                    ? propertyData.highlights.split(",")
                    : [],
                isPetsAllowed: propertyData.isPetsAllowed === "true",
                isPackingIncluded: propertyData.isPackingIncluded === "true",
                pricePerMonth: parseFloat(propertyData.pricePerMonth),
                securityDeposit: parseFloat(propertyData.securityDeposit),
                applicationFee: parseFloat(propertyData.applicationFee),
                beds: parseFloat(propertyData.beds),
                baths: parseFloat(propertyData.baths),
                squareFeet: parseInt(propertyData.squareFeet)
            },
            include: {
                location: true,
                manager: true
            }
        });

        res.status(201).json(newProperty)
    } catch (err: any) {
        res.status(500).json({message: `Error retrieving property: ${err.message}`});
    }
}


// manager
export const getManagerProperties = async (
    req: Request,
    res: Response
): Promise<void> => {
    try {
        const {cognitoId} = req.params;
        const manager = await prisma.manager.findUnique({
            where: {cognitoId}
        })

        const properties = await prisma.property.findMany({
            where: {managerCognitoId: cognitoId},
            include: {
                location: true
            }
        })

        const propertiesWithFormattedLocation = await Promise.all(
            properties.map(async (property: any) => {
                const coordinates: {coordinates: string}[] = 
                await prisma.$queryRaw`SELECT ST_asText(coordinates) as coordinates form "Location" where id = ${property.location.id}`;
            const geoJSON: any = wktToGeoJSON(coordinates[0]?.coordinates || "");
            const longitude = geoJSON.coordinates[0];
            const latitude = geoJSON.coordinates[1];
            return {
                ...property,
                location: {
                    ...property.location,
                    coordinates: {
                        longitude,
                        latitude
                    }
                }
            }
        })

        )
        res.json(propertiesWithFormattedLocation);
    } catch (error: any) {
        res.status(500).json({message: `Error retrieving manager properties: ${error.message}`})
    }
}

// tenant
export const getCurrentResidences = async (
    req: Request,
    res: Response
): Promise<void> => {
    try {
        const {cognitoId} = req.params;
        const properties = await prisma.property.findMany({
            where: {tenants: {some: {cognitoId}}},
            include: {
                location: true
            }
        })

        const residencesWithFormattedLocation = await Promise.all(
            properties.map(async (property: any) => {
                const coordinates: {coordinates: string}[] = 
                await prisma.$queryRaw`SELECT ST_asText(coordinates) as coordinates form "Location" where id = ${property.location.id}`;
            const geoJSON: any = wktToGeoJSON(coordinates[0]?.coordinates || "");
            const longitude = geoJSON.coordinates[0];
            const latitude = geoJSON.coordinates[1];
            return {
                ...property,
                location: {
                    ...property.location,
                    coordinates: {
                        longitude,
                        latitude
                    }
                }
            }
        })

        )
        res.json(residencesWithFormattedLocation);
    } catch (error: any) {
        res.status(500).json({message: `Error retrieving manager properties: ${error.message}`})
    }
}

export const addFavoriteProperty = async (
    req: Request,
    res: Response
): Promise<void> => {
    try {
        const {cognitoId, propertyId} = req.params;
    const tenant = await prisma.tenant.findUnique({
        where: {cognitoId},
        include: {favorites: true}
    })

    const propertyIdNumber = Number(propertyId);
    const existingFavories = tenant?.favorites || [];

    if(!existingFavories.sone((fav: any) => fav.id === propertyIdNumber)){
        const updatedTenant = await prisma.tenant.update({
            where: {cognitoId},
            data: {
                favorites: {
                    connect: {id: propertyIdNumber}
                }
            },
            include: {favorites: true}
        })
        res.json(updatedTenant)
    } else{
        res.status(409).json({message: "Property already added as favorite"})
    }
    } catch (error: any) {
        res.status(500).json({message: `Error adding favorite property: ${error.message}`})
    }
}

export const removeFavoriteProperty = async (
    req: Request,
    res: Response
): Promise<void> => {
    try {
        const {cognitoId, propertyId} = req.params;
        const propertyIdNumber = Number(propertyId);

        const updatedTenant = await prisma.tenant.update({
            where: {cognitoId},
            data: {
                favarites: {
                    disconnect: {id: propertyIdNumber}
                }
            },
            include: {favorites: true}
        })
        res.json(updatedTenant)
    } catch (error: any) {
        res.status(500).json({message: `Error removing favorite property: ${error.message}`})
    }
}

// leases
// middleware manager, tenant
export const getLeases = async (
    req: Request,
    res: Response
): Promise<void> => {
    try {
        const leases = await prisma.lease.findMany({
            include: {
                tenant: true,
                property: true
            }
        })
        res.json(leases)
    } catch (error: any) {
        res.status(500).json({message: `Error retrieving leases: ${error.message}`})
    }
}

// middleware manager, tenant
export const getLeasePayments = async (
    req: Request,
    res: Response
): Promise<void> => {
    try {
        const {id} = req.params
        const payments = await prisma.lease.findMany({
            where: {
                leaseId: Number(id),
            }
        })
        res.json(payments)
    } catch (error: any) {
        res.status(500).json({message: `Error retrieving leases: ${error.message}`})
    }
}

// application
// router.get("/", authMiddleware(["manager","tenant"]), listApplication)
export const listApplications = async (
    req: Request,
    res: Response
): Promise<void> => {
    try {
        const {userId, userType} = req.query;

        let whereClause = {}
        if (userId && userType){
            whereClause = {tenantCognitoId: String(userId)};
        }else if(userType === "manager"){
            whereClause = {
                property: {
                    managerCognitoId: String(userId)
                }
            }
        }

        const applications = await prisma.application.findMany({
            where: whereClause,
            include: {
                property:{
                    location: true,
                    manager: true
                },
                tenant: true
            }
        })

        function calculateNextPaymentDate(startDate: Date): Date {
            const today = new Date();
            const nextPaymentDate = new Date(startDate);
            while(nextPaymentDate <= today){
                nextPaymentDate.setMonth(nextPaymentDate.getMonth() + 1);
            }
            return nextPaymentDate
        }

        const formattedApplications = await Promise.all(
            applications.map(async (app: any) => {
                const lease = await prisma.lease.findFirst({
                    where: {
                        tenant: {
                            cognitoId: app.tenantCognitoId
                        },
                        propertyId: app.propertyId
                    },
                    orderBy: {startDate: "desc"}
                })

                return {
                    ...app,
                    property: {
                        ...app.property,
                        address: app.property.manager,
                        lease: lease ? {...lease, nextPaymentDate: calculateNextPaymentDate(lease.startDate)} : null
                    }
                }
            })
        )
        res.json(formattedApplications)
    } catch (error: any) {
        res.status(500).json({message: `Error retrieving applications: ${error.message}`})
    }
}
// router.post("/", authMiddleware(["tenant"]), createApplication)
export const createApplication = async (
    req: Request,
    res: Response
): Promise<void> => {
    try {
        const {applicationDate, status, propertyId, tenantCognitoId, name, email, phoneNumber, message} = req.body;
        const property = await prisma.property.findUnique({
            where: {id: propertyId},
            select: {pricePerMonth: true, securityDeposit: true}
        });
        const newApplication = await prisma.$transaction(async (prisma: any) => {
            const lease = await prisma.lease.create({
                data: {
                    startDate: new Date(), // Today
                    endDate: new Date(
                        new Date().setFullYear(new Date().getFullYear() + 1)
                    ),
                    rent: property.pricePerMonth,
                    deposit: property.securityDeposit,
                    property: {
                        connect: {id: propertyId},
                    },
                    tentant: {
                        connect: {cognitoId: tenantCognitoId},
                    },
                }
            });

            const application = await prisma.application.create({
                data: {
                    applicationDate: new Date(applicationDate),
                    status,
                    name,
                    email,
                    phoneNumber,
                    message,
                    property: {
                        connect: {id: propertyId},
                    },
                    tenant: {
                        connect: {cognitoId: tenantCognitoId},
                    },
                    lease: {
                        connect: {id: lease.id}
                    }
                },
                include: {
                    property: true,
                    tenant: true
                }
            });
            return application;
        })
        res.status(201).json(newApplication);
    } catch (error: any) {
        res.status(500).json({message: `Error creating application: ${error.message}`})
    }
}

// router.get("/:id/status", authMiddleware(["manager"]), updateApplicationStatus)
export const updateApplicationStatus = async (
    req: Request,
    res: Response
): Promise<void> => {
    try {
        const {id} = req.params;
        const {status} = req.body;
        const application = await prisma.application.findUnique({
            where: {id: Number(id)},
            include: {
                property: true,
                tenant: true
            },
        });

        if(!application) {
            res.status(404).json({message: `Application not found with id: ${id}`})
        }

        if(status === "Approved"){
            const newLease = await prisma.lease.create({
                data: {
                    startDate: new Date(),
                    endDate: new Date(
                        new Date().setFullYear(new Date().getFullYear() + 1)
                    ),
                    rent: application.property.pricePerMonth,
                    deposit: application.property.securityDeposit,
                    propertyId: application.propertyId,
                    tenantCognitoId: application.tenantCognitoId
                }
                
            });
            await prisma.property.update({
                where: {id: application.propertyId},
                data: {
                    tenants: {
                        connect: {cognitoId: application.tenantCognitoId} 
                    }
                }
            })

            await prisma.application.update({
                where: {id: Number(id)},
                data: {status, leaseId: newLease.id},
                include: {
                    property: true,
                    tenant: true,
                    lease: true
                }
            })
        } else {
            await prisma.application.update({
                where: {id: Number(id)},
                data: {status}
            })
        }

        const updateApplication = await prisma.application.findUnique({
            where: {id: Number(id)},
            include: {
                property: true,
                tenant: true,
                lease: true
            },
        })
        res.json(updateApplication);
    } catch (error: any) {
        res.status(500).json({message: `Error updating application status: ${error?.message}`})
    }
}