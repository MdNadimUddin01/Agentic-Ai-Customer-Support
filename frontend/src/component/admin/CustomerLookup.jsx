/**
 * CustomerLookup.jsx
 *
 * Admin page to verify chatbot responses against the actual ground-truth data
 * stored in MongoDB. Select any customer to see their profile, subscription,
 * full order history, tickets, and conversation previews — with billing totals
 * so you can instantly confirm or refute bot claims like:
 *   "You have made 3 payments totalling ₹87.00"
 */
import { useEffect, useState, useCallback } from 'react';
import { getAdminCustomers, getAdminCustomerProfile } from '../../services/supportApi';

const fmt = (v, fallback = '—') => (v !== null && v !== undefined ? v : fallback);

function Badge({ label, color }) {
    const colors = {
        green: 'bg-green-100 text-green-700 border-green-200',
        red: 'bg-red-100 text-red-700 border-red-200',
        yellow: 'bg-yellow-100 text-yellow-700 border-yellow-200',
        blue: 'bg-blue-100 text-blue-700 border-blue-200',
        indigo: 'bg-indigo-100 text-indigo-700 border-indigo-200',
        slate: 'bg-slate-100 text-slate-600 border-slate-200',
        orange: 'bg-orange-100 text-orange-700 border-orange-200',
        purple: 'bg-purple-100 text-purple-700 border-purple-200',
    };
    return (
        <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${colors[color] || colors.slate}`}>
            {label}
        </span>
    );
}

function Section({ title, children }) {
    return (
        <div className="rounded-2xl bg-white p-5 shadow-sm border border-slate-100">
            <h3 className="mb-4 text-sm font-bold uppercase tracking-wider text-slate-500">{title}</h3>
            {children}
        </div>
    );
}

function KV({ label, value, mono }) {
    return (
        <div className="flex items-start justify-between gap-4 py-1.5 border-b border-slate-50 last:border-0">
            <span className="text-xs text-slate-500 shrink-0">{label}</span>
            <span className={`text-xs font-semibold text-slate-800 text-right ${mono ? 'font-mono' : ''}`}>{fmt(value)}</span>
        </div>
    );
}

const ORDER_STATUS_COLOR = {
    delivered: 'green', shipped: 'blue', processing: 'yellow',
    cancelled: 'red', refunded: 'orange', pending: 'slate',
};
const TICKET_STATUS_COLOR = {
    open: 'red', in_progress: 'yellow', waiting_customer: 'purple',
    assigned: 'indigo', resolved: 'green', closed: 'slate',
};
const PLAN_COLOR = {
    enterprise: 'indigo', pro: 'blue', basic: 'green', free: 'slate',
};

/* ─── sub-panels ──────────────────────────────────────────────────────────── */

function SummaryPanel({ summary, subscription }) {
    const plan = subscription?.plan || 'free';
    return (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {[
                { label: 'Total Orders', value: summary.total_orders, tone: 'from-blue-500 to-cyan-400' },
                { label: 'Completed Payments', value: summary.completed_orders, tone: 'from-emerald-500 to-green-400' },
                { label: 'Total Spend (INR)', value: `₹${summary.total_spend.toFixed(2)}`, tone: 'from-violet-500 to-purple-400' },
                { label: 'Monthly Plan Price', value: `₹${(summary.monthly_price || 0).toFixed(2)}`, tone: 'from-orange-500 to-amber-400' },
            ].map(c => (
                <div key={c.label} className="rounded-2xl bg-white p-5 shadow-sm border border-slate-100">
                    <p className="text-xs text-slate-500">{c.label}</p>
                    <p className={`mt-1 bg-gradient-to-r ${c.tone} bg-clip-text text-2xl font-bold text-transparent`}>{c.value}</p>
                </div>
            ))}
        </div>
    );
}

function ProfilePanel({ customer, subscription }) {
    return (
        <div className="grid gap-4 md:grid-cols-2">
            <Section title="Account Info">
                <KV label="Customer ID" value={customer.customer_id} mono />
                <KV label="Name" value={customer.name} />
                <KV label="Email" value={customer.email} />
                <KV label="Phone" value={customer.phone} />
                <KV label="Industry" value={customer.industry} />
                <KV label="Joined" value={customer.created_at ? new Date(customer.created_at).toLocaleDateString() : '—'} />
            </Section>

            <Section title="Subscription">
                {subscription ? (
                    <>
                        <div className="mb-3 flex items-center gap-2">
                            <Badge label={(subscription.plan || 'free').toUpperCase()} color={PLAN_COLOR[subscription.plan] || 'slate'} />
                            <Badge label={subscription.status} color={subscription.status === 'active' ? 'green' : 'red'} />
                        </div>
                        <KV label="Monthly Price" value={`₹${(subscription.monthly_price || 0).toFixed(2)}`} />
                        <KV label="Users" value={subscription.features?.users === -1 ? 'Unlimited' : subscription.features?.users} />
                        <KV label="API Calls / mo" value={subscription.features?.api_calls?.toLocaleString()} />
                        <KV label="API Calls Used" value={subscription.usage?.api_calls_used?.toLocaleString()} />
                        <KV label="Storage" value={subscription.features?.storage_gb ? `${subscription.features.storage_gb} GB` : '—'} />
                        <KV label="Renewal" value={subscription.renewal_date ? new Date(subscription.renewal_date).toLocaleDateString() : '—'} />
                    </>
                ) : (
                    <p className="text-sm text-slate-400">No subscription found.</p>
                )}
            </Section>
        </div>
    );
}

function OrdersPanel({ orders, summary }) {
    const totalAll = orders.reduce((s, o) => s + (o.total || 0), 0);
    const totalCompleted = orders.filter(o => o.payment_status === 'completed').reduce((s, o) => s + (o.total || 0), 0);

    return (
        <Section title={`Orders — ${orders.length} total`}>
            {/* Quick-confirm billing summary — answers "total purchased by me" */}
            <div className="mb-4 rounded-xl bg-blue-50 border border-blue-100 p-4 text-sm text-blue-800">
                <span className="font-semibold">Billing Ground Truth: </span>
                <strong>{orders.length}</strong> order(s) placed &nbsp;·&nbsp;
                <strong>{summary.completed_orders}</strong> payment(s) completed &nbsp;·&nbsp;
                Total paid: <strong>₹{totalCompleted.toFixed(2)}</strong> &nbsp;·&nbsp;
                All-time order value: <strong>₹{totalAll.toFixed(2)}</strong>
            </div>

            {orders.length === 0 ? (
                <p className="text-sm text-slate-400">No orders found.</p>
            ) : (
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs">
                        <thead className="bg-slate-50 text-slate-500 uppercase">
                            <tr>
                                {['Order ID', 'Items', 'Subtotal', 'Tax', 'Total', 'Status', 'Payment', 'Placed'].map(h => (
                                    <th key={h} className="px-3 py-2 whitespace-nowrap">{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-50">
                            {orders.map(o => (
                                <tr key={o.order_id} className="hover:bg-slate-50">
                                    <td className="px-3 py-2 font-mono text-slate-700">{o.order_id}</td>
                                    <td className="px-3 py-2 text-slate-500 max-w-[160px]">
                                        {(o.items || []).map(i => i.name).join(', ') || '—'}
                                    </td>
                                    <td className="px-3 py-2">₹{(o.subtotal || 0).toFixed(2)}</td>
                                    <td className="px-3 py-2 text-slate-400">₹{(o.tax || 0).toFixed(2)}</td>
                                    <td className="px-3 py-2 font-semibold">₹{(o.total || 0).toFixed(2)}</td>
                                    <td className="px-3 py-2">
                                        <Badge label={o.status} color={ORDER_STATUS_COLOR[o.status] || 'slate'} />
                                    </td>
                                    <td className="px-3 py-2">
                                        <Badge label={o.payment_status} color={o.payment_status === 'completed' ? 'green' : o.payment_status === 'refunded' ? 'orange' : 'yellow'} />
                                    </td>
                                    <td className="px-3 py-2 whitespace-nowrap text-slate-400">
                                        {o.created_at ? new Date(o.created_at).toLocaleDateString() : '—'}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                        <tfoot>
                            <tr className="bg-slate-50 font-semibold text-xs text-slate-700">
                                <td colSpan={4} className="px-3 py-2 text-right">Grand Total</td>
                                <td className="px-3 py-2">₹{totalAll.toFixed(2)}</td>
                                <td colSpan={3} />
                            </tr>
                        </tfoot>
                    </table>
                </div>
            )}
        </Section>
    );
}

function TicketsPanel({ tickets }) {
    return (
        <Section title={`Support Tickets — ${tickets.length} total`}>
            {tickets.length === 0 ? (
                <p className="text-sm text-slate-400">No tickets found.</p>
            ) : (
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs">
                        <thead className="bg-slate-50 text-slate-500 uppercase">
                            <tr>
                                {['Ticket ID', 'Title', 'Priority', 'Category', 'Status', 'AI Confidence', 'Created'].map(h => (
                                    <th key={h} className="px-3 py-2 whitespace-nowrap">{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-50">
                            {tickets.map(t => {
                                const meta = t.metadata || {};
                                const conf = meta.confidence_score;
                                return (
                                    <tr key={t.ticket_id} className="hover:bg-slate-50">
                                        <td className="px-3 py-2 font-mono text-slate-700">{t.ticket_id}</td>
                                        <td className="px-3 py-2 max-w-[200px] text-slate-600">{t.title}</td>
                                        <td className="px-3 py-2">
                                            <Badge label={t.priority} color={{ urgent: 'red', high: 'orange', medium: 'yellow', low: 'blue' }[t.priority] || 'slate'} />
                                        </td>
                                        <td className="px-3 py-2 text-slate-500">{t.category}</td>
                                        <td className="px-3 py-2">
                                            <Badge label={(t.status || '').replace('_', ' ')} color={TICKET_STATUS_COLOR[t.status] || 'slate'} />
                                        </td>
                                        <td className="px-3 py-2">
                                            {conf != null ? (
                                                <span className={`font-semibold ${conf < 0.6 ? 'text-red-600' : 'text-green-600'}`}>
                                                    {(conf * 100).toFixed(0)}%
                                                </span>
                                            ) : '—'}
                                        </td>
                                        <td className="px-3 py-2 whitespace-nowrap text-slate-400">
                                            {t.created_at ? new Date(t.created_at).toLocaleDateString() : '—'}
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            )}
        </Section>
    );
}

function ConversationsPanel({ conversations }) {
    const [expanded, setExpanded] = useState(null);
    return (
        <Section title={`Conversations — ${conversations.length} total`}>
            {conversations.length === 0 ? (
                <p className="text-sm text-slate-400">No conversations found.</p>
            ) : (
                <div className="space-y-2">
                    {conversations.map(conv => (
                        <div key={conv.conversation_id} className="rounded-xl border border-slate-100 bg-slate-50">
                            <button
                                onClick={() => setExpanded(expanded === conv.conversation_id ? null : conv.conversation_id)}
                                className="w-full flex items-center justify-between gap-4 px-4 py-3 text-left text-xs"
                            >
                                <div className="flex items-center gap-3 min-w-0">
                                    <span className="font-mono text-slate-500 shrink-0">{conv.conversation_id}</span>
                                    <Badge label={conv.status} color={{ active: 'blue', resolved: 'green', escalated: 'red', closed: 'slate' }[conv.status] || 'slate'} />
                                    <Badge label={conv.channel} color="slate" />
                                    <span className="text-slate-400 shrink-0">{conv.message_count} msg{conv.message_count !== 1 ? 's' : ''}</span>
                                </div>
                                <div className="flex items-center gap-3 shrink-0 text-slate-400">
                                    <span>{conv.created_at ? new Date(conv.created_at).toLocaleDateString() : '—'}</span>
                                    <span>{expanded === conv.conversation_id ? '▲' : '▼'}</span>
                                </div>
                            </button>

                            {expanded === conv.conversation_id && (
                                <div className="border-t border-slate-100 px-4 py-3 space-y-3">
                                    {conv.last_user_message && (
                                        <div>
                                            <p className="text-[10px] font-semibold uppercase text-slate-400 mb-1">Last User Message</p>
                                            <p className="rounded-lg bg-white border border-slate-100 px-3 py-2 text-xs text-slate-700">
                                                {conv.last_user_message}
                                            </p>
                                        </div>
                                    )}
                                    {conv.last_bot_message && (
                                        <div>
                                            <p className="text-[10px] font-semibold uppercase text-slate-400 mb-1">Last Bot Response</p>
                                            <p className="rounded-lg bg-blue-50 border border-blue-100 px-3 py-2 text-xs text-blue-800 leading-relaxed">
                                                {conv.last_bot_message}
                                            </p>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </Section>
    );
}

/* ─── main component ──────────────────────────────────────────────────────── */

export function CustomerLookup() {
    const [customers, setCustomers] = useState([]);
    const [search, setSearch] = useState('');
    const [selectedId, setSelectedId] = useState(null);
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [listLoading, setListLoading] = useState(true);
    const [error, setError] = useState('');
    const [activeTab, setActiveTab] = useState('orders');

    // Load customer list
    useEffect(() => {
        setListLoading(true);
        getAdminCustomers()
            .then(setCustomers)
            .catch(e => setError(e?.response?.data?.detail || e.message))
            .finally(() => setListLoading(false));
    }, []);

    // Load profile whenever a customer is selected
    const loadProfile = useCallback(async (id) => {
        if (!id) return;
        setLoading(true);
        setProfile(null);
        setError('');
        try {
            const data = await getAdminCustomerProfile(id);
            setProfile(data);
            setActiveTab('orders');
        } catch (e) {
            setError(e?.response?.data?.detail || e.message || 'Failed to load profile');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { loadProfile(selectedId); }, [selectedId, loadProfile]);

    const filtered = customers.filter(c =>
        !search ||
        c.name?.toLowerCase().includes(search.toLowerCase()) ||
        c.email?.toLowerCase().includes(search.toLowerCase()) ||
        c.customer_id?.toLowerCase().includes(search.toLowerCase())
    );

    const tabs = ['orders', 'tickets', 'conversations', 'profile'];

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 px-4 py-28 sm:px-6 lg:px-10">
            <div className="mx-auto max-w-7xl">

                {/* Header */}
                <div className="mb-6">
                    <h1 className="text-3xl font-bold text-slate-900">Customer Lookup</h1>
                    <p className="mt-1 text-sm text-slate-500">
                        Select a customer to verify the chatbot's responses against their actual data in MongoDB.
                    </p>
                </div>

                <div className="grid gap-6 lg:grid-cols-[320px_1fr]">

                    {/* ── Left Sidebar: customer list ── */}
                    <div className="flex flex-col gap-3">
                        <input
                            type="search"
                            placeholder="Search by name, email or ID…"
                            value={search}
                            onChange={e => setSearch(e.target.value)}
                            className="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
                        />

                        <div className="rounded-2xl bg-white shadow-sm border border-slate-100 overflow-hidden">
                            {listLoading ? (
                                <p className="p-4 text-sm text-slate-400">Loading customers…</p>
                            ) : filtered.length === 0 ? (
                                <p className="p-4 text-sm text-slate-400">No customers found.</p>
                            ) : (
                                <ul className="divide-y divide-slate-50 max-h-[calc(100vh-240px)] overflow-y-auto">
                                    {filtered.map(c => {
                                        const plan = c.subscription?.plan || 'free';
                                        const isSelected = selectedId === c.customer_id;
                                        return (
                                            <li key={c.customer_id}>
                                                <button
                                                    onClick={() => setSelectedId(c.customer_id)}
                                                    className={`w-full text-left px-4 py-3 transition-colors ${isSelected ? 'bg-blue-50 border-l-4 border-blue-500' : 'hover:bg-slate-50 border-l-4 border-transparent'}`}
                                                >
                                                    <div className="flex items-center justify-between gap-2">
                                                        <div className="min-w-0">
                                                            <p className="text-sm font-semibold text-slate-800 truncate">{c.name}</p>
                                                            <p className="text-xs text-slate-400 truncate">{c.email}</p>
                                                            <p className="text-[10px] font-mono text-slate-300">{c.customer_id}</p>
                                                        </div>
                                                        <span className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase ${
                                                            plan === 'enterprise' ? 'bg-indigo-100 text-indigo-600' :
                                                            plan === 'pro' ? 'bg-blue-100 text-blue-600' :
                                                            plan === 'basic' ? 'bg-green-100 text-green-600' :
                                                            'bg-slate-100 text-slate-500'
                                                        }`}>
                                                            {plan}
                                                        </span>
                                                    </div>
                                                </button>
                                            </li>
                                        );
                                    })}
                                </ul>
                            )}
                        </div>
                    </div>

                    {/* ── Right Panel: profile ── */}
                    <div className="flex flex-col gap-5">
                        {!selectedId && (
                            <div className="flex flex-col items-center justify-center rounded-2xl bg-white border border-slate-100 shadow-sm py-24 text-center">
                                <div className="text-4xl mb-3">👈</div>
                                <p className="text-slate-500 text-sm font-medium">Select a customer to inspect their data</p>
                                <p className="text-slate-400 text-xs mt-1">Compare what the bot said vs what's actually in the database</p>
                            </div>
                        )}

                        {selectedId && loading && (
                            <div className="rounded-2xl bg-white border border-slate-100 shadow-sm p-10 text-center text-slate-400 text-sm">
                                Loading profile…
                            </div>
                        )}

                        {selectedId && !loading && error && (
                            <div className="rounded-2xl bg-red-50 border border-red-200 p-6 text-red-700 text-sm">{error}</div>
                        )}

                        {selectedId && !loading && profile && (
                            <>
                                {/* Customer name banner */}
                                <div className="flex items-center justify-between rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-5 text-white shadow">
                                    <div>
                                        <h2 className="text-xl font-bold">{profile.customer?.name}</h2>
                                        <p className="text-blue-200 text-sm">{profile.customer?.email}</p>
                                        <p className="text-blue-300 text-xs font-mono mt-0.5">{profile.customer?.customer_id}</p>
                                    </div>
                                    <div className="text-right text-sm text-blue-100 space-y-0.5">
                                        <p>Plan: <strong className="text-white uppercase">{profile.subscription?.plan || 'none'}</strong></p>
                                        <p>Open tickets: <strong className="text-white">{profile.summary?.open_tickets}</strong></p>
                                        <p>Conversations: <strong className="text-white">{profile.conversations?.length}</strong></p>
                                    </div>
                                </div>

                                {/* Summary cards */}
                                <SummaryPanel summary={profile.summary} subscription={profile.subscription} />

                                {/* Tabs */}
                                <div className="flex flex-wrap gap-2 rounded-2xl bg-white border border-slate-100 p-1.5 shadow-sm w-fit">
                                    {tabs.map(t => (
                                        <button
                                            key={t}
                                            onClick={() => setActiveTab(t)}
                                            className={`rounded-xl px-5 py-2 text-sm font-semibold capitalize transition-all ${activeTab === t ? 'bg-blue-600 text-white shadow' : 'text-slate-600 hover:bg-slate-100'}`}
                                        >
                                            {t}
                                            {t === 'orders' && <span className="ml-1.5 text-xs opacity-70">({profile.orders?.length})</span>}
                                            {t === 'tickets' && <span className="ml-1.5 text-xs opacity-70">({profile.tickets?.length})</span>}
                                            {t === 'conversations' && <span className="ml-1.5 text-xs opacity-70">({profile.conversations?.length})</span>}
                                        </button>
                                    ))}
                                </div>

                                {/* Tab content */}
                                {activeTab === 'orders' && (
                                    <OrdersPanel orders={profile.orders || []} summary={profile.summary} />
                                )}
                                {activeTab === 'tickets' && (
                                    <TicketsPanel tickets={profile.tickets || []} />
                                )}
                                {activeTab === 'conversations' && (
                                    <ConversationsPanel conversations={profile.conversations || []} />
                                )}
                                {activeTab === 'profile' && (
                                    <ProfilePanel customer={profile.customer} subscription={profile.subscription} />
                                )}
                            </>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
