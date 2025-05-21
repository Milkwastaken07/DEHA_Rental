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
    console.log("Properties: ", properties);

    useEffect(() => {
        // if(isLoading || isError || !properties) return;
        const map = new mapboxgl.Map({
            container: mapContainerRef.current!,
            style: 'mapbox://styles/pbbang42/cmartx75401sd01r4c0zua5jh',
            center: !filters.coordinates || [-73.9854, 40.7488],
            zoom: 9,
        });

        // properties.forEach((property) => {
        //     const marker = createPropertyMarker(property, map);
        //     const markerElement = marker.getElement();
        //     const path = markerElement.querySelector("path[fill='#3FB1CE']");
        //     if(path) path.setAttribute("fill", "#000000");
        // });
        
        const resizeMap = () => setTimeout(() => map.resize(), 100);
        resizeMap();
        return () => {
            map.remove();
        };
    });

    if (isLoading) return <div>Loading...</div>;
    // if (isError ) return <div>Error !!! {isError}</div>;

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
    const market = new mapboxgl.Marker()
        .setLngLat([property.location.coordinates.longitude, property.location.coordinates.latitude])
        .setPopup(
           new mapboxgl.Popup({offset: 25})
           .setHTML(`
               <div class="market-popup">
                <div class="market-popup-image></div>
                <div>
                    <a href="search/${property.id}" target="_blank" class="marker-popup-title">${property.name}</a>
                    <p class="marker-popup-price">
                        $${property.pricePerMonth} 
                        <span class="marker-popup-price-unit"> / month</span>
                    </p>
                </div>
               </div>
           `)
       )
       return market.addTo(map);
}

export default Map;
