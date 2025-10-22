'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api/client';
import type { Agent } from '@/types';

export default function UserDashboard() {
  const router = useRouter();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const user = api.getCurrentUser();

  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    try {
      const discoveredAgents = await api.discoverAgents();
      setAgents(discoveredAgents.slice(0, 3)); // Top 3 agents
    } catch (error) {
      console.error('Failed to load agents:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const stats = [
    { label: 'Queries This Week', value: '0', icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z', color: 'blue' },
    { label: 'Active Agents', value: agents.length.toString(), icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z', color: 'green' },
    { label: 'Avg Response Time', value: '45ms', icon: 'M13 10V3L4 14h7v7l9-11h-7z', color: 'orange' },
  ];

  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900">
          Welcome back, {user?.username}!
        </h1>
        <p className="text-slate-600 mt-2">
          Here's what's happening with your AI agents today
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className="bg-white rounded-xl p-6 border border-slate-200 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600 mb-1">{stat.label}</p>
                <p className="text-3xl font-bold text-slate-900">{stat.value}</p>
              </div>
              <div className={`w-12 h-12 bg-${stat.color}-100 rounded-xl flex items-center justify-center`}>
                <svg className={`w-6 h-6 text-${stat.color}-600`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={stat.icon} />
                </svg>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Query Console CTA */}
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl p-8 text-white relative overflow-hidden">
          <div className="relative z-10">
            <h3 className="text-2xl font-bold mb-2">Try the Console</h3>
            <p className="text-blue-100 mb-6">
              Start querying AI agents instantly with our chat interface
            </p>
            <Link
              href="/user/console"
              className="inline-flex items-center space-x-2 bg-white text-blue-600 px-6 py-3 rounded-lg font-medium hover:bg-blue-50 transition-colors"
            >
              <span>Open Console</span>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Link>
          </div>
          <div className="absolute -right-8 -bottom-8 w-32 h-32 bg-blue-400 rounded-full opacity-20"></div>
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-blue-400 rounded-full opacity-10"></div>
        </div>

        {/* Marketplace CTA */}
        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl p-8 text-white relative overflow-hidden">
          <div className="relative z-10">
            <h3 className="text-2xl font-bold mb-2">Explore Marketplace</h3>
            <p className="text-purple-100 mb-6">
              Discover new AI agents for any task you can imagine
            </p>
            <Link
              href="/user/marketplace"
              className="inline-flex items-center space-x-2 bg-white text-purple-600 px-6 py-3 rounded-lg font-medium hover:bg-purple-50 transition-colors"
            >
              <span>Browse Agents</span>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Link>
          </div>
          <div className="absolute -right-8 -bottom-8 w-32 h-32 bg-purple-400 rounded-full opacity-20"></div>
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-purple-400 rounded-full opacity-10"></div>
        </div>
      </div>

      {/* Featured Agents */}
      <div>
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">Featured Agents</h2>
            <p className="text-slate-600 mt-1">Popular agents on the network</p>
          </div>
          <Link
            href="/user/marketplace"
            className="text-blue-600 hover:text-blue-700 font-medium text-sm flex items-center space-x-1"
          >
            <span>View all</span>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </div>

        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-slate-600">Loading agents...</p>
          </div>
        ) : agents.length === 0 ? (
          <div className="bg-white rounded-xl p-12 text-center border border-slate-200">
            <div className="w-16 h-16 mx-auto mb-4 bg-slate-100 rounded-xl flex items-center justify-center">
              <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-slate-900 mb-2">No agents found</h3>
            <p className="text-slate-600 mb-6">Be the first to try out the protocol!</p>
            <Link
              href="/user/marketplace"
              className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Explore Marketplace
            </Link>
          </div>
        ) : (
          <div className="grid md:grid-cols-3 gap-6">
            {agents.map((agent) => (
              <div
                key={agent.did}
                className="bg-white rounded-xl p-6 border border-slate-200 hover:shadow-lg transition-all hover:border-blue-300 cursor-pointer"
                onClick={() => router.push(`/user/console?agent=${agent.did}`)}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl flex items-center justify-center">
                    <span className="text-white font-bold text-lg">
                      {agent.name.charAt(0)}
                    </span>
                  </div>
                  <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full font-medium">
                    Active
                  </span>
                </div>

                <h3 className="font-bold text-slate-900 mb-2">{agent.name}</h3>
                <p className="text-sm text-slate-600 mb-4 line-clamp-2">{agent.description}</p>

                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-500">
                    {agent.pricing.model === 'free' ? 'Free' : `$${agent.pricing.price_per_query}/query`}
                  </span>
                  <button className="text-blue-600 hover:text-blue-700 font-medium">
                    Try now →
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Recent Activity */}
      <div>
        <h2 className="text-2xl font-bold text-slate-900 mb-6">Recent Activity</h2>
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <div className="p-8 text-center text-slate-500">
            <svg className="w-12 h-12 mx-auto mb-4 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p>No recent activity yet</p>
            <p className="text-sm mt-2">Start querying agents to see your activity here</p>
          </div>
        </div>
      </div>
    </div>
  );
}
