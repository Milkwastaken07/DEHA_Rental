import Card from "@/components/Card";
import CardCompact from "@/components/CardCompact";
import {
  useAddFavoritePropertyMutation,
  useGetAuthUserQuery,
  useGetPropertiesQuery,
  useGetTenantQuery,
  useRemoveFavoritePropertyMutation,
} from "@/state/api";
import { useAppSelector } from "@/state/redux";
import { Property } from "@/types/models";
import React from "react";

const Listings = () => {
  const { data: authUser } = useGetAuthUserQuery();
  // console.log(authUser);
  const { data: tenant } = useGetTenantQuery(
    authUser?.cognitoInfo.userId || "",
    { skip: !authUser?.cognitoInfo.userId }
  );
  const [addFavorite] = useAddFavoritePropertyMutation();
  const [removeFavorite] = useRemoveFavoritePropertyMutation();
  const viewMode = useAppSelector((state) => state.global.viewMode);
  const filters = useAppSelector((state) => state.global.filters);
  // console.log(filters);

  const {
    data: properties,
    isLoading,
    isError,
  } = useGetPropertiesQuery({
    ...filters,
    priceRange: filters.priceRange as [number, number] | [null, null],
    squareFeet: filters.squareFeet as [number, number] | [null, null],
    coordinates: filters.coordinates as [number, number] | [null, null],
  });

  const handleFavoriteToggle = async (propertyId: number) => {
    if (!authUser) return;
    const isFavorite = tenant?.favorites?.some(
      (fav: number) => fav === propertyId
    );
    if (isFavorite) {
      await removeFavorite({
        cognitoId: authUser.cognitoInfo.userId,
        propertyId,
      });
    } else {
      await addFavorite({
        cognitoId: authUser.cognitoInfo.userId,
        propertyId,
      });
    }
  };

  if (isLoading) return <div>Loading...</div>;
  if (isError) return <div>Failed to fetch properties</div>;
  if (!properties) return <div>No properties</div>;
  return (
    <div className="w-full">
      <h3 className="text-sm px-4 font-bold">
        {properties?.properties.length}{" "}
        <span className="text-gray-700 font-normal">
          Places in {filters.location}
        </span>
      </h3>
      <div className="flex">
        <div className="p-4 w-full">
          {properties && properties.properties.length > 0 && properties?.properties.map((property) =>
            viewMode === "grid" ? (
              <Card
                key={property.id}
                property={property}
                isFavorite={tenant?.favorites?.some(
                  (fav: number) => fav === property.id
                ) || false}
                onFavoriteToggle={() => handleFavoriteToggle(property.id)}
                showFavoriteButton={!!authUser}
                propertyLink={`/search/${property.id}`}
              />
            ) : (
              <CardCompact 
                key={property.id}
                property={property}
                isFavorite={tenant?.favorites?.some(
                  (fav: number) => fav === property.id
                ) || false}
                onFavoriteToggle={() => handleFavoriteToggle(property.id)}
                showFavoriteButton={!!authUser}
                propertyLink={`/search/${property.id}`}
              />
            )
          )}
        </div>
      </div>
    </div>
  );
};

export default Listings;
