// Poros Protocol Types

export interface User {
  id: number;
  username: string;
  email: string;
  did?: string;
  role: 'user' | 'builder' | 'admin';
  created_at: string;
}

export interface Agent {
  id: number;
  agent_id: string;
  did: string;
  owner_id: number;
  name: string;
  description: string;
  url: string;
  capabilities: string[];
  skills: string[];
  pricing: {
    model: 'free' | 'per_query' | 'subscription';
    price_per_query?: number;
    subscription_tiers?: SubscriptionTier[];
  };
  is_active: boolean;
  created_at: string;
  updated_at: string;
  stats?: AgentStats;
  reputation?: AgentReputation;
}

export interface AgentStats {
  total_queries: number;
  successful_queries: number;
  failed_queries: number;
  avg_response_time_ms: number;
  uptime_percentage: number;
  last_query_at?: string;
}

export interface AgentReputation {
  rating: number; // 0-5
  total_ratings: number;
  trust_score: number; // 0-100
  verified: boolean;
}

export interface SubscriptionTier {
  name: string;
  price_per_month: number;
  queries_per_month: number;
  features: string[];
}

export interface QueryLog {
  id: number;
  user_id: number;
  agent_id: string;
  agent_did: string;
  query: any;
  response: any;
  status: 'success' | 'failed' | 'timeout';
  latency_ms: number;
  cost: number;
  timestamp: string;
}

export interface Transaction {
  id: number;
  user_id: number;
  agent_id: string;
  amount: number;
  currency: 'usd' | 'credits';
  type: 'query' | 'subscription' | 'topup';
  status: 'pending' | 'completed' | 'failed';
  timestamp: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RegisterAgentRequest {
  agent_card: {
    version: string;
    did: string;
    name: string;
    description: string;
    url: string;
    capabilities: string[];
    skills: string[];
    pricing: Agent['pricing'];
    actions: AgentAction[];
    signature: string;
  };
}

export interface AgentAction {
  name: string;
  description: string;
  parameters: Record<string, {
    type: string;
    required: boolean;
    description?: string;
  }>;
}

export interface DiscoverRequest {
  capability?: string;
  skills?: string[];
  filters?: {
    max_price?: number;
    min_rating?: number;
    verified_only?: boolean;
  };
}

export interface QueryRequest {
  agent_did: string;
  query: {
    action: string;
    parameters: Record<string, any>;
  };
}

export interface QueryResponse {
  agent_did: string;
  response: {
    status: string;
    result: any;
    error: string | null;
  };
  signature: string | null;
}
