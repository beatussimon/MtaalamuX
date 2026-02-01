# MtaalamuX - React Frontend

## Setup Instructions

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Create environment file:
```bash
cp .env.example .env
# Edit .env with your API URL
```

3. Start development server:
```bash
npm run dev
```

4. Build for production:
```bash
npm run build
```

## Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable components
│   │   ├── Header.jsx
│   │   ├── Sidebar.jsx
│   │   └── Layout.jsx
│   ├── pages/          # Page components
│   │   ├── HomePage.jsx
│   │   ├── LoginPage.jsx
│   │   ├── RegisterPage.jsx
│   │   ├── ProfessionalsPage.jsx
│   │   ├── ProfessionalDetailPage.jsx
│   │   ├── ArticlesPage.jsx
│   │   ├── ArticleDetailPage.jsx
│   │   ├── JobsPage.jsx
│   │   ├── DashboardPage.jsx
│   │   ├── ProfilePage.jsx
│   │   ├── MessagesPage.jsx
│   │   ├── NotificationsPage.jsx
│   │   ├── FAQPage.jsx
│   │   └── FeedbackPage.jsx
│   ├── store/          # State management (Zustand)
│   │   └── index.js
│   ├── services/       # API services
│   │   └── api.js
│   ├── App.jsx         # Main app component
│   ├── main.jsx        # Entry point
│   └── index.css       # Global styles
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── README.md
```

## Features

- ⚡️ Built with Vite for fast development
- 🎨 Modern UI with Tailwind CSS
- 🌙 Dark/Light mode support
- 🔐 JWT authentication
- 📱 Fully responsive design
- 🎭 Smooth animations with Framer Motion
- ♿ Accessible components
- 🧪 Unit and integration tests with Vitest
