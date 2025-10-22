# Poros Portal - Next.js Frontend

Complete dual-portal interface for the Poros Protocol decentralized AI agent network.

## Project Structure

```
portal/
├── app/
│   ├── (user)/              # User Portal (route group)
│   │   ├── dashboard/       # User dashboard with stats
│   │   ├── marketplace/     # Agent discovery & search
│   │   ├── console/         # Query interface (chat-style)
│   │   └── profile/         # User settings & API keys
│   ├── (builder)/           # Builder Portal (route group)
│   │   ├── studio/          # Builder dashboard & analytics
│   │   ├── agents/          # Agent management (CRUD)
│   │   ├── analytics/       # Performance metrics & graphs
│   │   └── payments/        # Monetization & payouts
│   ├── auth/
│   │   ├── login/
│   │   └── register/
│   ├── api/                 # Next.js API routes
│   │   ├── auth/
│   │   ├── agents/
│   │   └── users/
│   ├── layout.tsx           # Root layout
│   └── page.tsx             # Landing page
├── components/
│   ├── ui/                  # Reusable UI components (buttons, cards, etc.)
│   ├── user/                # User portal specific components
│   └── builder/             # Builder portal specific components
├── lib/
│   ├── api/
│   │   └── client.ts        # API client for backend communication
│   └── utils.ts             # Utility functions
├── hooks/                   # Custom React hooks
├── types/
│   └── index.ts             # TypeScript type definitions
├── .env.local               # Environment variables
└── package.json
```

## Features

### User Portal "Poros AI Console"

1. **Dashboard**
   - Personalized greeting
   - Query statistics (queries/week, avg latency)
   - Favorite agents
   - Trending agent recommendations

2. **Marketplace**
   - Search & filter agents by:
     - Category/tags
     - Performance score
     - Trust rating
     - Price (free/paid)
   - Agent cards show:
     - Name, description, developer
     - Rating, uptime %, pricing
     - "Try Now" button

3. **Query Console**
   - Chat-style interface
   - Multi-agent support
   - Response cards with:
     - Agent attribution
     - Signature verification status
     - Execution time
   - Conversation history

4. **Profile/Settings**
   - DID management
   - Email/password
   - API tokens
   - Preferences (theme, privacy)

### Builder Portal "Poros Studio"

1. **Studio Dashboard**
   - Overview of registered agents
   - Metrics per agent:
     - Total queries served
     - Success rate
     - Avg response latency
   - Revenue graphs (if monetized)

2. **Agent Management**
   - Register new agent form
   - Auto-generated DID + keypair
   - Edit existing agents
   - Uptime monitoring
   - Recent query logs

3. **Analytics**
   - Performance metrics:
     - Queries/day graph
     - Response time trends
     - Success/failure rates
   - User retention metrics

4. **Payments/Monetization**
   - Pricing model selection:
     - Free
     - Per-query microtransactions
     - Subscription tiers
   - Revenue dashboard
   - Payout settings (Stripe integration later)

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **UI Components**: Radix UI
- **Charts**: Recharts
- **HTTP Client**: Axios
- **JWT**: jose
- **Backend**: Poros Protocol FastAPI (Railway)

## Environment Variables

```bash
NEXT_PUBLIC_BACKEND_URL=https://poros-protocol-production.up.railway.app
NEXT_PUBLIC_APP_NAME=Poros Protocol
NEXT_PUBLIC_APP_VERSION=2.0
```

## Getting Started

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

Visit http://localhost:3000

## API Integration

The portal connects to the Poros Protocol backend at:
- **Production**: https://poros-protocol-production.up.railway.app
- **Local Dev**: http://localhost:8000

### Key Endpoints Used

**User Auth**:
- `POST /api/registry/users` - Register
- `POST /api/registry/users/login` - Login

**Agent Discovery**:
- `POST /api/orchestrate/discover` - Find agents
- `POST /api/orchestrate/query` - Query agent

**Agent Management** (Builder):
- `POST /api/registry/agents` - Register agent
- `GET /api/registry/agents/me` - List my agents
- `PUT /api/registry/agents/{id}` - Update agent
- `DELETE /api/registry/agents/{id}` - Delete agent

## Development Roadmap

### Phase 1: Foundation (Current)
- [x] Project setup
- [x] Type definitions
- [x] API client
- [ ] Landing page
- [ ] Auth pages (login/register)

### Phase 2: User Portal
- [ ] Dashboard
- [ ] Marketplace with search/filter
- [ ] Query Console (chat interface)
- [ ] Profile settings

### Phase 3: Builder Portal
- [ ] Studio dashboard
- [ ] Agent registration form
- [ ] Agent list & management
- [ ] Analytics graphs

### Phase 4: Advanced Features
- [ ] Real-time query streaming (WebSockets)
- [ ] Agent reputation algorithm
- [ ] Payment integration (Stripe)
- [ ] DID-based login

### Phase 5: Decentralization
- [ ] DHT-based agent discovery
- [ ] On-chain payments (Aurora Credits)
- [ ] Poros Passport (DID identity)

## Contributing

This is part of the Poros Protocol project. See main README for contribution guidelines.

## License

MIT
