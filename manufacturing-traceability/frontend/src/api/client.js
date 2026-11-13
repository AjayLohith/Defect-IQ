// Central API Client for TraceFlow REST endpoints
const API_BASE = '/api/v1';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  const response = await fetch(url, { ...options, headers });
  
  const contentType = response.headers.get('content-type') || '';
  if (!response.ok) {
    let message = `HTTP Error ${response.status}`;
    let code;
    let errorBody = {};
    if (contentType.includes('application/json')) {
      errorBody = await response.json().catch(() => ({}));
      message = errorBody?.detail?.message || errorBody?.detail || message;
      code = errorBody?.detail?.code;
    } else {
      const text = await response.text();
      message = `Server returned ${response.status}: ${text.slice(0, 150)}`;
    }
    const error = new Error(typeof message === 'object' ? JSON.stringify(message) : message);
    error.status = response.status;
    error.code = code;
    error.details = errorBody;
    throw error;
  }

  if (!contentType.includes('application/json')) {
    const text = await response.text();
    throw new Error(`Expected JSON response from backend but received ${contentType || 'non-JSON content'}. Please ensure backend API is running and reachable.`);
  }

  return response.json();
}

export const api = {
  // System Health & Validation
  getHealth: () => request('/health'),
  getValidationReports: () => request('/validation/reports'),
  runValidation: () => request('/validation/run', { method: 'POST' }),

  // Dashboard & Metrics
  getDashboardMetrics: () => request('/dashboard/metrics'),
  getMachineDrift: () => request('/dashboard/drift'),

  // Defects
  getDefects: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/defects${query ? `?${query}` : ''}`);
  },
  getDefect: (id) => request(`/defects/${id}`),
  createDefect: (data) => request('/defects', { method: 'POST', body: JSON.stringify(data) }),

  // Containment Actions
  getContainmentActions: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/containment${query ? `?${query}` : ''}`);
  },
  createContainmentAction: (data) => request('/containment', { method: 'POST', body: JSON.stringify(data) }),

  // Corrective Actions (CAPA)
  getCAPAs: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/capas${query ? `?${query}` : ''}`);
  },
  getCAPA: (id) => request(`/capas/${id}`),
  createCAPA: (data) => request('/capas', { method: 'POST', body: JSON.stringify(data) }),
  addVerification: (capaId, data) => request(`/capas/${capaId}/verifications`, { method: 'POST', body: JSON.stringify(data) }),
  closeCAPA: (capaId, data) => request(`/capas/${capaId}/close`, { method: 'POST', body: JSON.stringify(data) }),

  // Traceability
  getUpstreamTrace: (defectId) => request(`/traceability/upstream/${defectId}`),
  getDownstreamImpact: (lotId) => request(`/traceability/downstream/${lotId}`),

  // Production Orders
  getOrders: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/orders${query ? `?${query}` : ''}`);
  },
  getOrder: (id) => request(`/orders/${id}`),
  getOrderBOMReconciliation: (id) => request(`/orders/${id}/bom-reconciliation`),

  // Material Lots
  getLots: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/lots${query ? `?${query}` : ''}`);
  },
  getLot: (id) => request(`/lots/${id}`),
};

