import React from 'react';
import { Hexagon, Mic, Send, Lightbulb, Copy } from 'lucide-react';
import './Sidebar.css';

const Sidebar = () => {
    return (
        <div className="sidebar">
            {/* Brand */}
            <div className="brand">
                <Hexagon className="brand-icon" size={32} strokeWidth={2.5} />
                <div className="brand-text">
                    <h1>FloatChat</h1>
                    <span>ARGO Data Intelligence</span>
                </div>
            </div>

            {/* Chat Area */}
            <div className="chat-container">
                <div className="message-bot">
                    <p>
                        Welcome to FloatChat! I'm your AI assistant for exploring ARGO ocean data. I
                        can help you find floats by location, compare data, and analyze ocean
                        parameters. Try asking me something like "Show me floats near Mumbai" or "Compare
                        temperature data from different regions".
                    </p>
                    <div style={{ marginTop: '0.5rem', display: 'flex', justifyContent: 'flex-end' }}>
                        <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>9:51:41 AM</span>
                        <Copy size={14} style={{ marginLeft: 'auto', color: 'var(--text-secondary)', cursor: 'pointer' }} />
                    </div>
                </div>
            </div>

            {/* Suggestions */}
            <div className="suggestions">
                <h3><Lightbulb size={16} color="var(--accent-cyan)" /> Try asking:</h3>
                <div className="suggestion-chip">Compare Arabian Sea and Bay of Bengal and show differences</div>
                <div className="suggestion-chip">Show salinity profiles near the equator</div>
                <div className="suggestion-chip">Compare BGC parameters in Arabian Sea</div>
            </div>

            {/* Input Area */}
            <div className="chat-input-area">
                <input
                    type="text"
                    className="chat-input"
                    placeholder="Ask about ARGO ocean data..."
                />
                <div className="input-actions">
                    <button className="icon-btn"><Mic size={18} /></button>
                    <button className="icon-btn send-btn"><Send size={18} /></button>
                </div>
            </div>
        </div>
    );
};

export default Sidebar;
