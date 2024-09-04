import React, { useRef, useEffect } from 'react';
import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import GeoJSON from 'ol/format/GeoJSON';

const MapComponent = () => {
  const mapRef = useRef(null); // Use useRef to store the map instance

  useEffect(() => {
    const initMap = new Map({
      target: 'map',
      layers: [
        new TileLayer({
          source: new OSM({
            wrapX: true, 
          }),
        }),
      ],
      view: new View({
        center: [0, 0],
        zoom: 2,
      }),
    });

    mapRef.current = initMap; // Store the map in the ref

    return () => {
      mapRef.current.setTarget(undefined); // Clean up on unmount
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current; // Get the map from the ref
    if (map) {
      fetch('http://localhost:8081/geoserver/cruise/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=cruise:cruises_route&outputFormat=application/json')
        .then((response) => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.json();
        })
        .then((data) => {
          const vectorSource = new VectorSource({
            features: new GeoJSON().readFeatures(data, {
              featureProjection: 'EPSG:3857', 
            }),
            wrapX: true, 
          });

          const vectorLayer = new VectorLayer({
            source: vectorSource,
          });

          map.addLayer(vectorLayer);
        })
        .catch((error) => {
          console.error('Error fetching GeoServer data:', error);
        });
    }
  }, []); // Empty dependency array ensures this runs only once after the map is initialized

  return <div id="map" style={{ height: '400px', width: '100%' }} />;
};

export default MapComponent;