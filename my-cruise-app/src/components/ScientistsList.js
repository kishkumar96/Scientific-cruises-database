import React from 'react';
import './ScientistsList.css';

const ScientistsList = ({ scientists }) => {
    if (!Array.isArray(scientists) || scientists.length === 0) {
        return <p>No scientists found for this cruise.</p>;
    }

    return (
        <div className="scientists-container">
            <table className="scientists-table">
                <thead>
                    <tr>
                        <th>First Name</th>
                        <th>Last Name</th>
                    </tr>
                </thead>
                <tbody>
                    {scientists.map((scientist, index) => (
                        <tr key={index}>
                            <td>{scientist.first_name}</td>
                            <td>{scientist.last_name}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default ScientistsList;
