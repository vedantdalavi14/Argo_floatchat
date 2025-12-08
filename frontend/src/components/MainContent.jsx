import React, { useState } from 'react';
import { Map, BarChart2, Table, Code } from 'lucide-react'; // Code icon for the </> button
import './MainContent.css';
import ChartsView from './ChartsView';
import MapView from './MapView';
import DataTableView from './DataTableView';

const MainContent = () => {
    const [activeTab, setActiveTab] = useState('charts'); // Default to charts as per Img 1? Or Map Img 2? Let's do Charts.

    return (
        <main className="main-content">
            <div className="content-header">
                <h2 className="content-title">Ocean Data Explorer</h2>
                <button className="icon-btn" style={{ backgroundColor: 'var(--bg-card)', padding: '0.5rem' }}>
                    <Code size={18} />
                </button>
            </div>

            {/* Main Tabs */}
            <div className="tabs-container">
                <button
                    className={`tab-btn ${activeTab === 'map' ? 'active' : ''}`}
                    onClick={() => setActiveTab('map')}
                >
                    <Map size={18} /> Map View
                </button>
                <button
                    className={`tab-btn ${activeTab === 'charts' ? 'active' : ''}`}
                    onClick={() => setActiveTab('charts')}
                >
                    <BarChart2 size={18} /> Charts
                </button>
                <button
                    className={`tab-btn ${activeTab === 'table' ? 'active' : ''}`}
                    onClick={() => setActiveTab('table')}
                >
                    <Table size={18} /> Data Table
                </button>
            </div>

            {/* View Content */}
            <div className="view-container">
                {activeTab === 'charts' && <ChartsView />}
                {activeTab === 'map' && <MapView />}
                {activeTab === 'table' && <DataTableView />}
            </div>
        </main>
    );
};

export default MainContent;
