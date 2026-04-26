import { apiClient } from '../lib/apiClient';

export async function registerUser(payload) {
    const { data } = await apiClient.post('/api/auth/register', payload);
    return data;
}

export async function loginUser(payload) {
    const { data } = await apiClient.post('/api/auth/login', payload);
    return data;
}

export async function getCurrentUser() {
    const { data } = await apiClient.get('/api/auth/me');
    return data;
}

export async function getHealth() {
    const { data } = await apiClient.get('/api/health');
    return data;
}

export async function sendChatMessage(payload) {
    const { data } = await apiClient.post('/api/chat', payload);
    return data;
}

export async function getConversationById(conversationId) {
    const { data } = await apiClient.get(`/api/conversation/${conversationId}`);
    return data;
}

export async function getConversations(limit = 20) {
    const { data } = await apiClient.get('/api/conversations', { params: { limit } });
    return data;
}

export async function getSystemStats() {
    const { data } = await apiClient.get('/api/admin/stats');
    return data;
}

export async function getTestDataOverview() {
    const { data } = await apiClient.get('/api/admin/test-data');
    return data;
}

export async function getAdminTickets({ status_filter, priority, limit = 50 } = {}) {
    const params = { limit };
    if (status_filter) params.status_filter = status_filter;
    if (priority) params.priority = priority;
    const { data } = await apiClient.get('/api/admin/tickets', { params });
    return data;
}

export async function updateTicketStatus(ticketId, newStatus) {
    const { data } = await apiClient.patch(`/api/admin/tickets/${ticketId}/status`, { status: newStatus });
    return data;
}

export async function getTicketDetail(ticketId) {
    const { data } = await apiClient.get(`/api/admin/tickets/${ticketId}`);
    return data;
}

export async function getAdminCustomers(limit = 100) {
    const { data } = await apiClient.get('/api/admin/customers', { params: { limit } });
    return data;
}

export async function getAdminCustomerProfile(customerId) {
    const { data } = await apiClient.get(`/api/admin/customers/${customerId}`);
    return data;
}
