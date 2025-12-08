import React, { useState, useRef, useEffect } from 'react';
import { Hexagon, Mic, Send, Lightbulb, Copy, User } from 'lucide-react';
import './Sidebar.css';

const Sidebar = () => {
    const [messages, setMessages] = useState([
        {
            type: 'bot',
            text: "Welcome to FloatChat! I'm your AI assistant for exploring ARGO ocean data. Try asking me about temperature, salinity, or the float's location.",
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToBottom, [messages]);

    const handleSendMessage = async () => {
        if (!inputValue.trim()) return;

        const userMsg = {
            type: 'user',
            text: inputValue,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };

        setMessages(prev => [...prev, userMsg]);
        setInputValue('');
        setLoading(true);

        try {
            const response = await fetch('http://localhost:8000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMsg.text })
            });
            const data = await response.json();

            const botMsg = {
                type: 'bot',
                text: data.reply,
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            };
            setMessages(prev => [...prev, botMsg]);
        } catch (error) {
            console.error("Chat error:", error);
            const errorMsg = {
                type: 'bot',
                text: "Sorry, I'm having trouble connecting to the server.",
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') handleSendMessage();
    };

    const handleSuggestion = (text) => {
        setInputValue(text);
        // Optional: auto-send
        // handleSendMessage(); 
    };

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
                {messages.map((msg, idx) => (
                    <div key={idx} className={msg.type === 'bot' ? 'message-bot' : 'message-user'}>
                        <p>{msg.text}</p>
                        <div className="message-meta">
                            <span>{msg.time}</span>
                            {msg.type === 'bot' && <Copy size={12} className="copy-icon" />}
                        </div>
                    </div>
                ))}

                {loading && (
                    <div className="message-bot">
                        <div className="typing-indicator">
                            <span></span><span></span><span></span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Suggestions */}
            <div className="suggestions">
                <h3><Lightbulb size={16} color="var(--accent-cyan)" /> Try asking:</h3>
                <div className="suggestion-chip" onClick={() => handleSuggestion("What is the average temperature?")}>
                    What is the average temperature?
                </div>
                <div className="suggestion-chip" onClick={() => handleSuggestion("Where is the float now?")}>
                    Where is the float now?
                </div>
                <div className="suggestion-chip" onClick={() => handleSuggestion("What is the salinity?")}>
                    What is the salinity?
                </div>
            </div>

            {/* Input Area */}
            <div className="chat-input-area">
                <input
                    type="text"
                    className="chat-input"
                    placeholder="Ask about ARGO ocean data..."
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                />
                <div className="input-actions">
                    <button className="icon-btn"><Mic size={18} /></button>
                    <button className="icon-btn send-btn" onClick={handleSendMessage}><Send size={18} /></button>
                </div>
            </div>
        </div>
    );
};

export default Sidebar;
