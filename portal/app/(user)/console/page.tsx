'use client';

import { Suspense, useEffect, useState, useRef } from 'react';
import { useSearchParams } from 'next/navigation';
import { api } from '@/lib/api/client';
import type { Agent, QueryResponse } from '@/types';

interface Message {
  id: string;
  role: 'user' | 'agent';
  content: string;
  agentName?: string;
  timestamp: Date;
  latency?: number;
  status?: 'success' | 'error';
}

function ConsoleContent() {
  const searchParams = useSearchParams();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadAgents();
  }, []);

  useEffect(() => {
    const agentDid = searchParams.get('agent');
    if (agentDid && agents.length > 0) {
      const agent = agents.find((a) => a.did === agentDid);
      if (agent) setSelectedAgent(agent);
    }
  }, [searchParams, agents]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadAgents = async () => {
    try {
      const discovered = await api.discoverAgents();
      setAgents(discovered);
      if (discovered.length > 0 && !selectedAgent) {
        setSelectedAgent(discovered[0]);
      }
    } catch (error) {
      console.error('Failed to load agents:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !selectedAgent) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    const startTime = Date.now();

    try {
      const response: QueryResponse = await api.queryAgent({
        agent_did: selectedAgent.did,
        query: {
          action: 'query',
          parameters: { query: input },
        },
      });

      const latency = Date.now() - startTime;

      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'agent',
        content: JSON.stringify(response.response.result, null, 2),
        agentName: selectedAgent.name,
        timestamp: new Date(),
        latency,
        status: response.response.status === 'success' ? 'success' : 'error',
      };

      setMessages((prev) => [...prev, agentMessage]);
    } catch (error: any) {
      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'agent',
        content: error.message || 'Failed to get response from agent',
        agentName: selectedAgent.name,
        timestamp: new Date(),
        status: 'error',
      };

      setMessages((prev) => [...prev, agentMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-[calc(100vh-12rem)] flex gap-6">
      {/* Agent Selector Sidebar */}
      <div className="w-64 flex-shrink-0 bg-white rounded-xl border border-slate-200 p-4 overflow-y-auto">
        <h3 className="font-semibold text-slate-900 mb-4">Active Agents</h3>
        <div className="space-y-2">
          {agents.map((agent) => (
            <button
              key={agent.did}
              onClick={() => setSelectedAgent(agent)}
              className={`w-full text-left p-3 rounded-lg transition-all ${
                selectedAgent?.did === agent.did
                  ? 'bg-blue-50 border-2 border-blue-300'
                  : 'bg-slate-50 border-2 border-transparent hover:border-slate-200'
              }`}
            >
              <div className="flex items-start space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center flex-shrink-0">
                  <span className="text-white font-bold">{agent.name.charAt(0)}</span>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-slate-900 text-sm truncate">{agent.name}</div>
                  <div className="text-xs text-slate-500 truncate">{agent.capabilities[0]}</div>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 bg-white rounded-xl border border-slate-200 flex flex-col overflow-hidden">
        {/* Chat Header */}
        <div className="px-6 py-4 border-b border-slate-200 bg-slate-50">
          {selectedAgent ? (
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold">{selectedAgent.name.charAt(0)}</span>
                </div>
                <div>
                  <h2 className="font-semibold text-slate-900">{selectedAgent.name}</h2>
                  <p className="text-xs text-slate-500">{selectedAgent.description}</p>
                </div>
              </div>
              <span className="text-xs bg-green-100 text-green-700 px-3 py-1 rounded-full font-medium">
                Online
              </span>
            </div>
          ) : (
            <p className="text-slate-600">Select an agent to start chatting</p>
          )}
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center max-w-md">
                <div className="w-16 h-16 mx-auto mb-4 bg-blue-100 rounded-2xl flex items-center justify-center">
                  <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                    />
                  </svg>
                </div>
                <h3 className="font-semibold text-slate-900 mb-2">Start a conversation</h3>
                <p className="text-sm text-slate-600">
                  Ask {selectedAgent?.name || 'an agent'} anything. Try asking about the weather, latest news, or any task it can help with.
                </p>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-[70%] ${message.role === 'user' ? 'order-2' : ''}`}>
                    <div
                      className={`rounded-2xl px-4 py-3 ${
                        message.role === 'user'
                          ? 'bg-blue-600 text-white'
                          : message.status === 'error'
                          ? 'bg-red-50 text-red-900 border border-red-200'
                          : 'bg-slate-100 text-slate-900'
                      }`}
                    >
                      {message.role === 'agent' && (
                        <div className="text-xs font-medium mb-1 opacity-70">{message.agentName}</div>
                      )}
                      <div className="text-sm whitespace-pre-wrap break-words">{message.content}</div>
                    </div>
                    <div className="flex items-center space-x-2 mt-1 px-2">
                      <span className="text-xs text-slate-500">
                        {message.timestamp.toLocaleTimeString()}
                      </span>
                      {message.latency && (
                        <span className="text-xs text-slate-400">• {message.latency}ms</span>
                      )}
                      {message.status === 'success' && (
                        <svg className="w-3 h-3 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                            clipRule="evenodd"
                          />
                        </svg>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-slate-100 rounded-2xl px-4 py-3">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input */}
        <div className="p-4 border-t border-slate-200">
          <form onSubmit={handleSubmit} className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={!selectedAgent || isLoading}
              placeholder={selectedAgent ? `Message ${selectedAgent.name}...` : 'Select an agent first...'}
              className="flex-1 px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none disabled:bg-slate-50 disabled:text-slate-400"
            />
            <button
              type="submit"
              disabled={!selectedAgent || isLoading || !input.trim()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}


export default function QueryConsolePage() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center h-full"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div></div>}>
      <ConsoleContent />
    </Suspense>
  );
}
