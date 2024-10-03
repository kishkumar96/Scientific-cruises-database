import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import LegTable from '../components/LegTable';
import ScientistsList from '../components/ScientistsList';
import CruiseDetailMap from '../components/maps/CruiseDetailMap';
import './CruiseDetailPage.css';

/**
 * CruiseDetailPage component fetches and displays detailed information about a specific cruise.
 * 
 * @component
 * @example
 * return (
 *   <CruiseDetailPage />
 * )
 * 
 * @returns {JSX.Element} The rendered component.
 */
const CruiseDetailPage = () => {
    const { id } = useParams();
    const [cruiseDetail, setCruiseDetail] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isRetrying, setIsRetrying] = useState(false);
    const apiUrl = process.env.REACT_APP_API_URL || 'https://cruisedb.corp.spc.int/api/';

    const fetchCruiseDetail = useCallback(async () => {
        try {
            setIsRetrying(false);
            setLoading(true);
            const response = await fetch(`${apiUrl}/cruises/${id}/`);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();
            setCruiseDetail(data);
        } catch (error) {
            setError(`Failed to load cruise details: ${error.message}`);
        } finally {
            setLoading(false);
        }
    }, [apiUrl, id]);

    useEffect(() => {
        fetchCruiseDetail();
    }, [fetchCruiseDetail]);

    if (loading) return <div className="loading-indicator">Loading...</div>;
    if (error) return (
        <div className="error-message">
            <p>Error: {error}</p>
            <button onClick={() => { setIsRetrying(true); fetchCruiseDetail(); }} disabled={isRetrying}>
                {isRetrying ? 'Retrying...' : 'Retry'}
            </button>
        </div>
    );
    if (!cruiseDetail) return <div>No cruise details available.</div>;

    return (
        <div className="cruise-detail-container">
            <header className="cruise-detail-header">
                <h1>{cruiseDetail.cruise_name}</h1>
                <img
                    src={cruiseDetail.vessel_details?.vessel_picture_url || 'placeholder-image.jpg'}
                    alt={cruiseDetail.vessel_details?.vessel_name ? `Vessel ${cruiseDetail.vessel_details.vessel_name}` : 'Vessel unavailable'}
                    loading="lazy" // Use lazy loading to improve performance
                />
                <div>
                    <p><strong>Vessel:</strong> {cruiseDetail.vessel_details?.vessel_name || 'Unknown Vessel'}</p>
                    <p><strong>Description:</strong> {cruiseDetail.vessel_details?.vessel_desc || 'No description available.'}</p>
                    <p><strong>More Information:</strong>
                        {cruiseDetail.vessel_details?.vessel_credit_url ? (
                            <a
                                href={cruiseDetail.vessel_details.vessel_credit_url}
                                target="_blank"
                                rel="noopener noreferrer">
                                Visit Website
                            </a>
                        ) : (
                            'No additional information available.'
                        )}
                    </p>
                </div>
            </header>

            <main className="main-content">
                <section className="cruise-detail-section">
                    <h2>Legs</h2>
                    {cruiseDetail.legs?.length ? (
                        <LegTable legs={cruiseDetail.legs} />
                    ) : (
                        <p>No leg details available.</p>
                    )}
                </section>
                <section className="cruise-detail-section">
                    <h2>Scientists</h2>
                    {cruiseDetail.scientists?.length ? (
                        <ScientistsList scientists={cruiseDetail.scientists} />
                    ) : (
                        <p>No scientists information available.</p>
                    )}
                </section>
                <section className="cruise-detail-section">
                    <h2>Map</h2>
                    <CruiseDetailMap cruiseId={id} />
                </section>
            </main>
        </div>
    );
};

export default CruiseDetailPage;
