"use client";
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { fetchAuthSession, getCurrentUser } from "aws-amplify/auth";
import { Application, Lease, Manager, Payment, Property, Tenant } from "@/types/models";
import { cleanParams, createNewUserInDatabase, withToast } from "@/lib/utils";
import { FiltersState } from ".";

export const api = createApi({
  baseQuery: fetchBaseQuery({
    baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL,
    prepareHeaders: async (headers) => {
      const session = await fetchAuthSession();
      const { idToken } = session.tokens ?? {};
      if (idToken) {
        headers.set("Authorization", `Bearer ${idToken}`);
      }
      return headers;
    },
  }),
  reducerPath: "api",
  tagTypes: [
    "Managers",
    "Tenants",
    "Properties",
    "PropertyDetails",
    "Leases",
    "Payments",
    "Applications",
  ],
  endpoints: (build) => ({
    getAuthUser: build.query<User, void>({
      queryFn: async (_, _queryApi, _extraoptions, fetchWithBQ) => {
        try {
          const session = await fetchAuthSession();
          const { idToken } = session.tokens ?? {};
          const user = await getCurrentUser();
          const userRole = idToken?.payload["custom:role"] as string;

          const endpoint =
            userRole === "manager"
              ? `managers/${user.userId}`
              : `tenants/${user.userId}`;
          console.log("User role: ", userRole);
          let userDetailsRespone = await fetchWithBQ(endpoint);
          // if user doesn't exist, create new user
          if (userDetailsRespone.error && userDetailsRespone.error.status === 404) {
              console.log("User doesn't exist in database, creating new user: ", );
              userDetailsRespone = await createNewUserInDatabase(
                user,
                idToken,
                userRole,
                fetchWithBQ
              );
            } 
          return {
            data: {
              cognitoInfo: { ...user },
              userInfo: userDetailsRespone.data as Manager,
              userRole,
            },
          };
        } catch (error: any) {
          return { error: error.message || "Couldn't not fetch user data" };
        }
      },
    }),

    updateTenantSettings: build.mutation<
      Tenant,
      { cognitoId: string } & Partial<Tenant>
    >({
      query: ({ cognitoId, ...updatedTenant }) => ({
        url: `tenants/${cognitoId}/update`,
        method: "PUT",
        body: updatedTenant,
      }),
      invalidatesTags: (result) => [{ type: "Tenants", id: result?.id }],
    }),

    // Property related endpoints
    getProperties: build.query<
      {properties: Property[]},
      Partial<FiltersState> & { favoriteIds?: number[] }
    >({
      query: (filters) => {
        const params = cleanParams({
          location: filters.location,
          priceMin: filters.priceRange?.[0],
          priceMax: filters.priceRange?.[1],
          beds: filters.beds,
          baths: filters.baths,
          propertyType: filters.propertyType,
          squareFeetMin: filters.squareFeet?.[0],
          squareFeetMax: filters.squareFeet?.[1],
          amenities: filters.amenities?.join(","),
          availableFrom: filters.availableFrom,
          favoriteIds: filters.favoriteIds?.join(","),
          latitude: filters.coordinates?.[0],
          longitude: filters.coordinates?.[1],
        });
        return { url: "properties", params };
      },
      providesTags: (result) =>
        Array.isArray(result) && result.length > 0
          ? [
              ...result.map(({ id }) => ({ type: "Properties" as const, id })),
              { type: "Properties", id: "LIST" },
            ]
          : [{ type: "Properties", id: "LIST" }],
      async onQueryStarted(_, { queryFulfilled }) {
        await withToast(queryFulfilled, {
          error: "Failed to fetch properties.",
        });
      },
    }),

    getProperty: build.query<Property, number>({
      query: (id) => `properties/${id}`,
      providesTags: (result, error, id) => [{ type: "PropertyDetails", id }],
      async onQueryStarted(_, { queryFulfilled }) {
        await withToast(queryFulfilled, {
          error: "Failed to load property details.",
        });
      },
    }),
    // Tenant related endpoints
    getTenant: build.query<Tenant, string>({
      query: (cognitoId) => `tenants/${cognitoId}`,
      providesTags: (result) => [{ type: "Tenants", id: result?.id }],
    }),

    getCurrentResidences: build.query<{properties: Property[]}, string>({
      query: (cognitoId) => `tenants/${cognitoId}/current-residences`,
      providesTags: (result) =>
        result
          ? [
              ...result.properties.map(({ id }) => ({ type: "Properties" as const, id })),
              { type: "Properties", id: "LIST" },
            ]
          : [{ type: "Properties", id: "LIST" }],
      async onQueryStarted(_, { queryFulfilled }) {
        await withToast(queryFulfilled, {
          error: "Failed to fetch current residences.",
        });
      },
    }),

    // add favorite property to tenant's favorite list
    addFavoriteProperty: build.mutation<
      Tenant,
      { cognitoId: string; propertyId: number }
    >({
      query: ({ cognitoId, propertyId }) => ({
        url: `tenants/${cognitoId}/favorites/${propertyId}`,
        method: "POST",
      }),
      invalidatesTags: (result) => [
        { type: "Tenants", id: result?.id },
        { type: "Properties", id: "LIST" },
      ],
    }),

    // remove favorite property from tenant's favorite list
    removeFavoriteProperty: build.mutation<
      Tenant,
      { cognitoId: string; propertyId: number }
    >({
      query: ({ cognitoId, propertyId }) => ({
        url: `tenants/${cognitoId}/favorites/${propertyId}`,
        method: "DELETE",
      }),
      invalidatesTags: (result) => [
        { type: "Tenants", id: result?.id },
        { type: "Properties", id: "LIST" },
      ],
    }),

    // manager related endpoints
    getManagerProperties: build.query<Property[], string>({
      query: (cognitoId) => `managers/${cognitoId}/properties`,
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: "Properties" as const, id })),
              { type: "Properties", id: "LIST" },
            ]
          : [{ type: "Properties", id: "LIST" }],
      async onQueryStarted(_, { queryFulfilled }) {
        await withToast(queryFulfilled, {
          error: "Failed to load manager profile.",
        });
      },
    }),

    updateManagerSettings: build.mutation<
      Manager,
      { cognitoId: string } & Partial<Manager>
    >({
      query: ({ cognitoId, ...updatedManager }) => ({
        url: `managers/${cognitoId}/update`,
        method: "PUT",
        body: updatedManager,
      }),
      invalidatesTags: (result) => [{ type: "Managers", id: result?.id }],
      async onQueryStarted(_, { queryFulfilled }) {
        await withToast(queryFulfilled, {
          success: "Settings updated successfully!",
          error: "Failed to update settings.",
        });
      },
    }),

    createProperty: build.mutation<Property, FormData>({
      query: (newProperty) => ({
        url: `properties`,
        method: "POST",
        body: newProperty,
      }),
      invalidatesTags: (result) => [
        { type: "Properties", id: "LIST" },
        { type: "Managers", id: result?.manager?.id },
      ],
      async onQueryStarted(_, { queryFulfilled }) {
        await withToast(queryFulfilled, {
          success: "Property created successfully!",
          error: "Failed to create property.",
        });
      },
    }),

        // lease related enpoints
        getLeases: build.query<Lease[], number>({
          query: () => "leases",
          providesTags: ["Leases"],
          async onQueryStarted(_, { queryFulfilled }) {
            await withToast(queryFulfilled, {
              error: "Failed to fetch leases.",
            });
          },
        }),
    
        getPropertyLeases: build.query<Lease[], number>({
          query: (propertyId) => `properties/${propertyId}/leases`,
          providesTags: ["Leases"],
          async onQueryStarted(_, { queryFulfilled }) {
            await withToast(queryFulfilled, {
              error: "Failed to fetch property leases.",
            });
          },
        }),
    
        getPayments: build.query<Payment[], number>({
          query: (leaseId) => `leases/${leaseId}/payments`,
          providesTags: ["Payments"],
          async onQueryStarted(_, { queryFulfilled }) {
            await withToast(queryFulfilled, {
              error: "Failed to fetch payment info.",
            });
          },
        }),

     // application related endpoints
     getApplications: build.query<
     Application[],
     { userId?: string; userType?: string }
   >({
     query: (params) => {
       const queryParams = new URLSearchParams();
       if (params.userId) {
         queryParams.append("userId", params.userId.toString());
       }
       if (params.userType) {
         queryParams.append("userType", params.userType);
       }

       return `applications?${queryParams.toString()}`;
     },
     providesTags: ["Applications"],
     async onQueryStarted(_, { queryFulfilled }) {
       await withToast(queryFulfilled, {
         error: "Failed to fetch applications.",
       });
     },
   }),

   updateApplicationStatus: build.mutation<
     Application & { lease?: Lease },
     { id: number; status: string }
   >({
     query: ({ id, status }) => ({
       url: `applications/${id}/status`,
       method: "PUT",
       body: { status },
     }),
     invalidatesTags: ["Applications", "Leases"],
     async onQueryStarted(_, { queryFulfilled }) {
       await withToast(queryFulfilled, {
         success: "Application status updated successfully!",
         error: "Failed to update application settings.",
       });
     },
   }),

   createApplication: build.mutation<Application, Partial<Application>>({
     query: (body) => ({
       url: `applications`,
       method: "POST",
       body: body,
     }),
     invalidatesTags: ["Applications"],
     async onQueryStarted(_, { queryFulfilled }) {
       await withToast(queryFulfilled, {
         success: "Application created successfully!",
         error: "Failed to create applications.",
       });
     },
   }),
 
  }),

});

export const {
  useGetAuthUserQuery,
  useUpdateTenantSettingsMutation,
  useUpdateManagerSettingsMutation,
  useGetPropertiesQuery,
  useGetTenantQuery,
  useAddFavoritePropertyMutation,
  useRemoveFavoritePropertyMutation,
  useCreateApplicationMutation, 
  useGetPropertyQuery,
  useGetApplicationsQuery,
  useGetLeasesQuery,
  useGetPropertyLeasesQuery,
  useGetPaymentsQuery,
  useGetManagerPropertiesQuery,
  useCreatePropertyMutation,
  useGetCurrentResidencesQuery,
  useUpdateApplicationStatusMutation
} = api;
// export const {} = api;
