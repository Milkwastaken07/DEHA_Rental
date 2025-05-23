import React, { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { useAppSelector } from '@/state/redux';
import { useGetPropertiesQuery } from '@/state/api';
import { Property } from '@/types/models';

mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN as string;
const Map = () => {
    const mapContainerRef = useRef(null);
    const filters = useAppSelector((state) => state.global.filters);
    const {
        data: properties,
        isLoading,
        isError,
    } = useGetPropertiesQuery({
        ...filters,
        priceRange: filters.priceRange as [number, number] | [null, null],
        squareFeet: filters.squareFeet as [number, number] | [null, null],
        coordinates: filters.coordinates as [number, number] | [null, null]
    });
    

    useEffect(() => {
        // if(isLoading || isError || !properties) return;
        if(!properties) return;

        console.log("properties", properties);
        console.log("isLoading", isLoading);
        console.log("isError", isError);

        const map = new mapboxgl.Map({
            container: mapContainerRef.current!,
            style: 'mapbox://styles/pbbang42/cmartx75401sd01r4c0zua5jh',
            center: [-118.144516, 34.147785],
            zoom: 9,
        });
        console.log("ok 1", properties.properties);
        properties.properties.forEach((property: Property) => {
          console.log(property);
            const marker = createPropertyMarker(property, map);
            const markerElement = marker.getElement();
            const path = markerElement.querySelector("path[fill='#3FB1CE']");
            if(path) path.setAttribute("fill", "#000000");
        });
        console.log("ok 2");
        
        const resizeMap = () => setTimeout(() => map.resize(), 100);
        resizeMap();
        return () => {
            map.remove();
        };
    }, [properties]);

    if (isError ) return <div>Error !!! {isError}</div>;
    if (isLoading) return <div>Loading...</div>;
    console.log(properties);
    return (
        <div className='basis-5/12 grow relative rounded-xl'>
            <div 
                className='map-container rounded-xl'
                ref={mapContainerRef}
                style={{
                    height: "100%",
                    width: "100%",
                }}
            />
        </div>
    );
}

const createPropertyMarker = (property: Property, map: mapboxgl.Map) => {
  console.log(property);
    const marker = new mapboxgl.Marker()
      .setLngLat([
        property.location.longitude,
        property.location.latitude,
      ])
      .setPopup(
        new mapboxgl.Popup().setHTML(
          `
          <div class="marker-popup">
            <div class="marker-popup-image"></div>
            <div>
              <a href="/search/${property.id}" target="_blank" class="marker-popup-title">${property.name}</a>
              <p class="marker-popup-price">
                $${property.pricePerMonth}
                <span class="marker-popup-price-unit"> / month</span>
              </p>
            </div>
          </div>
          `
        )
      )
      .addTo(map);

    return marker;
  };

export default Map;
