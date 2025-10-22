import axios, { AxiosInstance } from 'axios';
import type {
  User,
  Agent,
  AuthResponse,
  QueryRequest,
  QueryResponse,
  DiscoverRequest,
  QueryLog,
  AgentStats
} from '@/types';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://poros-protocol-production.up.railway.app';

class PorosAPI {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: `${BACKEND_URL}/api`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include auth token
    this.client.interceptors.request.use((config) => {
      if (this.token) {
        config.headers.Authorization = `Bearer ${this.token}`;
      }
      return config;
    });
  }

  // Set token from localStorage or cookie
  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('poros_token', token);
    }
  }

  // Clear token
  clearToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('poros_token');
      localStorage.removeItem('poros_user');
    }
  }

  // Load token from storage
  loadToken() {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('poros_token');
      if (token) {
        this.token = token;
      }
    }
  }

  // Auth APIs
  async register(username: string, email: string, password: string): Promise<AuthResponse> {
    const response = await this.client.post('/registry/users', {
      username,
      email,
      password,
    });

    const authData: AuthResponse = {
      access_token: response.data.access_token,
      token_type: 'bearer',
      user: {
        id: response.data.user_id || 0,
        username,
        email,
        role: 'user',
        created_at: new Date().toISOString(),
      }
    };

    this.setToken(authData.access_token);
    if (typeof window !== 'undefined') {
      localStorage.setItem('poros_user', JSON.stringify(authData.user));
    }

    return authData;
  }

  async login(username: string, password: string): Promise<AuthResponse> {
    const response = await this.client.post('/registry/users/login', {
      username,
      password,
    });

    const authData: AuthResponse = {
      access_token: response.data.access_token || response.data.token,
      token_type: 'bearer',
      user: response.data.user || {
        id: 0,
        username,
        email: '',
        role: 'user',
        created_at: new Date().toISOString(),
      }
    };

    this.setToken(authData.access_token);
    if (typeof window !== 'undefined') {
      localStorage.setItem('poros_user', JSON.stringify(authData.user));
    }

    return authData;
  }

  logout() {
    this.clearToken();
  }

  // Get current user from storage
  getCurrentUser(): User | null {
    if (typeof window !== 'undefined') {
      const userStr = localStorage.getItem('poros_user');
      return userStr ? JSON.parse(userStr) : null;
    }
    return null;
  }

  // Agent Discovery APIs
  async discoverAgents(request?: DiscoverRequest): Promise<Agent[]> {
    const response = await this.client.post('/orchestrate/discover', request || {});
    return response.data.agents || [];
  }

  // Query Agent
  async queryAgent(request: QueryRequest): Promise<QueryResponse> {
    const response = await this.client.post('/orchestrate/query', request);
    return response.data;
  }

  // Agent Registration (for builders)
  async registerAgent(agentCard: any): Promise<Agent> {
    const response = await this.client.post('/registry/agents', {
      agent_card: agentCard,
    });
    return response.data;
  }

  // Get user's agents
  async getMyAgents(): Promise<Agent[]> {
    const response = await this.client.get('/registry/agents/me');
    return response.data.agents || [];
  }

  // Update agent
  async updateAgent(agentId: string, updates: Partial<Agent>): Promise<Agent> {
    const response = await this.client.put(`/registry/agents/${agentId}`, updates);
    return response.data;
  }

  // Delete agent
  async deleteAgent(agentId: string): Promise<void> {
    await this.client.delete(`/registry/agents/${agentId}`);
  }

  // Get agent stats
  async getAgentStats(agentId: string): Promise<AgentStats> {
    const response = await this.client.get(`/registry/agents/${agentId}/stats`);
    return response.data;
  }

  // Get query history
  async getQueryHistory(limit = 50): Promise<QueryLog[]> {
    const response = await this.client.get(`/registry/queries?limit=${limit}`);
    return response.data.queries || [];
  }
}

// Export singleton instance
export const api = new PorosAPI();
