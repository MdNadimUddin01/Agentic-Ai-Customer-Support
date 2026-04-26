import { useEffect, useState, useCallback } from 'react';
import {
    getSystemStats,
    getTestDataOverview,
    getAdminTickets,
    updateTicketStatus,
} from '../../services/supportApi';

const PRIORITY_COLORS = {
    urgent: 'bg-red-100 text-red-700 border-red-200',
    high: 'bg-orange-100 text-orange-700 border-orange-200',
    medium: 'bg-yellow-100 text-yellow-700 border-yellow-200',
    low: 'bg-blue-100 text-blue-700 border-blue-200',
};

const STATUS_COLORS = {
    open: 'bg-rose-50 text-rose-700',
    assigned: 'bg-indigo-50 text-indigo-700',
    in_progress: 'bg-amber-50 text-amber-700',
    waiting_customer: 'bg-purple-50 text-purple-700',
    resolved: 'bg-green-50 text-green-700',
    closed: 'bg-slate-100 text-slate-500',
};

const STATUS_OPTIONS = ['open', 'assigned', 'in_progress', 'waiting_customer', 'resolved', 'closed'];
const PRIORITY_OPTIONS = ['', 'urgent', 'high', 'medium', 'low'];

function Badge({ label, colorClass }) {
    return (
        <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${colorClass}`}>
            {label}
        </span>
    );
}

function StatCard({ label, value, tone }) {
    return (
        <div className="rounded-2xl bg-white p-5 shadow">
            <p className="text-sm text-slate-500">{label}</p>
            <p className={`mt-2 bg-gradient-to-r ${tone} bg-clip-text text-3xl font-bold text-transparent`}>
                {value}
            </p>
        </div>
    );
}

export function AdminDashboard() {
    const [stats, setStats] = useState(null);
    const [testData, setTestData] = useState(null);
    const [tickets, setTickets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [ticketsLoading, setTicketsLoading] = useState(false);
    const [error, setError] = useState('');
    const [activeTab, setActiveTab] = useState('overview');

    const [filterStatus, setFilterStatus] = useState('');
    const [filterPriority, setFilterPriority] = useState('');
    const [updatingTicket, setUpdatingTicket] = useState(null);

    const loadOverview = useCallback(async () => {
        try {
            setLoading(true);
            const [statsData, testDataInfo] = await Promise.all([
                getSystemStats(),
                getTestDataOverview(),
            ]);
            setStats(statsData);
            setTestData(testDataInfo);
            setError('');
        } catch (err) {
            setError(err?.response?.data?.detail || err.message || 'Failed to load stats');
        } finally {
            setLoading(false);
        }
    }, []);

    const loadTickets = useCallback(async () => {
        try {
            setTicketsLoading(true);
            const data = await getAdminTickets({
                status_filter: filterStatus || undefined,
                priority: filterPriority || undefined,
                limit: 50,
            });
            setTickets(Array.isArray(data) ? data : []);
        } catch (err) {
            setError(err?.response?.data?.detail || err.message || 'Failed to load tickets');
        } finally {
            setTicketsLoading(false);
        }
    }, [filterStatus, filterPriority]);

    useEffect(() => { loadOverview(); }, [loadOverview]);
    useEffect(() => { if (activeTab === 'tickets') loadTickets(); }, [activeTab, loadTickets]);

    const handleStatusChange = async (ticketId, newStatus) => {
        setUpdatingTicket(ticketId);
        try {
            await updateTicketStatus(ticketId, newStatus);
            setTickets(prev =>
                prev.map(t => t.ticket_id === ticketId ? { ...t, status: newStatus } : t)
            );
        } catch (err) {
            alert(`Failed to update: ${err?.response?.data?.detail || err.message}`);
        } finally {
            setUpdatingTicket(null);
        }
    };

    const overviewCards = [
        { label: 'Total Conversations', value: stats?.conversations?.total ?? '-', tone: 'from-blue-500 to-cyan-500' },
        { label: 'Active Conversations', value: stats?.conversations?.active ?? '-', tone: 'from-indigo-500 to-violet-500' },
        { label: 'Escalated', value: stats?.conversations?.escalated ?? '-', tone: 'from-orange-500 to-red-500' },
        { label: 'Open Tickets', value: stats?.tickets?.open ?? '-', tone: 'from-emerald-500 to-green-600' },
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 px-4 py-28 sm:px-6 lg:px-10">
            <div className="mx-auto max-w-7xl">

                <div className="mb-6 flex items-center justify-between gap-4">
                    <div>
                        <h1 className="text-3xl font-bold text-slate-900">Admin Dashboard</h1>
                        <p className="mt-1 text-sm text-slate-500">Live system metrics · Tickets · Order Tracking API</p>
                    </div>
                    <button
                        onClick={() => { loadOverview(); if (activeTab === 'tickets') loadTickets(); }}
                        className="rounded-full bg-white px-5 py-2 text-sm font-semibold text-slate-700 shadow hover:bg-slate-100"
                    >
                        ↻ Refresh
                    </button>
                </div>

                {/* Tabs */}
                <div className="mb-6 flex gap-2 rounded-2xl bg-white p-1 shadow w-fit">
                    {['overview', 'tickets', 'orders'].map(tab => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            className={`rounded-xl px-5 py-2 text-sm font-semibold transition-all ${
                                activeTab === tab
                                    ? 'bg-blue-600 text-white shadow'
                                    : 'text-slate-600 hover:bg-slate-100'
                            }`}
                        >
                            {tab.charAt(0).toUpperCase() + tab.slice(1)}
                        </button>
                    ))}
                </div>

                {loading && (
                    <div className="rounded-2xl bg-white p-8 text-center shadow text-slate-500">Loading…</div>
                )}
                {!loading && error && (
                    <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-700 shadow">{error}</div>
                )}

                {/* Overview Tab */}
                {!loading && !error && activeTab === 'overview' && (
                    <>
                        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                            {overviewCards.map(c => <StatCard key={c.label} {...c} />)}
                        </div>
                        <div className="mt-6 grid gap-4 sm:grid-cols-2">
                            <div className="rounded-2xl bg-white p-6 shadow">
                                <h2 className="text-lg font-semibold text-slate-900">Ticket Metrics</h2>
                                <ul className="mt-4 space-y-2 text-sm text-slate-700">
                                    <li>Total: <strong>{stats?.tickets?.total ?? '-'}</strong></li>
                                    <li>Open: <strong>{stats?.tickets?.open ?? '-'}</strong></li>
                                    <li>Resolved: <strong>{stats?.tickets?.resolved ?? '-'}</strong></li>
                                </ul>
                            </div>
                            <div className="rounded-2xl bg-white p-6 shadow">
                                <h2 className="text-lg font-semibold text-slate-900">Service Metrics</h2>
                                <ul className="mt-4 space-y-2 text-sm text-slate-700">
                                    <li>Escalation Rate: <strong>{stats?.metrics?.escalation_rate ?? 0}%</strong></li>
                                    <li>Resolution Rate: <strong>{stats?.metrics?.resolution_rate ?? 0}%</strong></li>
                                    <li>Updated: <strong>{stats?.timestamp ? new Date(stats.timestamp).toLocaleString() : '-'}</strong></li>
                                </ul>
                            </div>
                        </div>
                        <div className="mt-6 rounded-2xl bg-white p-6 shadow">
                            <h2 className="mb-4 text-lg font-semibold text-slate-900">Seeded Data</h2>
                            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
                                {[
                                    ['Customers', testData?.counts?.customers],
                                    ['Subscriptions', testData?.counts?.subscriptions],
                                    ['Orders', testData?.counts?.orders],
                                    ['Conversations', testData?.counts?.conversations],
                                    ['Knowledge Docs', testData?.counts?.knowledge_entries],
                                ].map(([label, val]) => (
                                    <div key={label} className="rounded-xl bg-slate-50 p-3 text-sm">
                                        {label}: <strong>{val ?? '-'}</strong>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </>
                )}

                {/* Tickets Tab */}
                {activeTab === 'tickets' && (
                    <div className="rounded-2xl bg-white p-6 shadow">
                        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
                            <h2 className="text-lg font-semibold text-slate-900">Support Tickets</h2>
                            <div className="flex gap-2">
                                <select
                                    value={filterStatus}
                                    onChange={e => setFilterStatus(e.target.value)}
                                    className="rounded-lg border border-slate-200 px-3 py-1.5 text-sm text-slate-700 focus:outline-none"
                                >
                                    <option value="">All statuses</option>
                                    {STATUS_OPTIONS.map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
                                </select>
                                <select
                                    value={filterPriority}
                                    onChange={e => setFilterPriority(e.target.value)}
                                    className="rounded-lg border border-slate-200 px-3 py-1.5 text-sm text-slate-700 focus:outline-none"
                                >
                                    {PRIORITY_OPTIONS.map(p => <option key={p} value={p}>{p || 'All priorities'}</option>)}
                                </select>
                                <button
                                    onClick={loadTickets}
                                    className="rounded-lg bg-blue-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
                                >
                                    Apply
                                </button>
                            </div>
                        </div>

                        {ticketsLoading ? (
                            <p className="text-center text-slate-400 py-8">Loading tickets…</p>
                        ) : tickets.length === 0 ? (
                            <p className="text-center text-slate-400 py-8">No tickets found.</p>
                        ) : (
                            <div className="overflow-x-auto">
                                <table className="w-full text-left text-sm">
                                    <thead className="bg-slate-50 text-xs text-slate-500 uppercase">
                                        <tr>
                                            {['Ticket ID', 'Customer', 'Priority', 'Intent', 'Confidence', 'Reason', 'Status', 'Created', 'Action'].map(h => (
                                                <th key={h} className="px-4 py-3 whitespace-nowrap">{h}</th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-100">
                                        {tickets.map(ticket => (
                                            <tr key={ticket.ticket_id} className="hover:bg-slate-50 transition-colors">
                                                <td className="px-4 py-3 font-mono text-xs text-slate-700">{ticket.ticket_id}</td>
                                                <td className="px-4 py-3 text-slate-600 text-xs">{ticket.customer_id}</td>
                                                <td className="px-4 py-3">
                                                    <Badge
                                                        label={(ticket.priority || '').toUpperCase()}
                                                        colorClass={PRIORITY_COLORS[ticket.priority] || 'bg-slate-100 text-slate-600 border-slate-200'}
                                                    />
                                                </td>
                                                <td className="px-4 py-3 text-slate-500 text-xs whitespace-nowrap">
                                                    {ticket.source_intent || '—'}
                                                </td>
                                                <td className="px-4 py-3">
                                                    {ticket.confidence_score != null ? (
                                                        <span className={`font-semibold text-sm ${ticket.confidence_score < 0.6 ? 'text-red-600' : 'text-green-600'}`}>
                                                            {(ticket.confidence_score * 100).toFixed(0)}%
                                                        </span>
                                                    ) : '—'}
                                                </td>
                                                <td className="px-4 py-3 text-slate-400 text-xs whitespace-nowrap">
                                                    {ticket.escalation_reason?.replace(/_/g, ' ') || '—'}
                                                </td>
                                                <td className="px-4 py-3">
                                                    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_COLORS[ticket.status] || 'bg-slate-100'}`}>
                                                        {(ticket.status || '').replace('_', ' ')}
                                                    </span>
                                                </td>
                                                <td className="px-4 py-3 text-xs text-slate-400 whitespace-nowrap">
                                                    {ticket.created_at ? new Date(ticket.created_at).toLocaleDateString() : '—'}
                                                </td>
                                                <td className="px-4 py-3">
                                                    <select
                                                        disabled={updatingTicket === ticket.ticket_id}
                                                        value={ticket.status}
                                                        onChange={e => handleStatusChange(ticket.ticket_id, e.target.value)}
                                                        className="rounded border border-slate-200 px-2 py-1 text-xs text-slate-700 disabled:opacity-40"
                                                    >
                                                        {STATUS_OPTIONS.map(s => (
                                                            <option key={s} value={s}>{s.replace('_', ' ')}</option>
                                                        ))}
                                                    </select>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                )}

                {/* Orders Tab — Week 7 External API demo */}
                {activeTab === 'orders' && (
                    <div className="rounded-2xl bg-white p-6 shadow">
                        <h2 className="text-lg font-semibold text-slate-900 mb-1">Order Tracking — External API Demo</h2>
                        <p className="text-sm text-slate-500 mb-6">
                            when the user asks <em>"Where is my order?"</em> the intent classifier returns{' '}
                            <code className="rounded bg-slate-100 px-1">order_status</code>, routing to{' '}
                            <strong>OrderTrackingTool</strong> which queries MongoDB then calls a mock courier API.
                        </p>

                        <div className="grid gap-4 sm:grid-cols-2">
                            <div className="rounded-xl border border-blue-100 bg-blue-50 p-5">
                                <h3 className="mb-3 font-semibold text-blue-800">Autonomous Flow</h3>
                                <ol className="space-y-2 text-sm text-blue-700 list-decimal list-inside">
                                    <li>User: <em>"Where is my order?"</em></li>
                                    <li>Intent classifier → <code className="rounded bg-blue-100 px-1">order_status</code></li>
                                    <li>Router → <code className="rounded bg-blue-100 px-1">AgentType.ORDER</code></li>
                                    <li><code className="rounded bg-blue-100 px-1">OrderTrackingTool.execute()</code></li>
                                    <li>MongoDB lookup → order + tracking number</li>
                                    <li>Mock courier API called with tracking number</li>
                                    <li>Returns status, ETA, and events to user</li>
                                </ol>
                            </div>
                            <div className="rounded-xl border border-slate-200 bg-slate-50 p-5">
                                <h3 className="mb-3 font-semibold text-slate-700">Sample Bot Response</h3>
                                <pre className="whitespace-pre-wrap text-xs text-slate-600 leading-relaxed">{`Order ORD-12345 — Status: SHIPPED
  Tracking: TRK9876543210 via MockCourier
  Latest: In transit @ Regional Hub
  ETA: 2026-04-19
  Items: Wireless Headphones, USB-C Cable
    Total: ₹149.98

Is there anything else I can help with?`}</pre>
                            </div>
                        </div>

                        <div className="mt-6">
                            <h3 className="mb-3 font-semibold text-slate-800 text-sm">Seeded Orders (MongoDB)</h3>
                            <div className="overflow-x-auto rounded-xl border border-slate-200">
                                <table className="w-full text-left text-xs">
                                    <thead className="bg-slate-50 text-slate-500 uppercase">
                                        <tr>
                                            {['Order ID', 'Customer', 'Status', 'Payment', 'Total'].map(h => (
                                                <th key={h} className="px-4 py-2">{h}</th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-100">
                                        {!(testData?.sample_orders?.length) ? (
                                            <tr>
                                                <td colSpan={5} className="px-4 py-6 text-center text-slate-400">
                                                    No orders seeded — run <code>scripts/seed_data.py</code>
                                                </td>
                                            </tr>
                                        ) : testData.sample_orders.map(order => (
                                            <tr key={order.order_id} className="hover:bg-slate-50">
                                                <td className="px-4 py-2 font-mono">{order.order_id}</td>
                                                <td className="px-4 py-2 text-slate-500">{order.customer_id}</td>
                                                <td className="px-4 py-2">
                                                    <Badge label={order.status} colorClass="bg-slate-100 text-slate-600 border-slate-200" />
                                                </td>
                                                <td className="px-4 py-2 text-slate-500">{order.payment_status}</td>
                                                <td className="px-4 py-2 font-semibold">₹{order.total}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
