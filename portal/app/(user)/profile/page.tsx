'use client';

import { useState } from 'react';
import { api } from '@/lib/api/client';

export default function ProfilePage() {
  const user = api.getCurrentUser();
  const [apiToken, setApiToken] = useState('');

  const generateApiToken = () => {
    const token = `poros_${Math.random().toString(36).substring(2, 15)}${Math.random().toString(36).substring(2, 15)}`;
    setApiToken(token);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="space-y-8 max-w-4xl">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Profile Settings</h1>
        <p className="text-slate-600 mt-2">Manage your account and preferences</p>
      </div>

      {/* Account Information */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div className="px-6 py-4 bg-slate-50 border-b border-slate-200">
          <h2 className="font-semibold text-slate-900">Account Information</h2>
        </div>
        <div className="p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Username</label>
            <input
              type="text"
              value={user?.username || ''}
              disabled
              className="w-full px-4 py-3 border border-slate-300 rounded-lg bg-slate-50 text-slate-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Email</label>
            <input
              type="email"
              value={user?.email || ''}
              disabled
              className="w-full px-4 py-3 border border-slate-300 rounded-lg bg-slate-50 text-slate-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Role</label>
            <div className="flex items-center space-x-2">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                user?.role === 'builder'
                  ? 'bg-purple-100 text-purple-700'
                  : 'bg-blue-100 text-blue-700'
              }`}>
                {user?.role || 'user'}
              </span>
            </div>
          </div>

          {user?.did && (
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Decentralized Identifier (DID)
              </label>
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  value={user.did}
                  disabled
                  className="flex-1 px-4 py-3 border border-slate-300 rounded-lg bg-slate-50 text-slate-500 font-mono text-sm"
                />
                <button
                  onClick={() => copyToClipboard(user.did!)}
                  className="px-4 py-3 border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
                >
                  <svg className="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </button>
              </div>
              <p className="text-xs text-slate-500 mt-2">Your cryptographically verified identity on the network</p>
            </div>
          )}
        </div>
      </div>

      {/* API Access */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div className="px-6 py-4 bg-slate-50 border-b border-slate-200">
          <h2 className="font-semibold text-slate-900">API Access</h2>
        </div>
        <div className="p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">API Token</label>
            <p className="text-sm text-slate-600 mb-4">
              Use this token to access the Poros Protocol API from your applications
            </p>
            {apiToken ? (
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  value={apiToken}
                  readOnly
                  className="flex-1 px-4 py-3 border border-slate-300 rounded-lg bg-slate-50 font-mono text-sm"
                />
                <button
                  onClick={() => copyToClipboard(apiToken)}
                  className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Copy
                </button>
              </div>
            ) : (
              <button
                onClick={generateApiToken}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Generate API Token
              </button>
            )}
          </div>

          <div className="bg-slate-50 rounded-lg p-4">
            <h3 className="font-medium text-slate-900 mb-2">Example Usage</h3>
            <pre className="text-xs text-slate-600 font-mono overflow-x-auto">
{`curl -X POST https://poros-protocol-production.up.railway.app/api/orchestrate/discover \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"capability": "weather_forecast"}'`}
            </pre>
          </div>
        </div>
      </div>

      {/* Preferences */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div className="px-6 py-4 bg-slate-50 border-b border-slate-200">
          <h2 className="font-semibold text-slate-900">Preferences</h2>
        </div>
        <div className="p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium text-slate-900">Email Notifications</div>
              <div className="text-sm text-slate-600">Receive updates about your queries</div>
            </div>
            <button className="relative inline-flex h-6 w-11 items-center rounded-full bg-slate-300 transition-colors">
              <span className="inline-block h-4 w-4 transform rounded-full bg-white transition-transform translate-x-1" />
            </button>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium text-slate-900">Query History</div>
              <div className="text-sm text-slate-600">Save your conversation history</div>
            </div>
            <button className="relative inline-flex h-6 w-11 items-center rounded-full bg-blue-600 transition-colors">
              <span className="inline-block h-4 w-4 transform rounded-full bg-white transition-transform translate-x-6" />
            </button>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium text-slate-900">Dark Mode</div>
              <div className="text-sm text-slate-600">Coming soon</div>
            </div>
            <button disabled className="relative inline-flex h-6 w-11 items-center rounded-full bg-slate-200 transition-colors opacity-50 cursor-not-allowed">
              <span className="inline-block h-4 w-4 transform rounded-full bg-white transition-transform translate-x-1" />
            </button>
          </div>
        </div>
      </div>

      {/* Danger Zone */}
      <div className="bg-white rounded-xl border-2 border-red-200 overflow-hidden">
        <div className="px-6 py-4 bg-red-50 border-b border-red-200">
          <h2 className="font-semibold text-red-900">Danger Zone</h2>
        </div>
        <div className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium text-slate-900">Delete Account</div>
              <div className="text-sm text-slate-600">Permanently delete your account and all data</div>
            </div>
            <button className="px-4 py-2 border-2 border-red-600 text-red-600 rounded-lg hover:bg-red-50 transition-colors font-medium">
              Delete Account
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
