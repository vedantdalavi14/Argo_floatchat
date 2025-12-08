import React, { useState } from 'react';
import { Thermometer, Droplets, Activity, Wind, Globe, AlertTriangle, User, RefreshCw } from 'lucide-react';
import './Header.css';

const Header = () => {
    const [refreshing, setRefreshing] = useState(false);

    const handleRefresh = async () => {
        setRefreshing(true);
        try {
            await fetch('http://localhost:8000/api/reload');
            // Force a page reload or event to update charts. 
            // For now, simple page reload is effective.
            window.location.reload();
        } catch (error) {
            console.error(error);
        }
        setRefreshing(false);
    };

    return (
        <header className="header">
            {/* Stats Chips */}
            <div className="stats-container">
                <div className="stat-chip stat-temp">
                    <Thermometer size={16} className="stat-icon" />
                    <span>28.5°C</span>
                </div>
                <div className="stat-chip stat-psu">
                    <Droplets size={16} className="stat-icon" />
                    <span>35.0 PSU</span>
                </div>
                <div className="stat-chip stat-pressure">
                    <Activity size={16} className="stat-icon" /> {/* Using Activity for dbar/pressure abstractly */}
                    <span>1013.2 dbar</span>
                </div>
                <div className="stat-chip stat-wind">
                    <Wind size={16} className="stat-icon" />
                    <span>2.1 m/s</span>
                </div>
            </div>

            {/* Actions */}
            <div className="header-actions">
                <button
                    className={`region-btn ${refreshing ? 'animate-spin' : ''}`}
                    onClick={handleRefresh}
                    title="Reload Data"
                >
                    <RefreshCw size={16} />
                    {refreshing ? ' Reloading...' : ' Refresh Data'}
                </button>

                <button className="region-btn">
                    <Globe size={16} /> Indian Ocean
                </button>

                <div className="incois-badge">
                    <span className="incois-dot"></span> INCOIS
                </div>

                <button className="icon-action">
                    <AlertTriangle size={20} />
                </button>
                <button className="icon-action">
                    <User size={20} />
                </button>
            </div>
        </header>
    );
};

export default Header;
