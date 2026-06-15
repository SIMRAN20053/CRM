import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const customersAPI = {
  list: (params) => api.get('/customers', { params }).then((res) => res.data),
  get: (id) => api.get(`/customers/${id}`).then((res) => res.data),
  create: (data) => api.post('/customers', data).then((res) => res.data),
  bulkCreate: (data) => api.post('/customers/bulk', data).then((res) => res.data),
};

export const segmentsAPI = {
  list: () => api.get('/segments').then((res) => res.data),
  create: (data) => api.post('/segments', data).then((res) => res.data),
  get: (id) => api.get(`/segments/${id}`).then((res) => res.data),
  getCustomers: (id) => api.get(`/segments/${id}/customers`).then((res) => res.data),
};

export const campaignsAPI = {
  list: () => api.get('/campaigns').then((res) => res.data),
  create: (data) => api.post('/campaigns', data).then((res) => res.data),
  get: (id) => api.get(`/campaigns/${id}`).then((res) => res.data),
  launch: (id) => api.post(`/campaigns/${id}/launch`).then((res) => res.data),
  getStats: (id) => api.get(`/campaigns/${id}/stats`).then((res) => res.data),
  getLogs: (id, params) => api.get(`/campaigns/${id}/logs`, { params }).then((res) => res.data),
};

export const aiAPI = {
  generatePlan: (data) => api.post('/ai/objective', data).then((res) => res.data),
  getInsights: (campaignId) => api.post(`/ai/insights/${campaignId}`).then((res) => res.data),
};

export default api;
