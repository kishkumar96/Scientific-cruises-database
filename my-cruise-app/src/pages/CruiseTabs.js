import React, { useState } from 'react';
import CruiseList from './CruiseList'; // Your cruise list component
import MapComponent from './MapComponent'; // Your map component

const CruiseTabs = () => {
  const [activeTab, setActiveTab] = useState('list'); // 'list' or 'map'

  const handleTabClick = (tab) => {
    setActiveTab(tab);
  };

  return (
    <div className="cruise-tabs-container">
      <div className="tab-buttons">
        <button
          onClick={() => handleTabClick('list')}
          className={activeTab === 'list' ? 'active' : ''}
        >
          List Cruises
        </button>
        <button
          onClick={() => handleTabClick('map')}
          className={activeTab === 'map' ? 'active' : ''}
        >
          Map
        </button>
      </div>
      <div className="tab-content">
        {activeTab === 'list' && <CruiseList />}
        {activeTab === 'map' && <MapComponent />}
      </div>
    </div>
  );
};

export default CruiseTabs;
