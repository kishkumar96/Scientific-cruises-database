import React from 'react';
import './LegTable.css';

const LegTable = ({ legs }) => {
    if (!legs || legs.length === 0) {
        return <p>No legs available for this cruise.</p>;
    }

    return (
        <table className="legs-table">
            <thead>
                <tr>
                    <th>Leg Number</th>
                    <th>Departure Port</th>
                    <th>Arrival Port</th>
                    <th>Start Date</th>
                    <th>End Date</th>
                </tr>
            </thead>
            <tbody>
                {legs.map((leg, index) => (
                    <tr key={index}>
                        <td>{leg.leg_number}</td>
                        <td>{leg.departure_port}</td>
                        <td>{leg.arrival_port}</td>
                        <td>{leg.start_date || 'N/A'}</td>
                        <td>{leg.end_date || 'N/A'}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    );
};

export default LegTable;
