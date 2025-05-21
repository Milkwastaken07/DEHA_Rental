import React, { useState } from "react";
import { initialState, FiltersState } from "@/state";
import { usePathname, useRouter } from "next/navigation";
import { debounce } from "lodash";
import { cleanParams, cn, formatEnumString } from "@/lib/utils";
import { useDispatch } from "react-redux";
import { useAppSelector } from "@/state/redux";
import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { AmenityIcons, PropertyTypeIcons } from "@/lib/constants";
import { Slider } from "@/components/ui/slider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
const FiltersFull = () => {
  const dispatch = useDispatch();
  const router = useRouter();
  const pathname = usePathname();
  const [filters, setFilters] = useState<any>(initialState.filters);
  const [localFilters, setLocalFilters] = useState(initialState.filters);
  const isFiltersFullOpen = useAppSelector(
    (state) => state.global.isFiltersFullOpen
  );

  const updateURL = debounce((newFillers: FiltersState) => {
    const cleanFilters = cleanParams(newFillers);
    const updatedSearchParams = new URLSearchParams();

    Object.entries(cleanFilters).forEach(([key, value]) => {
      updatedSearchParams.set(
        key,
        Array.isArray(value) ? value.join(",") : value.toString()
      );
    });

    router.push(`${pathname}?${updatedSearchParams.toString()}`);
  });

  const handleSubmit = () => {
    dispatch({ type: 'filters/setFilters', payload: localFilters });
    updateURL(localFilters);
  };

  const handleReset = () => {
    setLocalFilters(initialState.filters);
    dispatch({ type: 'filters/setFilters', payload: localFilters });
    updateURL(initialState.filters);
  };

  const handleAmenityChange = (amenity: AmenityEnum) => {
    setLocalFilters((prev: any) => ({
      ...prev,
      amenities: prev.amenities.includes(amenity)
        ? prev.amenities.filter((a: AmenityEnum) => a !== amenity)
        : [...prev.amenities, amenity],
    }));
  };

  const handleLocationSearch = async () => {
    try {
      const response = await fetch(
        `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(
          localFilters.location
        )}.json?access_token=${
          process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN
        }&fuzzyMath=true`
      )
      const data = await response.json();
      if(data.features && data.features.length > 0) {
        const [lng, lat] = data.features[0].center;
        setLocalFilters((prev: any) => ({
          ...prev,
          coordinates: [lng, lat],
        }))
      }
    } catch (error) {
      console.error("Error search location:", error);
    }
  }

  if (!isFiltersFullOpen) return null;
  return (
    <div className="bg-white rounded-lg px-4 h-full overflow-auto pb-10">
      <div className="flex flex-col space-y-6">
        {/* Location */}
        <div>
          <h4 className="font-bold mb-2">Location</h4>
          <div className="flex items-center">
            <Input
              placeholder="Enter location"
              value={filters.location}
              onChange={(e) =>
                setLocalFilters((prev) => ({
                  ...prev,
                  location: e.target.value,
                }))
              }
              className="rounded-l-xl rounded-r-none border-r-0"
            />
            <Button
              className="rounded-r-xl rounded-l-none border-l-none border-black shadow-md"
              onClick={handleLocationSearch}
            >
              <Search className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Property Type */}
        <div>
          <h4 className="font-bold mb-2">Property Type</h4>
          <div className="grid grid-cols-2 gap-4">
            {Object.entries(PropertyTypeIcons).map(([type, Icon]) => (
              <div
                key={type}
                className={cn(
                  "flex flex-col items-center justify-center p-4 border rounded-lg cursor-pointer",
                  localFilters.propertyType === type
                    ? "border-black"
                    : "border-gray-200"
                )}
                onClick={() =>
                  setLocalFilters((prev) => ({
                    ...prev,
                    propertyType: type as PropertyTypeEnum,
                  }))
                }
              >
                <Icon className="w-6 h-6 mb-2" />
                <span>{type}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Price Range */}
        <div>
          <h4 className="font-bold mb-2">Price Range (Monthly)</h4>
          <Slider
            min={0}
            max={10000}
            step={100}
            value={[
              localFilters.priceRange[0] ?? 0,
              localFilters.priceRange[1] ?? 10000,
            ]}
            onValueChange={(value: any) =>
              setLocalFilters((prev: any) => ({
                ...prev,
                priceRange: value as [number, number],
              }))
            }
          />
          <div className="flex justify-between mt-2">
            <span>Min: ${localFilters.priceRange[0] ?? 0}</span>
            <span>Max: ${localFilters.priceRange[1] ?? 10000}</span>
          </div>
        </div>

        {/* Beds*/}
        <div className="flex gap-4">
            <div className="flex-1">
                <h4 className="font-bold mb-2">Beds</h4>
                <Select 
                    value={String(localFilters.beds) || "any"}
                    onValueChange={(value: any) => setLocalFilters((prev: any) => ({...prev, beds: value}))}
                >
                    <SelectTrigger className="w-full rounded-xl">
                        <SelectValue placeholder="Beds"/>
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="any">Any</SelectItem>
                        <SelectItem value="1">1+ bed</SelectItem>
                        <SelectItem value="2">2+ beds</SelectItem>
                        <SelectItem value="3">3+ beds</SelectItem>
                        <SelectItem value="4">4+ beds</SelectItem>
                        <SelectItem value="5">5+ beds</SelectItem>
                    </SelectContent>
                </Select>
            </div>
        </div>

        {/* Baths*/}
        <div className="flex gap-4">
            <div className="flex-1">
                <h4 className="font-bold mb-2">Baths</h4>
                <Select 
                    value={String(localFilters.baths) || "any"}
                    onValueChange={(value: any) => setLocalFilters((prev: any) => ({...prev, baths: value}))}
                >
                    <SelectTrigger className="w-full rounded-xl">
                        <SelectValue placeholder="Baths"/>
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="any">Any</SelectItem>
                        <SelectItem value="1">1+ bath</SelectItem>
                        <SelectItem value="2">2+ baths</SelectItem>
                        <SelectItem value="3">3+ baths</SelectItem>
                        <SelectItem value="4">4+ baths</SelectItem>
                        <SelectItem value="5">5+ baths</SelectItem>
                    </SelectContent>
                </Select>
            </div>
        </div>

        {/* Square Feet */}
        <div>
            <h4 className="font-bold mb-2">Square Feet</h4>
            <Slider
                min={0}
                max={5000}
                step={100}
                value={[localFilters.squareFeet[0] || 0, localFilters.squareFeet[1] || 5000]}
                onValueChange={(value: any) => setLocalFilters((prev: any) => ({...prev, squareFeet: value as [number, number]}))}
                className="[&>.bar]:bg-primary-700"
            />
            <div className="flex justify-between mt-2">
                <span>Min: {localFilters.squareFeet[0] || 0} sqft</span>
                <span>Max: {localFilters.squareFeet[1] || 10000} sqft</span>
            </div>
        </div>
        
        {/* Amenities */}
        <div>
            <h4 className="font-bold mb-2">Amenities</h4>
            <div className="flex flex-wrap gap-2">
                {Object.entries(AmenityIcons).map(([amenity, Icon]) => (
                    <div
                        key={amenity}
                        className={cn(
                          "flex items-center space-x-2 p-2 border rounded-lg cursor-pointer",
                          localFilters.amenities.includes(amenity as AmenityEnum)
                            ? "border-black"
                            : "border-gray-200"
                        )}
                        onClick={() => handleAmenityChange(amenity as AmenityEnum)}
                        >
                            <Icon className="w-5 h-5 hover:cursor-pointer" />
                            <Label>{formatEnumString(amenity)}</Label>
                        </div>
                ))}
            </div>
        </div>

        {/* Availabel From  */}
        <div>
            <h4 className="font-bold mb-2">Available From</h4>
            <Input
                type="date"
                value={localFilters.availableFrom || "any"}
                onChange={(e) => setLocalFilters((prev: any) => ({...prev, availableFrom: e.target.value}))}
                className="rounded-xl"
            />
        </div>
        {/* Apply and Reset buttons */}
        <div className="flex gap-4 mt-6">
            {/* Apply  */}
          <Button
            className="flex-1 bg-primary-700 text-white rounded-xl"
            onClick={handleSubmit}
          >
            APPLY
          </Button>
          {/* Reset  */}
          <Button
            className="flex-1 rounded-xl"
            variant="outline"
            onClick={handleReset}
          >
            Reset Filters
          </Button>
        </div>
      </div>
    </div>
  );
};

export default FiltersFull;
