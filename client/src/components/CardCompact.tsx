import Image from "next/image";
import React from "react";
import { Button } from "./ui/button";
import { Bath, Bed, Heart, House, Star } from "lucide-react";
import Link from "next/link";

const CardCompact = ({
  property,
  isFavorite,
  onFavoriteToggle,
  showFavoriteButton = true,
  propertyLink,
}: CardCompactProps) => {
  const [imgSrc, setImgSrc] = React.useState(
    property.photoUrls?.[0] || "/placeholder.jpg"
  );

  return (
    <div className="bg-white rounded-xl overflow-hidden shadow-lg w-full flex h-40 mb-5">
      <div className="relative w-1/3">
        <Image
          src={imgSrc}
          alt={property.name}
          fill
          className="object-cover"
          sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
          onError={(e) => setImgSrc("/placeholder.jpg")}
        />
        <div className="absolute bottom-2 left-2 flex gap-1 flex-col">
          {property.isPetsAllowed && (
            <span className="bg-white/80 text-black text-xs font-semibold px-2 py-1 rounded-full">
              Pets
            </span>
          )}
          {property.isParkingIncluded && (
            <span className="bg-white/80 text-black text-xs font-semibold px-2 py-1 rounded-full">
              Parking
            </span>
          )}
        </div>
        <div className="w-2/3 p-4 flex flex-col justify-between"></div>
        <div>
          <div className="flex justify-between items-start">
          <h2 className="text-xl font-bold mb-1">
            {propertyLink ? (
              <Link
                href={propertyLink}
                className="hover:underline hover:text-blue-600"
                scroll={false}
              >
                {property.name}
              </Link>
            ) : (
              property.name
            )}
          </h2>
          </div>
          {showFavoriteButton && (
            <Button
              className="bg-white rounded-full p-1"
              onClick={onFavoriteToggle}
            >
              <Heart
                className={`'w-4 h-4' ${
                  isFavorite ? "text-red-500 fill-red-500" : "text-gray-500"
                }`}
              />
            </Button>
          )}
          <p className="text-gray-600 mb-1 text-sm">
            {property?.location?.address}, {property?.location?.city}
          </p>
          <div className="flex text-sm items-center">
            <div className="flex items-center mb-2">
              <Star className="w-4 h-4 text-yellow-400 mr-1" />
              <span className="font-semibold">
                {property.averageRating.toFixed(1)}
              </span>
              <Star className="w-4 h-4 text-yellow-400 mr-1" />
              <span className="font-semibold">
                ({property.numberOfReviews} Reviews)
              </span>
            </div>
            <p className="text-lg font-bold mb-3">
              ${property.pricePerNight.toFixed(0)}
              {""}
              <span className="text-gray-600 text-base font-normal">
                {" "}
                /month
              </span>
            </p>
          </div>
          <hr />
          <div className="flex justify-between items-center gap-4 text-gray-600 mt-5">
            <span className="flex items-center">
              <Bed className="w-5 h-5 mr-2" />
              {property.beds} Bed
            </span>
            <span className="flex items-center">
              <Bath className="w-5 h-5 mr-2" />
              {property.baths} Bath
            </span>
            <span className="flex items-center">
              <House className="w-5 h-5 mr-2" />
              {property.squareFeet} sqft
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CardCompact;
