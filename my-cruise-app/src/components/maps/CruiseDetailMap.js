import React, { useRef, useEffect } from 'react';
import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import ImageLayer from 'ol/layer/Image';
import ImageWMS from 'ol/source/ImageWMS';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import GeoJSON from 'ol/format/GeoJSON';

const CruiseDetailMap = ({ cruiseId }) => {
  const mapContainerRef = useRef();

  useEffect(() => {
    const map = new Map({
      target: mapContainerRef.current,
      layers: [
        new TileLayer({
          source: new OSM(),
        }),
      ],
      view: new View({
        center: [0, 0],
        zoom: 2,
      }),
    });

    // Add WMS layer
    const wmsLayer = new ImageLayer({
      source: new ImageWMS({
        url: 'http://localhost:8081/geoserver/cruise/wms', // Update with your GeoServer WMS URL
        params: {
          'LAYERS': 'cruise:cruises_route', // Replace with your actual layer name
          'TILED': true,
        },
        serverType: 'geoserver',
      }),
    });

    map.addLayer(wmsLayer);

    // Fetch and add GeoServer vector data
    const fetchGeoServerData = async () => {
      try {
        const response = await fetch(`http://localhost:8081/geoserver/cruise/wfs?service=WFS&version=2.0.0&request=GetFeature&typeName=cruise:cruises_route&outputFormat=application/json&cql_filter=cruise_id='${cruiseId}'`);
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        const vectorSource = new VectorSource({
          features: new GeoJSON().readFeatures(data, {
            featureProjection: 'EPSG:3857', // Match the projection used in the map
          }),
        });

        const vectorLayer = new VectorLayer({
          source: vectorSource,
        });

        map.addLayer(vectorLayer);
      } catch (error) {
        console.error('Error fetching route from GeoServer:', error);
      }
    };

    fetchGeoServerData();

    return () => map.setTarget(undefined);
  }, [cruiseId]);

  return (
    <div ref={mapContainerRef} className="map-container" style={{ height: '400px', width: '100%' }} />
  );
};

export default CruiseDetailMap;
