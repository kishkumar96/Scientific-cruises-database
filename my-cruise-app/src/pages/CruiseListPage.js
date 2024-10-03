import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import MapComponent from '../components/maps/CruiseListMap'; // Corrected path
import CountryFlag from 'react-country-flag';
import Tooltip from '../components/Tooltip'; // Corrected path for Tooltip
import './CruiseListPage.css'; // Keep this as it is, since it's in the same directory as CruiseListPage.js
import countries from 'i18n-iso-countries';

countries.registerLocale(require('i18n-iso-countries/langs/en.json'));

const Pagination = ({ totalItems, itemsPerPage, currentPage, onPageChange }) => {
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    if (totalPages <= 1) return null;

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

/**
 * CruiseListPage component renders a list of scientific cruises with search and filter functionalities.
 * It also provides pagination and navigation to cruise details.
 *
 * @component
 * @example
 * return (
 *   <CruiseListPage />
 * )
 *
 * @returns {JSX.Element} The rendered CruiseListPage component.
 *
 * @typedef {Object} Cruise
 * @property {string} cruise_id - The unique identifier for the cruise.
 * @property {string} cruise_name - The name of the cruise.
 * @property {string} status_name - The status of the cruise.
 * @property {string} iso2_country - The ISO 3166-1 alpha-2 code of the country.
 * @property {Object} vessel_details - The details of the vessel.
 * @property {string} vessel_details.vessel_name - The name of the vessel.
 * @property {Array} legs - The legs of the cruise.
 * @property {Object} legs[0] - The first leg of the cruise.
 * @property {string} legs[0].start_date - The start date of the first leg.
 * @property {Object} legs[legs.length - 1] - The last leg of the cruise.
 * @property {string} legs[legs.length - 1].end_date - The end date of the last leg.
 *
 * @typedef {Object} Status
 * @property {string} id - The unique identifier for the status.
 * @property {string} name - The name of the status.
 *
 * @typedef {Object} Filters
 * @property {string} status - The status filter.
 *
 * @typedef {Object} PaginationProps
 * @property {number} totalItems - The total number of items.
 * @property {number} itemsPerPage - The number of items per page.
 * @property {number} currentPage - The current page number.
 * @property {function} onPageChange - The function to handle page change.
 */
const CruiseListPage = () => {
    const [activeTab, setActiveTab] = useState('list');
    const [currentPage, setCurrentPage] = useState(1);
    const [itemsPerPage] = useState(10);
    const [searchTerm, setSearchTerm] = useState('');
    const [debouncedSearchTerm, setDebouncedSearchTerm] = useState(searchTerm);
    const [filters, setFilters] = useState({ status: '' });
    const [cruises, setCruises] = useState([]);
    const [statuses, setStatuses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const apiUrl = process.env.REACT_APP_API_URL || 'https://cruisedb.corp.spc.int/api';

    const handleSearchChange = (e) => setDebouncedSearchTerm(e.target.value);

    const getCountryName = useCallback((isoCode) => {
        return countries.getName(isoCode, "en", { select: "official" }) || 'No country';
    }, []);

    useEffect(() => {
        const handler = setTimeout(() => {
            setSearchTerm(debouncedSearchTerm);
        }, 300);

        return () => {
            clearTimeout(handler);
        };
    }, [debouncedSearchTerm]);

    const filteredCruises = useMemo(() => cruises.filter(cruise => {
        const name = cruise.cruise_name.toLowerCase();
        const status = cruise.status_name;
        return name.includes(searchTerm.toLowerCase()) &&
            (!filters.status || status === filters.status);
    }), [cruises, searchTerm, filters.status]);

    const indexOfLastCruise = currentPage * itemsPerPage;
    const indexOfFirstCruise = indexOfLastCruise - itemsPerPage;
    const currentCruises = filteredCruises.slice(indexOfFirstCruise, indexOfLastCruise);

    const handlePageChange = pageNumber => setCurrentPage(pageNumber);
    const handleSeeDetails = id => navigate(`/cruises/${id}`);

    useEffect(() => {
        const fetchCruises = async () => {
            try {
                const response = await fetch(`${apiUrl}/cruises/`, {
                    headers: { 'Accept': 'application/json' }
                });
                if (!response.ok) throw new Error(`Failed to fetch cruises. Status: ${response.status}`);
                const data = await response.json();
                setCruises(data);
            } catch (error) {
                setError('An error occurred while loading cruises. Please try again later.');
            } finally {
                setLoading(false);
            }
        };
        fetchCruises();
    }, [apiUrl]);

    useEffect(() => {
        const fetchStatuses = async () => {
            try {
                const response = await fetch(`${apiUrl}/statuses/`, {
                    headers: { 'Accept': 'application/json' }
                });
                if (!response.ok) throw new Error(`Failed to fetch statuses. Status: ${response.status}`);
                const data = await response.json();
                setStatuses(data);
            } catch (error) {
                setError('An error occurred while loading statuses. Please try again later.');
            }
        };
        fetchStatuses();
    }, [apiUrl]);

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
