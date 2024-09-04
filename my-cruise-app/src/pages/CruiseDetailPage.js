import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import LegTable from '../components/LegTable';
import ScientistsList from '../components/ScientistsList';
import CruiseDetailMap from '../components/maps/CruiseDetailMap';
import './CruiseDetailPage.css'; // Make sure this import is correct

const CruiseDetailPage = () => {
    const { id } = useParams();
    const [cruiseDetail, setCruiseDetail] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        async function fetchCruiseDetail() {
            try {
                const response = await fetch(`http://localhost:8000/api/cruises/${id}/`);
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
        }
        fetchCruiseDetail();
    }, [id]);

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;
    if (!cruiseDetail) return <div>No cruise details available.</div>;

    return (
        <div className="cruise-detail-container">
            <header className="cruise-detail-header">
                <h1>{cruiseDetail.cruise_name}</h1>
                <img
                    src={cruiseDetail.vessel_details?.vessel_picture_url || 'placeholder-image.jpg'}
                    alt={cruiseDetail.vessel_details?.vessel_name ? `Vessel ${cruiseDetail.vessel_details.vessel_name}` : 'Vessel unavailable'}
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
                    <LegTable legs={cruiseDetail.legs || []} />
                </section>
                <section className="cruise-detail-section">
                    <h2>Scientists</h2>
                    <ScientistsList scientists={cruiseDetail.scientists || []} />
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
