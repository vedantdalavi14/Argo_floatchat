import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { MapPin, Navigation } from 'lucide-react';
import './MapView.css';

// Fix Leaflet marker icons in React
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

// Component to recenter map when positions change
const RecenterMap = ({ positions }) => {
    const map = useMap();
    useEffect(() => {
        if (positions && positions.length > 0) {
            const bounds = L.latLngBounds(positions);
            map.fitBounds(bounds, { padding: [50, 50] });
        }
    }, [positions, map]);
    return null;
};

const MapView = () => {
    const [positions, setPositions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedMonths, setSelectedMonths] = useState([]);

    const months = [
        { id: 1, name: 'Jan' }, { id: 2, name: 'Feb' }, { id: 3, name: 'Mar' },
        { id: 4, name: 'Apr' }, { id: 5, name: 'May' }, { id: 6, name: 'Jun' },
        { id: 7, name: 'Jul' }, { id: 8, name: 'Aug' }, { id: 9, name: 'Sep' },
        { id: 10, name: 'Oct' }, { id: 11, name: 'Nov' }, { id: 12, name: 'Dec' },
    ];

    useEffect(() => {
        let query = '';
        if (selectedMonths.length > 0) {
            query = '?' + selectedMonths.map(m => `months=${m}`).join('&');
        }

        setLoading(true);
        fetch(`http://localhost:8000/api/track${query}`)
            .then(res => res.json())
            .then(data => {
                // Convert to [lat, lon] array
                const coords = data.map(d => [d.avg_latitude, d.avg_longitude]);
                setPositions(coords);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, [selectedMonths]);

    const toggleMonth = (monthId) => {
        setSelectedMonths(prev => {
            if (prev.includes(monthId)) {
                return prev.filter(id => id !== monthId);
            } else {
                return [...prev, monthId];
            }
        });
    };

    const toggleAllMonths = () => {
        if (selectedMonths.length === 0) return;
        setSelectedMonths([]);
    };

    const startPoint = positions.length > 0 ? positions[0] : null;
    const endPoint = positions.length > 0 ? positions[positions.length - 1] : null;

    return (
        <div className="map-view">
            <div className="map-container-wrapper">
                <div style={{ position: 'absolute', top: 10, left: 60, right: 10, zIndex: 999, pointerEvents: 'none' }}>
                    {/* Filter Chips Overlay */}
                    <div className="filter-container" style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', pointerEvents: 'auto', background: 'rgba(15, 23, 42, 0.8)', padding: '8px', borderRadius: '8px', width: 'fit-content' }}>
                        <span style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', display: 'flex', alignItems: 'center', marginRight: '4px' }}>Filter:</span>
                        <button
                            className={`filter-chip ${selectedMonths.length === 0 ? 'active' : ''}`}
                            onClick={toggleAllMonths}
                            style={{ fontSize: '0.75rem', padding: '2px 8px' }}
                        >
                            All
                        </button>
                        {months.map(m => (
                            <button
                                key={m.id}
                                className={`filter-chip ${selectedMonths.includes(m.id) ? 'active' : ''}`}
                                onClick={() => toggleMonth(m.id)}
                                style={{ fontSize: '0.75rem', padding: '2px 8px' }}
                            >
                                {m.name}
                            </button>
                        ))}
                    </div>
                </div>

                <MapContainer center={[10, 75]} zoom={4} style={{ height: '100%', width: '100%' }}>
                    <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />

                    {positions.length > 0 && (
                        <>
                            {positions.map((pos, idx) => (
                                <CircleMarker
                                    key={idx}
                                    center={pos}
                                    pathOptions={{ color: '#3b82f6', fillColor: '#3b82f6', fillOpacity: 0.7 }}
                                    radius={6}
                                >
                                    <Popup>Lat: {pos[0].toFixed(2)}, Lon: {pos[1].toFixed(2)}</Popup>
                                </CircleMarker>
                            ))}
                            <RecenterMap positions={positions} />
                        </>
                    )}
                </MapContainer>
            </div>

            <div className="float-details-panel">
                <div className="details-header">
                    <h3>Float Details</h3>
                    <button className="region-btn" style={{ fontSize: '0.8rem', padding: '0.25rem 0.5rem' }}>Indian Ocean</button>
                </div>

                {loading ? (
                    <div className="empty-state"><p>Loading track...</p></div>
                ) : positions.length > 0 ? (
                    <div style={{ color: 'var(--text-primary)' }}>
                        <div className="stat-card" style={{ border: 'none', padding: '0' }}>
                            <div className="stat-row">
                                <span className="stat-label">Total Points:</span>
                                <span className="stat-value">{positions.length}</span>
                            </div>
                            <div className="stat-row" style={{ marginTop: '1rem' }}>
                                <span className="stat-label">Status:</span>
                                <span className="stat-value highlight" style={{ color: '#4ade80' }}>Active</span>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="empty-state">
                        <div className="empty-icon-circle">
                            <Navigation size={32} color="#64748b" />
                        </div>
                        <p>No track data available</p>
                    </div>
                )}

            </div>
        </div >
    );
};

export default MapView;
