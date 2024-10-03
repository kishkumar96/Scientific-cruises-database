import React, { useRef, useEffect } from 'react';
import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import GeoJSON from 'ol/format/GeoJSON';
import Style from 'ol/style/Style';
import Stroke from 'ol/style/Stroke';
import Icon from 'ol/style/Icon';
import Point from 'ol/geom/Point';
import Feature from 'ol/Feature';

/**
 * CruiseDetailMap component renders a map with a cruise route.
 * 
 * @component
 * @param {Object} props - Component properties.
 * @param {string} props.cruiseId - The ID of the cruise to fetch and display the route for.
 * 
 * @example
 * <CruiseDetailMap cruiseId="12345" />
 * 
 * @returns {JSX.Element} A React component that renders a map with the cruise route.
 */
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

    const fetchGeoServerData = async () => {
      try {
        const response = await fetch(
          `https://cruisedb.corp.spc.int/geoserver/cruise/wfs?service=WFS&version=2.0.0&request=GetFeature&typeName=cruise:cruises_route&outputFormat=application/json&cql_filter=cruise_id='${cruiseId}'`
        );
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        console.log('GeoServer WFS data:', data);

        const vectorSource = new VectorSource({
          features: new GeoJSON().readFeatures(data, {
            featureProjection: 'EPSG:3857',
          }),
        });

        const vectorLayer = new VectorLayer({
          source: vectorSource,
          style: function (feature) {
            // Fixed cruise color for consistency
            const cruiseColor = '#ff6347'; 

            // Handle MultiLineString and LineString geometries
            const coordinates = feature.getGeometry().getType() === 'MultiLineString'
              ? feature.getGeometry().getCoordinates()[0]
              : feature.getGeometry().getCoordinates();
            const startPoint = coordinates[0];
            const endPoint = coordinates[coordinates.length - 1];

            // Create start and end vertex icons (directional arrows)
            const startFeature = new Feature(new Point(startPoint));
            const endFeature = new Feature(new Point(endPoint));

            const arrowIcon = new Icon({
              src: '/path/to/your/arrow-icon.png', // Replace this with the path to your arrow icon
              scale: 0.5,
              rotation: 0, // Optionally calculate rotation based on route direction
            });

            startFeature.setStyle(new Style({
              image: arrowIcon,
            }));

            endFeature.setStyle(new Style({
              image: arrowIcon,
            }));

            // Dotted line style for the cruise route
            return new Style({
              stroke: new Stroke({
                color: cruiseColor,
                width: 2,
                lineDash: [4, 8], // Dotted line pattern
              }),
            });
          },
        });

        map.addLayer(vectorLayer);

        // Fit the map to the extent of the cruise route
        map.getView().fit(vectorSource.getExtent(), { padding: [50, 50, 50, 50], maxZoom: 10 });

      } catch (error) {
        console.error('Error fetching route from GeoServer:', error);
      }
    };

    fetchGeoServerData();

    return () => map.setTarget(undefined); // Clean up on unmount
  }, [cruiseId]);

  return (
    <div ref={mapContainerRef} className="map-container" style={{ height: '400px', width: '100%' }} />
  );
};

export default CruiseDetailMap;
