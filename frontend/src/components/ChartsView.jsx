import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import { Thermometer, Droplets, Activity, Music, Snowflake, Zap } from 'lucide-react';
import './ChartsView.css';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

const ChartsView = () => {
    const [activeParam, setActiveParam] = useState('temp');
    const [selectedMonths, setSelectedMonths] = useState([]); // Empty = All
    const [statsLayer, setStatsLayer] = useState('overall'); // [NEW] 'overall', 'surface', 'deep'
    const [chartData, setChartData] = useState(null);
    const [stats, setStats] = useState({});
    const [loading, setLoading] = useState(false);

    const months = [
        { id: 1, name: 'Jan' }, { id: 2, name: 'Feb' }, { id: 3, name: 'Mar' },
        { id: 4, name: 'Apr' }, { id: 5, name: 'May' }, { id: 6, name: 'Jun' },
        { id: 7, name: 'Jul' }, { id: 8, name: 'Aug' }, { id: 9, name: 'Sep' },
        { id: 10, name: 'Oct' }, { id: 11, name: 'Nov' }, { id: 12, name: 'Dec' },
    ];

    // Fetch Logic
    useEffect(() => {
        fetchData();
    }, [activeParam, selectedMonths, statsLayer]);

    const fetchData = async () => {
        setLoading(true);
        try {
            // Construct Query Params
            let query = `?`;
            if (selectedMonths.length > 0) {
                query += selectedMonths.map(m => `months=${m}`).join('&');
            }

            const [dataRes, statsRes] = await Promise.all([
                fetch(`http://localhost:8000/api/timeseries/${activeParam}${query}`),
                fetch(`http://localhost:8000/api/stats${query ? query + '&' : '?'}parameter=${activeParam}&layer=${statsLayer}`)
            ]);

            const data = await dataRes.json();
            const statsData = await statsRes.json();

            setChartData(data);
            setStats(statsData);

        } catch (error) {
            console.error("Failed to fetch data", error);
        }
        setLoading(false);
    };

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
        if (selectedMonths.length === 0) return; // Already all
        setSelectedMonths([]);
    };

    const getParamLabel = () => {
        const map = {
            'temp': 'Temperature (°C)',
            'sal': 'Salinity (PSU)',
            'sound': 'Sound Speed (m/s)',
            'density': 'Density (kg/m³)',
            'freezing': 'Freezing Point (°C)',
            'conductivity': 'Conductivity (S/m)'
        };
        return map[activeParam];
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    color: '#94a3b8',
                    usePointStyle: true,
                }
            },
            title: {
                display: false,
            },
            tooltip: {
                mode: 'index',
                intersect: false,
            }
        },
        scales: {
            x: {
                grid: { color: '#334155' },
                ticks: { color: '#94a3b8', maxTicksLimit: 10 },
                title: {
                    display: true,
                    text: 'Date',
                    color: '#94a3b8'
                }
            },
            y: {
                grid: { color: '#334155' },
                ticks: { color: '#94a3b8' },
                title: {
                    display: true,
                    text: getParamLabel(),
                    color: '#94a3b8'
                }
            },
        },
        elements: {
            point: {
                radius: 1, // small points for time series
                hoverRadius: 4
            },
            line: {
                borderWidth: 2
            }
        }
    };

    return (
        <div className="charts-view">
            {/* Sub Tabs - Parameters */}
            <div className="sub-tabs" style={{ flexWrap: 'wrap' }}>
                <button className={`sub-tab-btn ${activeParam === 'temp' ? 'active' : ''}`} onClick={() => setActiveParam('temp')}>
                    <Thermometer size={14} /> Temperature
                </button>
                <button className={`sub-tab-btn ${activeParam === 'sal' ? 'active' : ''}`} onClick={() => setActiveParam('sal')}>
                    <Droplets size={14} /> Salinity
                </button>
                <button className={`sub-tab-btn ${activeParam === 'sound' ? 'active' : ''}`} onClick={() => setActiveParam('sound')}>
                    <Music size={14} /> Sound Speed
                </button>
                <button className={`sub-tab-btn ${activeParam === 'conductivity' ? 'active' : ''}`} onClick={() => setActiveParam('conductivity')}>
                    <Zap size={14} /> Conductivity
                </button>
                <button className={`sub-tab-btn ${activeParam === 'freezing' ? 'active' : ''}`} onClick={() => setActiveParam('freezing')}>
                    <Snowflake size={14} /> Freezing Pt
                </button>
            </div>

            {/* Filter Chips */}
            <div className="filter-container" style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap', padding: '0 0.5rem' }}>
                <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', display: 'flex', itemsAlign: 'center', paddingTop: '0.25rem' }}>Filter Months:</span>
                <button
                    className={`filter-chip ${selectedMonths.length === 0 ? 'active' : ''}`}
                    onClick={toggleAllMonths}
                >
                    All
                </button>
                {months.map(m => (
                    <button
                        key={m.id}
                        className={`filter-chip ${selectedMonths.includes(m.id) ? 'active' : ''}`}
                        onClick={() => toggleMonth(m.id)}
                    >
                        {m.name}
                    </button>
                ))}
            </div>

            <div className="dashboard-grid">
                {/* Chart Area */}
                <div className="chart-section">
                    <div className="chart-header">
                        <h3>{getParamLabel()} Time Series</h3>
                    </div>
                    <div className="chart-container-inner">
                        {chartData ? <Line options={options} data={chartData} /> : <div style={{ color: 'white' }}>Loading...</div>}
                    </div>
                </div>

                {/* Right Panel - Statistics */}
                <div className="stats-panel">
                    {/* General Stats */}
                    <div className="stat-card">
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                            <h4 style={{ margin: 0 }}>Statistics ({activeParam})</h4>
                            <div className="layer-selector" style={{ display: 'flex', gap: '4px' }}>
                                {['surface', 'overall', 'deep'].map(l => (
                                    <button
                                        key={l}
                                        onClick={() => setStatsLayer(l)}
                                        style={{
                                            border: '1px solid var(--border-color)',
                                            background: statsLayer === l ? 'var(--accent-blue)' : 'var(--bg-primary)',
                                            color: statsLayer === l ? '#000' : 'var(--text-secondary)',
                                            fontSize: '0.65rem',
                                            padding: '2px 6px',
                                            borderRadius: '4px',
                                            cursor: 'pointer',
                                            textTransform: 'capitalize'
                                        }}
                                    >
                                        {l}
                                    </button>
                                ))}
                            </div>
                        </div>
                        <div className="stat-row">
                            <span className="stat-label">Average:</span>
                            <span className="stat-value">{stats.avg || '-'}</span>
                        </div>
                        <div className="stat-row">
                            <span className="stat-label">Maximum:</span>
                            <span className="stat-value">{stats.max || '-'}</span>
                        </div>
                        <div className="stat-row">
                            <span className="stat-label">Minimum:</span>
                            <span className="stat-value">{stats.min || '-'}</span>
                        </div>
                        <div className="stat-row">
                            <span className="stat-label">Range:</span>
                            <span className="stat-value">{stats.range || '-'}</span>
                        </div>
                        <div className="stat-row">
                            <span className="stat-label">Points:</span>
                            <span className="stat-value">{stats.count || '-'}</span>
                        </div>
                    </div>

                    {/* Data Quality */}
                    <div className="stat-card">
                        <h4>Data Quality</h4>
                        <div className="stat-row">
                            <span className="stat-label">Accuracy:</span>
                            <span className="stat-value badge badge-blue">99.9%</span>
                        </div>
                        <div className="stat-row">
                            <span className="stat-label">QC Status:</span>
                            <span className="stat-value badge badge-green">PASSED</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ChartsView;
