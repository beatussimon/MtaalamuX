# MtaalamuX Mobile

Production-ready Expo + React Native mobile app for MtaalamuX platform.

## Features
- JWT Authentication with automatic token refresh
- Expert discovery with verification badges
- Consultation-based messaging with time bounds
- Tier-based access (Basic/Plus/Premium)
- Real-time message polling

## Tech Stack
- Expo (Managed) + TypeScript
- Expo Router (file-based navigation)
- TanStack Query (server state)
- Axios + interceptors
- Expo SecureStore (tokens)
- Zustand (global state)
- NativeWind (Tailwind)
- React Hook Form + Zod

## Setup
```bash
cd mtx-mobile
npm install
cp .env.example .env
# Edit .env with your backend URL
npm run dev
```

## Testing
```bash
npm test
npm run test:coverage
```

## Building
```bash
npm run build:ios
npm run build:android
```

## Project Structure
```
mtx-mobile/
├── app/           # Expo Router screens
├── src/
│   ├── api/       # Axios client
│   ├── components/# UI components
│   ├── hooks/     # React Query hooks
│   ├── store/     # Zustand stores
│   ├── types/     # TypeScript types
│   └── utils/     # Helpers
└── tests/         # Jest tests
```

## Backend Requirements
- Django REST Framework API at `/api/`
- dj_rest_auth with JWT tokens
- Same endpoints as MTX backend
