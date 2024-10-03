import React, { useRef, useEffect, useCallback } from 'react';
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
import Feature from 'ol/Feature';
import Point from 'ol/geom/Point';

const generateRandomColor = () => {
  const letters = '0123456789ABCDEF';
  let color = '#';
  for (let i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
};

const CruiseListMap = () => {
  const mapContainerRef = useRef();
  const colorCache = useRef({});

  const getCruiseColor = useCallback((cruiseId) => {
    if (!colorCache.current[cruiseId]) {
      colorCache.current[cruiseId] = generateRandomColor();
    }
    return colorCache.current[cruiseId];
  }, []);

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
        minZoom: 2,
        maxZoom: 14,
      }),
    });

    const fetchGeoServerData = async () => {
      try {
        const response = await fetch(`https://cruisedb.corp.spc.int/geoserver/cruise/wfs?service=WFS&version=2.0.0&request=GetFeature&typeName=cruise:cruises_route&outputFormat=application/json`);
        if (!response.ok) {
          if (response.status === 404) {
            throw new Error('Cruise route data not found.');
          } else {
            throw new Error(`GeoServer data fetch failed: ${response.status}`);
          }
        }
        const data = await response.json();

        const vectorSource = new VectorSource({
          features: new GeoJSON().readFeatures(data, {
            featureProjection: 'EPSG:3857',
          }),
        });

        const vectorLayer = new VectorLayer({
          source: vectorSource,
          style: function (feature) {
            const cruiseId = feature.get('cruise_id');
            const cruiseColor = getCruiseColor(cruiseId);

            // Handle MultiLineString and LineString geometries
            const coordinates = feature.getGeometry().getType() === 'MultiLineString'
              ? feature.getGeometry().getCoordinates()[0]
              : feature.getGeometry().getCoordinates();
            const startPoint = coordinates[0];
            const endPoint = coordinates[coordinates.length - 1];

            // Create start and end vertex icons
            const startVertex = new Feature({
              geometry: new Point(startPoint),
            });
            const endVertex = new Feature({
              geometry: new Point(endPoint),
            });

            const arrowIcon = new Icon({
              src: 'https://example.com/path/to/arrow-icon.png', // Update this URL
              scale: 0.5,
              rotation: 0,
            });

            startVertex.setStyle(new Style({ image: arrowIcon }));
            endVertex.setStyle(new Style({ image: arrowIcon }));

            return new Style({
              stroke: new Stroke({
                color: cruiseColor,
                width: 2,
                lineDash: [4, 4], // Dotted line
              }),
            });
          },
        });

        map.addLayer(vectorLayer);
      } catch (error) {
        console.error('Error fetching route from GeoServer:', error);
        alert(error.message || 'Unable to fetch route data. Please try again later.');
      }
    };

    fetchGeoServerData();

    return () => map.setTarget(undefined);
  }, [getCruiseColor]);

  return <div ref={mapContainerRef} style={{ height: '600px', width: '100%' }} />;
};

export default CruiseListMap;
