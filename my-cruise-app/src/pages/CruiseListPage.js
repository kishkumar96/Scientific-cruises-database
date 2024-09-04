import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import MapComponent from '../components/maps/CruiseListMap';
import CountryFlag from 'react-country-flag';
import Tooltip from '../components/Tooltip';
import './CruiseListPage.css';
import countries from 'i18n-iso-countries';

countries.registerLocale(require('i18n-iso-countries/langs/en.json'));

// Pagination component to handle page numbers
const Pagination = ({ totalItems, itemsPerPage, currentPage, onPageChange }) => {
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    if (totalPages <= 1) return null; // No pagination needed if there's only one page

    return (
        <div className="pagination">
            {Array.from({ length: totalPages }, (_, index) => (
                <button
                    key={index}
                    onClick={() => onPageChange(index + 1)}
                    className={currentPage === index + 1 ? 'page-number active' : 'page-number'}
                >
                    {index + 1}
                </button>
            ))}
        </div>
    );
};

const CruiseListPage = () => {
    const [activeTab, setActiveTab] = useState('list');
    const [currentPage, setCurrentPage] = useState(1);
    const [itemsPerPage] = useState(10);
    const [searchTerm, setSearchTerm] = useState('');
    const [filters, setFilters] = useState({ status: '' });
    const [cruises, setCruises] = useState([]);
    const [statuses, setStatuses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const handleSearchChange = (e) => setSearchTerm(e.target.value);

    const getCountryName = (isoCode) => {
        return countries.getName(isoCode, "en", { select: "official" }) || 'No country';
    };

    // Filter cruises based on search term and status filter
    const filteredCruises = cruises.filter(cruise => {
        const name = cruise.cruise_name.toLowerCase();
        const status = cruise.status_name;
        return name.includes(searchTerm.toLowerCase()) &&
            (!filters.status || status === filters.status);
    });

    const indexOfLastCruise = currentPage * itemsPerPage;
    const indexOfFirstCruise = indexOfLastCruise - itemsPerPage;
    const currentCruises = filteredCruises.slice(indexOfFirstCruise, indexOfLastCruise);

    const handlePageChange = pageNumber => setCurrentPage(pageNumber);
    const handleSeeDetails = id => navigate(`/cruises/${id}`);
    const apiUrl = process.env.REACT_APP_API_URL;

    // Fetch cruises data
    useEffect(() => {
        const fetchCruises = async () => {
            try {
                const response = await fetch('${apiUrl}/api/cruises/', {
                    headers: { 'Accept': 'application/json' }
                });
                if (!response.ok) throw new Error(`Failed to fetch cruises. Status: ${response.status}`);
                const data = await response.json();
                setCruises(data);
            } catch (error) {
                console.error('Error fetching cruises:', error);
                setError('An error occurred while loading cruises. Please try again later.');
            } finally {
                setLoading(false);
            }
        };
        fetchCruises();
    }, []);

    // Fetch statuses data
    useEffect(() => {
        const fetchStatuses = async () => {
            try {
                const response = await fetch('${apiUrl}/api/statuses/', {
                    headers: { 'Accept': 'application/json' }
                });
                if (!response.ok) throw new Error(`Failed to fetch statuses. Status: ${response.status}`);
                const data = await response.json();
                setStatuses(data);
            } catch (error) {
                console.error('Error fetching statuses:', error);
                setError('An error occurred while loading statuses. Please try again later.');
            }
        };
        fetchStatuses();
    }, []);

    return (
        <div className="cruise-list-container">
            <header>
                <h1>Scientific Cruises - SPC</h1>
                <nav>
                    <button onClick={() => setActiveTab('list')} className={activeTab === 'list' ? 'tab active' : 'tab'}>List</button>
                    <button onClick={() => setActiveTab('map')} className={activeTab === 'map' ? 'tab active' : 'tab'}>Map</button>
                </nav>
            </header>
            <main>
                {activeTab === 'list' && (
                    <section aria-label="Cruise List">
                        <h2>List Cruises</h2>
                        <div className="search-filter-container">
                            <input
                                type="text"
                                placeholder="Search cruises..."
                                onChange={handleSearchChange}
                                className="search-input"
                            />
                            <select
                                value={filters.status}
                                onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                                className="status-filter"
                            >
                                <option value="">All Statuses</option>
                                {statuses.map((status) => (
                                    <option key={status.id} value={status.name}>{status.name}</option>
                                ))}
                            </select>
                        </div>

                        {loading && <div>Loading cruises...</div>}
                        {error && <div className="error-message">Error: {error}</div>}

                        {!loading && !error && (
                            <>
                                <div className="cruise-list-table-container">
                                    <table className="cruise-list-table" role="grid">
                                        <thead>
                                            <tr role="row">
                                                <th scope="col">Name</th>
                                                <th scope="col">Status</th>
                                                <th scope="col">Country</th>
                                                <th scope="col">Vessel</th>
                                                <th scope="col">First Departure</th>
                                                <th scope="col">Last Arrival</th>
                                                <th scope="col">Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {currentCruises.map(cruise => (
                                                <tr key={cruise.cruise_id} role="row">
                                                    <td>{cruise.cruise_name}</td>
                                                    <td>{cruise.status_name}</td>
                                                    <td>
                                                        <Tooltip text={getCountryName(cruise.iso2_country)}>
                                                            <CountryFlag
                                                                countryCode={cruise.iso2_country}
                                                                svg
                                                                style={{ width: '50px', height: '30px' }}
                                                            />
                                                        </Tooltip>
                                                    </td>
                                                    <td>{cruise.vessel_details ? cruise.vessel_details.vessel_name : 'N/A'}</td>
                                                    <td>{cruise.legs && cruise.legs[0] ? cruise.legs[0].start_date : 'N/A'}</td>
                                                    <td>{cruise.legs && cruise.legs[cruise.legs.length - 1] ? cruise.legs[cruise.legs.length - 1].end_date : 'N/A'}</td>
                                                    <td>
                                                        <button
                                                            onClick={() => handleSeeDetails(cruise.cruise_id)}
                                                            className="details-button"
                                                            aria-label={`See details for ${cruise.cruise_name}`}
                                                        >
                                                            See Details
                                                        </button>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                                <Pagination
                                    totalItems={filteredCruises.length}
                                    itemsPerPage={itemsPerPage}
                                    currentPage={currentPage}
                                    onPageChange={handlePageChange}
                                />
                            </>
                        )}
                    </section>
                )}
                {activeTab === 'map' && <MapComponent />}
            </main>
        </div>
    );
};

export default CruiseListPage;
