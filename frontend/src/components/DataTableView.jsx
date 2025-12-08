import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Download } from 'lucide-react';
import './DataTableView.css';

const DataTableView = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [totalRecords, setTotalRecords] = useState(0);
    const [selectedMonths, setSelectedMonths] = useState([]);

    // Sorting State
    const [sortBy, setSortBy] = useState('date');
    const [sortOrder, setSortOrder] = useState('asc'); // 'asc' or 'desc'

    // Config
    const limit = 31;

    const months = [
        { id: 1, name: 'Jan' }, { id: 2, name: 'Feb' }, { id: 3, name: 'Mar' },
        { id: 4, name: 'Apr' }, { id: 5, name: 'May' }, { id: 6, name: 'Jun' },
        { id: 7, name: 'Jul' }, { id: 8, name: 'Aug' }, { id: 9, name: 'Sep' },
        { id: 10, name: 'Oct' }, { id: 11, name: 'Nov' }, { id: 12, name: 'Dec' },
    ];

    useEffect(() => {
        fetchTableData();
    }, [page, selectedMonths, sortBy, sortOrder]);

    const fetchTableData = async () => {
        setLoading(true);
        try {
            let query = `?page=${page}&limit=${limit}&sort_by=${sortBy}&sort_order=${sortOrder}`;
            if (selectedMonths.length > 0) {
                query += '&' + selectedMonths.map(m => `months=${m}`).join('&');
            }

            const res = await fetch(`http://localhost:8000/api/table${query}`);
            const result = await res.json();

            setData(result.data);
            setTotalPages(result.pages);
            setTotalRecords(result.total);

            if (result.pages > 0 && page > result.pages) {
                setPage(1);
            }

        } catch (error) {
            console.error("Failed to fetch table data", error);
        }
        setLoading(false);
    };

    const handleSort = (columnKey) => {
        if (sortBy === columnKey) {
            // Toggle order
            setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
        } else {
            // New column, default to asc
            setSortBy(columnKey);
            setSortOrder('asc');
        }
    };

    const toggleMonth = (monthId) => {
        setSelectedMonths(prev => {
            const newSelection = prev.includes(monthId)
                ? prev.filter(id => id !== monthId)
                : [...prev, monthId];
            setPage(1);
            return newSelection;
        });
    };

    const toggleAllMonths = () => {
        setSelectedMonths([]);
        setPage(1);
    };

    const handleDownload = () => {
        let query = `?`;
        if (selectedMonths.length > 0) {
            query += selectedMonths.map(m => `months=${m}`).join('&');
        }
        window.location.href = `http://localhost:8000/api/download${query}`;
    };

    // Helper to render sort icon
    const renderSortIcon = (columnKey) => {
        if (sortBy !== columnKey) return null;
        return <span style={{ marginLeft: '4px', fontSize: '0.8rem' }}>{sortOrder === 'asc' ? '▲' : '▼'}</span>;
    };

    return (
        <div className="data-table-view">
            {/* Filter Chips */}
            <div className="filter-container" style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', padding: '0 0.5rem' }}>
                <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', display: 'flex', alignItems: 'center', paddingTop: '0.25rem' }}>Filter Months:</span>
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

            <div className="table-controls">
                <span className="table-stats">
                    Showing {(page - 1) * limit + 1}-{Math.min(page * limit, totalRecords)} of {totalRecords} records
                </span>
                <button className="region-btn" onClick={handleDownload} style={{ gap: '0.5rem', fontSize: '0.85rem' }}>
                    <Download size={16} /> Download CSV
                </button>
            </div>

            <div className="table-container">
                <table className="data-table">
                    <thead>
                        <tr>
                            <th onClick={() => handleSort('date')}>Date {renderSortIcon('date')}</th>
                            <th onClick={() => handleSort('month')}>Month {renderSortIcon('month')}</th>
                            <th onClick={() => handleSort('avg_temp_overall')}>Temp (°C) {renderSortIcon('avg_temp_overall')}</th>
                            <th onClick={() => handleSort('avg_sal_overall')}>Salinity (PSU) {renderSortIcon('avg_sal_overall')}</th>
                            <th onClick={() => handleSort('avg_sound_overall')}>Sound Speed (m/s) {renderSortIcon('avg_sound_overall')}</th>
                            <th onClick={() => handleSort('avg_density_overall')}>Density (kg/m³) {renderSortIcon('avg_density_overall')}</th>
                            <th onClick={() => handleSort('avg_conductivity_overall')}>Conductivity (S/m) {renderSortIcon('avg_conductivity_overall')}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr><td colSpan="7" style={{ textAlign: 'center', padding: '2rem' }}>Loading...</td></tr>
                        ) : data.length === 0 ? (
                            <tr><td colSpan="7" style={{ textAlign: 'center', padding: '2rem' }}>No data found</td></tr>
                        ) : (
                            data.map((row, index) => (
                                <tr key={index}>
                                    <td>{row.date}</td>
                                    <td>{row.month}</td>
                                    <td>{row.avg_temp_overall?.toFixed(2)}</td>
                                    <td>{row.avg_sal_overall?.toFixed(2)}</td>
                                    <td>{row.avg_sound_overall?.toFixed(2)}</td>
                                    <td>{row.avg_density_overall?.toFixed(2)}</td>
                                    <td>{row.avg_conductivity_overall?.toFixed(5)}</td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            <div className="pagination-controls">
                <button
                    className="page-btn"
                    disabled={page === 1}
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                >
                    <ChevronLeft size={16} />
                </button>
                <span style={{ color: 'var(--text-secondary)' }}>
                    Page <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{page}</span> of {totalPages}
                </span>
                <button
                    className="page-btn"
                    disabled={page === totalPages || totalPages === 0}
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                >
                    <ChevronRight size={16} />
                </button>
            </div>
        </div>
    );
};
export default DataTableView;
