import React, { useState, useRef, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { getConversationById, getConversations, getHealth, sendChatMessage } from '../../services/supportApi';
import { useAuth } from '../../context/AuthContext';
import { ChatQuickActions } from './components/ChatQuickActions';
import { TypingIndicator } from './components/TypingIndicator';

const FALLBACK_CUSTOMER_ID = 'cust_001';
const INITIAL_BOT_MESSAGE = {
    id: 1,
    text: "Hello! I'm your AI support agent. I can help you with orders, refunds, account issues, and more. I have access to your account and can take actions on your behalf.",
    sender: 'bot',
    timestamp: new Date()
};

const resolveCustomerId = (routeId) => {
    if (!routeId || routeId === 'newchat') return FALLBACK_CUSTOMER_ID;
    return routeId;
};

export function AgenticCustomerSupport() {
    const { id } = useParams();
    const { user, isAdmin, signOut } = useAuth();
    const navigate = useNavigate();
    const customerId = user?.customer_id || resolveCustomerId(id);
    const [messages, setMessages] = useState([INITIAL_BOT_MESSAGE]);
    const [input, setInput] = useState('');
    const [isProcessing, setIsProcessing] = useState(false);
    const [agentActions, setAgentActions] = useState([]);
    const [conversationId, setConversationId] = useState(null);
    const [apiStatus, setApiStatus] = useState('checking');
    const [copiedMessageId, setCopiedMessageId] = useState(null);
    const [conversationHistory, setConversationHistory] = useState([]);
    const [historyLoading, setHistoryLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const customerData = {
        name: user?.name || 'Authenticated User',
        email: user?.email || 'customer@example.com',
        accountStatus: 'Authenticated',
        recentOrders: [
            { id: "ORD-12345", item: "Wireless Headphones", status: "Delivered", date: "Nov 10, 2025", amount: 129.99 },
            { id: "ORD-12344", item: "USB-C Cable", status: "Shipped", date: "Nov 15, 2025", amount: 19.99 }
        ],
        supportTickets: [
            { id: "TKT-789", issue: "Defective product", status: "Open" }
        ]
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, agentActions]);

    const checkBackendHealth = async () => {
        setApiStatus('checking');
        try {
            await getHealth();
            setApiStatus('online');
        } catch {
            setApiStatus('offline');
        }
    };

    useEffect(() => {
        checkBackendHealth();
    }, []);

    const loadConversationHistory = async () => {
        if (!customerId) return;
        setHistoryLoading(true);
        try {
            const history = await getConversations(30);
            setConversationHistory(Array.isArray(history) ? history : []);
        } catch {
            setConversationHistory([]);
        } finally {
            setHistoryLoading(false);
        }
    };

    useEffect(() => {
        loadConversationHistory();
    }, [customerId]);

    const openConversation = async (idToOpen) => {
        try {
            const data = await getConversationById(idToOpen);
            const loadedMessages = (data?.messages || []).map((msg, index) => ({
                id: `${idToOpen}-${index}`,
                text: msg.content,
                sender: msg.role === 'assistant' ? 'bot' : 'user',
                timestamp: msg.timestamp ? new Date(msg.timestamp) : new Date()
            }));

            setConversationId(idToOpen);
            setMessages(loadedMessages.length ? loadedMessages : [{ ...INITIAL_BOT_MESSAGE, id: Date.now() }]);
            setAgentActions((prev) => ([
                ...prev,
                {
                    id: Date.now() + 10,
                    text: `Loaded conversation ${idToOpen}`,
                    type: 'database',
                    icon: '📚',
                    timestamp: new Date()
                }
            ]));
        } catch {
            setAgentActions((prev) => ([
                ...prev,
                {
                    id: Date.now() + 11,
                    text: `Unable to load conversation ${idToOpen}`,
                    type: 'error',
                    icon: '⚠️',
                    timestamp: new Date()
                }
            ]));
        }
    };

    const resetConversation = () => {
        setMessages([{ ...INITIAL_BOT_MESSAGE, id: Date.now() }]);
        setAgentActions([]);
        setConversationId(null);
        setInput('');
        setCopiedMessageId(null);
    };

    const copyMessageText = async (messageId, text) => {
        try {
            await navigator.clipboard.writeText(text);
            setCopiedMessageId(messageId);
            setTimeout(() => setCopiedMessageId(null), 1200);
        } catch {
            setCopiedMessageId(null);
        }
    };

    const handleSend = async (overrideText) => {
        const messageToSend = (overrideText ?? input).trim();
        if (!messageToSend) return;

        const userMessage = {
            id: Date.now(),
            text: messageToSend,
            sender: 'user',
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        if (!overrideText) {
            setInput('');
        }
        setIsProcessing(true);
        setAgentActions(prev => ([
            ...prev,
            {
                id: Date.now() + 1,
                text: 'Classifying intent and routing to the right specialist agent',
                type: 'action',
                icon: '🧭',
                timestamp: new Date()
            }
        ]));

        try {
            const data = await sendChatMessage({
                message: messageToSend,
                customer_id: customerId,
                channel: 'web',
                conversation_id: conversationId,
                session_id: conversationId,
                industry: 'saas'
            });

            if (data?.conversation_id) {
                setConversationId(data.conversation_id);
            }

            setAgentActions(prev => ([
                ...prev,
                {
                    id: Date.now() + 2,
                    text: `Handled by ${data?.agent_type || 'support'} agent`,
                    type: 'database',
                    icon: '🤖',
                    timestamp: new Date()
                },
                ...(data?.escalated ? [{
                    id: Date.now() + 3,
                    text: `Escalated to human support${data?.ticket_id ? ` (Ticket: ${data.ticket_id})` : ''}`,
                    type: 'success',
                    icon: '🎫',
                    timestamp: new Date()
                }] : [])
            ]));

            const botResponse = {
                id: Date.now() + 4,
                text: data?.response || 'I could not process that request right now.',
                sender: 'bot',
                timestamp: new Date()
            };

            setMessages(prev => [...prev, botResponse]);
            loadConversationHistory();
        } catch (error) {
            setAgentActions(prev => ([
                ...prev,
                {
                    id: Date.now() + 5,
                    text: 'Backend unavailable or request failed',
                    type: 'error',
                    icon: '⚠️',
                    timestamp: new Date()
                }
            ]));

            const errorMessage = error?.response?.data?.detail || error?.message || 'Unexpected error';
            setMessages(prev => ([
                ...prev,
                {
                    id: Date.now() + 6,
                    text: `Sorry, I couldn't reach support service. ${errorMessage}`,
                    sender: 'bot',
                    timestamp: new Date()
                }
            ]));
        }

        
        setIsProcessing(false);
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', backgroundColor: '#f5f7fa', fontFamily: 'Arial, sans-serif' }}>

            {/* ── Top Navigation Bar ── */}
            <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0 20px',
                height: '52px',
                backgroundColor: '#1e3a70',
                boxShadow: '0 2px 8px rgba(0,0,0,0.18)',
                flexShrink: 0,
                zIndex: 100,
            }}>
                {/* Brand / back home */}
                <Link
                    to="/"
                    style={{ display: 'flex', alignItems: 'center', gap: '10px', textDecoration: 'none', color: 'white' }}
                >
                    <span style={{ fontSize: '22px' }}>🤖</span>
                    <span style={{ fontWeight: 700, fontSize: '16px', letterSpacing: '0.01em' }}>AgenticAI Support</span>
                </Link>

                {/* Centre links */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Link to="/" style={{
                        display: 'flex', alignItems: 'center', gap: '6px',
                        padding: '6px 14px', borderRadius: '20px',
                        backgroundColor: 'rgba(255,255,255,0.12)',
                        color: 'white', textDecoration: 'none', fontSize: '13px', fontWeight: 600,
                        transition: 'background 0.15s',
                    }}>🏠 Home</Link>

                    {isAdmin && (
                        <>
                            <Link to="/admin" style={{
                                display: 'flex', alignItems: 'center', gap: '6px',
                                padding: '6px 14px', borderRadius: '20px',
                                backgroundColor: 'rgba(255,255,255,0.12)',
                                color: 'white', textDecoration: 'none', fontSize: '13px', fontWeight: 600,
                            }}>📊 Admin</Link>

                            <Link to="/customers" style={{
                                display: 'flex', alignItems: 'center', gap: '6px',
                                padding: '6px 14px', borderRadius: '20px',
                                backgroundColor: 'rgba(255,255,255,0.12)',
                                color: 'white', textDecoration: 'none', fontSize: '13px', fontWeight: 600,
                            }}>👥 Customers</Link>
                        </>
                    )}
                </div>

                {/* Right: user + sign out */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    {user && (
                        <span style={{ color: 'rgba(255,255,255,0.75)', fontSize: '13px' }}>
                            {user.name || user.email}
                        </span>
                    )}
                    <button
                        onClick={() => { signOut(); navigate('/'); }}
                        style={{
                            padding: '6px 16px', borderRadius: '20px', border: 'none',
                            backgroundColor: '#e53e3e', color: 'white',
                            fontSize: '13px', fontWeight: 600, cursor: 'pointer',
                        }}
                    >
                        Sign Out
                    </button>
                </div>
            </div>

            {/* ── Main content (sidebar + chat) ── */}
            <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
            {/* Sidebar - Agent Activity */}
            <div style={{
                width: '320px',
                backgroundColor: '#ffffff',
                borderRight: '1px solid #e0e0e0',
                display: 'flex',
                flexDirection: 'column',
                boxShadow: '2px 0 8px rgba(0,0,0,0.1)'
            }}>
                <div style={{
                    padding: '20px',
                    backgroundColor: '#2c5aa0',
                    color: 'white',
                    borderBottom: '3px solid #1e3a70'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{ fontSize: '32px' }}>⚡</div>
                        <div>
                            <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold' }}>Agent Activity</h2>
                            <p style={{ margin: '4px 0 0 0', fontSize: '13px', opacity: 0.9 }}>Real-time operations</p>
                        </div>
                    </div>
                </div>

                <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
                    {agentActions.length === 0 && (
                        <div style={{ textAlign: 'center', color: '#999', fontSize: '14px', marginTop: '60px' }}>
                            <div style={{ fontSize: '48px', marginBottom: '12px' }}>🤖</div>
                            <p style={{ margin: '8px 0' }}>Agent actions will appear here</p>
                            <p style={{ fontSize: '12px', margin: '4px 0' }}>Watching and learning...</p>
                        </div>
                    )}

                    {agentActions.map((action) => (
                        <div key={action.id} style={{ marginBottom: '12px' }}>
                            <div style={{
                                display: 'flex',
                                gap: '12px',
                                padding: '12px',
                                backgroundColor: action.type === 'success' ? '#e8f5e9' :
                                    action.type === 'action' ? '#e3f2fd' :
                                        action.type === 'database' ? '#f3e5f5' :
                                            action.type === 'error' ? '#ffebee' : '#f5f5f5',
                                border: `2px solid ${action.type === 'success' ? '#4caf50' :
                                    action.type === 'action' ? '#2196f3' :
                                        action.type === 'database' ? '#9c27b0' :
                                            action.type === 'error' ? '#f44336' : '#bdbdbd'}`,
                                borderRadius: '8px',
                                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                            }}>
                                <div style={{ fontSize: '24px' }}>{action.icon}</div>
                                <div style={{ flex: 1 }}>
                                    <p style={{ margin: '0 0 4px 0', fontSize: '13px', fontWeight: '600', color: '#333' }}>
                                        {action.text}
                                    </p>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <span style={{ fontSize: '11px', color: '#666' }}>
                                            {action.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                                        </span>
                                        <span style={{
                                            fontSize: '10px',
                                            padding: '2px 8px',
                                            borderRadius: '12px',
                                            backgroundColor: action.type === 'success' ? '#4caf50' :
                                                action.type === 'action' ? '#2196f3' :
                                                    action.type === 'database' ? '#9c27b0' :
                                                        action.type === 'error' ? '#f44336' : '#757575',
                                            color: 'white',
                                            fontWeight: '600'
                                        }}>
                                            {action.type.toUpperCase()}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}

                    <div style={{ marginTop: '18px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                            <h4 style={{ margin: 0, fontSize: '13px', color: '#334155' }}>Recent Conversations</h4>
                            <button
                                onClick={loadConversationHistory}
                                style={{ border: 'none', background: 'transparent', color: '#2c5aa0', fontSize: '12px', cursor: 'pointer' }}
                            >
                                Refresh
                            </button>
                        </div>

                        {historyLoading ? (
                            <p style={{ margin: 0, fontSize: '12px', color: '#64748b' }}>Loading history...</p>
                        ) : conversationHistory.length === 0 ? (
                            <p style={{ margin: 0, fontSize: '12px', color: '#94a3b8' }}>No previous conversations yet.</p>
                        ) : (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                {conversationHistory.map((conv) => (
                                    <button
                                        key={conv.conversation_id}
                                        onClick={() => openConversation(conv.conversation_id)}
                                        style={{
                                            textAlign: 'left',
                                            border: conv.conversation_id === conversationId ? '2px solid #2563eb' : '1px solid #e2e8f0',
                                            background: '#fff',
                                            borderRadius: '8px',
                                            padding: '8px',
                                            cursor: 'pointer'
                                        }}
                                    >
                                        <div style={{ fontSize: '11px', color: '#1e293b', fontWeight: 700 }}>{conv.conversation_id}</div>
                                        <div style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>{conv.preview || 'No preview'}</div>
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Customer Info */}
                <div style={{
                    borderTop: '1px solid #e0e0e0',
                    backgroundColor: '#f8f9fa',
                    padding: '16px'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                        <span style={{ fontSize: '24px' }}>👤</span>
                        <h3 style={{ margin: 0, fontSize: '14px', fontWeight: 'bold', color: '#333' }}>Customer Profile</h3>
                    </div>
                    <div style={{ fontSize: '13px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', margin: '8px 0' }}>
                            <span style={{ color: '#666' }}>Name:</span>
                            <span style={{ fontWeight: '600', color: '#333' }}>{customerData.name}</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', margin: '8px 0' }}>
                            <span style={{ color: '#666' }}>Customer ID:</span>
                            <span style={{ fontWeight: '600', color: '#2c5aa0' }}>{customerId}</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', margin: '8px 0' }}>
                            <span style={{ color: '#666' }}>Status:</span>
                            <span style={{
                                padding: '4px 12px',
                                backgroundColor: '#ffa000',
                                color: 'white',
                                fontSize: '11px',
                                fontWeight: 'bold',
                                borderRadius: '12px'
                            }}>
                                ⭐ {customerData.accountStatus}
                            </span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', margin: '8px 0' }}>
                            <span style={{ color: '#666' }}>Orders:</span>
                            <span style={{ fontWeight: '600', color: '#2c5aa0' }}>{customerData.recentOrders.length} Recent</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Chat Area */}
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                {/* Header */}
                <div style={{
                    backgroundColor: '#ffffff',
                    padding: '20px 32px',
                    borderBottom: '1px solid #e0e0e0',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                            <div style={{ position: 'relative' }}>
                                <div style={{
                                    width: '56px',
                                    height: '56px',
                                    backgroundColor: '#2c5aa0',
                                    borderRadius: '12px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    boxShadow: '0 4px 8px rgba(0,0,0,0.2)'
                                }}>
                                    <span style={{ fontSize: '32px' }}>🤖</span>
                                </div>
                                <div style={{
                                    position: 'absolute',
                                    bottom: '-4px',
                                    right: '-4px',
                                    width: '16px',
                                    height: '16px',
                                    backgroundColor: apiStatus === 'online' ? '#4caf50' : apiStatus === 'offline' ? '#f44336' : '#ff9800',
                                    borderRadius: '50%',
                                    border: '2px solid white'
                                }}></div>
                            </div>
                            <div>
                                <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 'bold', color: '#2c5aa0' }}>
                                    Agentic AI Support
                                </h1>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
                                    <span style={{
                                        padding: '2px 8px',
                                        backgroundColor: apiStatus === 'online' ? '#e8f5e9' : apiStatus === 'offline' ? '#ffebee' : '#fff8e1',
                                        color: apiStatus === 'online' ? '#2e7d32' : apiStatus === 'offline' ? '#c62828' : '#ef6c00',
                                        fontSize: '11px',
                                        fontWeight: '600',
                                        borderRadius: '12px'
                                    }}>● {apiStatus === 'online' ? 'Backend Online' : apiStatus === 'offline' ? 'Backend Offline' : 'Checking API'}</span>
                                    <span style={{ fontSize: '12px', color: '#666' }}>Customer: {customerId}{conversationId ? ` • ${conversationId}` : ''}</span>
                                </div>
                            </div>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <button
                                onClick={checkBackendHealth}
                                style={{
                                    border: '1px solid #d1d5db',
                                    backgroundColor: '#fff',
                                    color: '#334155',
                                    borderRadius: '20px',
                                    fontSize: '12px',
                                    padding: '6px 12px',
                                    cursor: 'pointer'
                                }}
                            >
                                Recheck API
                            </button>
                            <button
                                onClick={resetConversation}
                                style={{
                                    border: '1px solid #d1d5db',
                                    backgroundColor: '#fff',
                                    color: '#334155',
                                    borderRadius: '20px',
                                    fontSize: '12px',
                                    padding: '6px 12px',
                                    cursor: 'pointer'
                                }}
                            >
                                New Chat
                            </button>
                            {isProcessing && (
                            <div style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px',
                                padding: '8px 16px',
                                backgroundColor: '#e3f2fd',
                                borderRadius: '20px',
                                border: '1px solid #2196f3'
                            }}>
                                <div style={{
                                    width: '8px',
                                    height: '8px',
                                    backgroundColor: '#2196f3',
                                    borderRadius: '50%',
                                    animation: 'pulse 1.5s infinite'
                                }}></div>
                                <span style={{ color: '#1565c0', fontSize: '13px', fontWeight: '600' }}>Agent working...</span>
                            </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Messages */}
                <div style={{ flex: 1, overflowY: 'auto', padding: '24px 32px' }}>
                    {messages.map((message) => (
                        <div
                            key={message.id}
                            style={{
                                display: 'flex',
                                gap: '12px',
                                marginBottom: '24px',
                                flexDirection: message.sender === 'user' ? 'row-reverse' : 'row'
                            }}
                        >
                            <div style={{
                                width: '40px',
                                height: '40px',
                                borderRadius: '12px',
                                backgroundColor: message.sender === 'bot' ? '#2c5aa0' : '#424242',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                flexShrink: 0,
                                boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                            }}>
                                <span style={{ fontSize: '20px' }}>
                                    {message.sender === 'bot' ? '🤖' : '👨‍💼'}
                                </span>
                            </div>
                            <div style={{ maxWidth: '600px' }}>
                                <div style={{
                                    padding: '16px 20px',
                                    borderRadius: '16px',
                                    backgroundColor: message.sender === 'bot' ? '#ffffff' : '#2c5aa0',
                                    color: message.sender === 'bot' ? '#333' : '#ffffff',
                                    border: message.sender === 'bot' ? '1px solid #e0e0e0' : 'none',
                                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                                }}>
                                    <p style={{
                                        margin: 0,
                                        fontSize: '14px',
                                        lineHeight: '1.6',
                                        whiteSpace: 'pre-line'
                                    }}>{message.text}</p>
                                </div>
                                <div style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '8px',
                                    marginTop: '6px',
                                    paddingLeft: '8px',
                                    fontSize: '11px',
                                    color: '#666'
                                }}>
                                    <span>
                                        {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </span>
                                    {message.sender === 'bot' && (
                                        <>
                                            <span style={{ color: '#4caf50', fontWeight: '600' }}>✓ Delivered</span>
                                            <button
                                                onClick={() => copyMessageText(message.id, message.text)}
                                                style={{
                                                    border: 'none',
                                                    background: 'transparent',
                                                    cursor: 'pointer',
                                                    color: '#2c5aa0',
                                                    fontWeight: '600',
                                                    fontSize: '11px'
                                                }}
                                            >
                                                {copiedMessageId === message.id ? 'Copied' : 'Copy'}
                                            </button>
                                        </>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                    {isProcessing && (
                        <div style={{ marginLeft: '52px', marginBottom: '20px' }}>
                            <TypingIndicator />
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div style={{
                    backgroundColor: '#ffffff',
                    borderTop: '1px solid #e0e0e0',
                    padding: '20px 32px'
                }}>
                    <div style={{ display: 'flex', gap: '12px', marginBottom: '12px' }}>
                        <textarea
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyPress={handleKeyPress}
                            maxLength={5000}
                            placeholder="✨ Describe your issue... (e.g., 'I need a refund', 'Where is my order?')"
                            disabled={isProcessing}
                            style={{
                                flex: 1,
                                padding: '14px 20px',
                                border: '2px solid #e0e0e0',
                                borderRadius: '24px',
                                fontSize: '14px',
                                outline: 'none',
                                minHeight: '52px',
                                maxHeight: '120px',
                                resize: 'vertical',
                                backgroundColor: isProcessing ? '#f5f5f5' : 'white'
                            }}
                            onFocus={(e) => e.target.style.borderColor = '#2c5aa0'}
                            onBlur={(e) => e.target.style.borderColor = '#e0e0e0'}
                        />
                        <button
                            onClick={handleSend}
                            disabled={input.trim() === '' || isProcessing}
                            style={{
                                padding: '14px 32px',
                                backgroundColor: isProcessing || input.trim() === '' ? '#ccc' : '#2c5aa0',
                                color: 'white',
                                border: 'none',
                                borderRadius: '24px',
                                fontSize: '14px',
                                fontWeight: '600',
                                cursor: isProcessing || input.trim() === '' ? 'not-allowed' : 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px',
                                boxShadow: '0 2px 6px rgba(0,0,0,0.2)'
                            }}
                        >
                            {isProcessing ? (
                                <>
                                    <span style={{ fontSize: '16px' }}>⚙️</span>
                                    <span>Processing</span>
                                </>
                            ) : (
                                <>
                                    <span style={{ fontSize: '16px' }}>🚀</span>
                                    <span>Send</span>
                                </>
                            )}
                        </button>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                        <span style={{ fontSize: '12px', color: '#64748b' }}>
                            Press Enter to send · Shift+Enter for a new line
                        </span>
                        <span style={{ fontSize: '12px', color: '#64748b' }}>
                            {input.length}/5000
                        </span>
                    </div>
                    <ChatQuickActions
                        disabled={isProcessing}
                        onFill={(text) => setInput(text)}
                        onSend={(text) => handleSend(text)}
                    />
                </div>
            </div>
            </div>{/* end main content flex row */}
        </div>
    );
}