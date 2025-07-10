# 🎨 Frontend Module

React-based web interface for the Brew Master AI chatbot, providing a modern, responsive user experience.

## 🎯 Purpose

This module provides the user interface for interacting with the Brew Master AI chatbot. It features:
- Real-time chat interface
- Responsive design for mobile and desktop
- Session management
- Modern UI with loading states and error handling

## ✨ Features

### 💬 Chat Interface
- **Real-time Messaging**: Send and receive messages instantly
- **Conversation History**: View current session messages
- **Message Types**: User messages and bot responses
- **Source Attribution**: Display information sources for transparency

### 📱 Responsive Design
- **Mobile-First**: Optimized for mobile devices
- **Desktop Support**: Enhanced experience on larger screens
- **Touch-Friendly**: Easy interaction on touch devices
- **Cross-Browser**: Works on all modern browsers

### 🔧 User Experience
- **Loading States**: Visual feedback during API calls
- **Error Handling**: Graceful error messages
- **Session Management**: Persistent conversation context
- **Clean Interface**: Minimal, focused design

## 🚀 Quick Start

### Prerequisites
```bash
# Node.js 16+
# Backend server running on localhost:8000
```

### Installation
```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

### Build for Production
```bash
# Build optimized version
npm run build

# Preview production build
npm run preview
```

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── App.jsx              # Main application component
│   ├── main.jsx             # Application entry point
│   ├── components/          # Reusable UI components
│   ├── hooks/               # Custom React hooks
│   ├── services/            # API service functions
│   ├── utils/               # Utility functions
│   └── styles/              # CSS and styling
├── public/                  # Static assets
├── package.json             # Dependencies and scripts
└── README.md               # This file
```

## 🔧 Development

### Available Scripts
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run test         # Run tests (if configured)
```

### Development Server
- **URL**: http://localhost:5173
- **Hot Reload**: Automatic refresh on file changes
- **Error Overlay**: In-browser error display

## 📡 API Integration

### Backend Connection
The frontend connects to the FastAPI backend at `http://localhost:8000`:

```javascript
// Example API call
const response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: userMessage,
    top_k: 3
  })
});
```

### API Endpoints Used
- `POST /chat` - Send chat messages and receive responses
- `GET /health` - Check backend status (optional)

## 🎨 UI Components

### Chat Interface
- **Message List**: Displays conversation history
- **Input Field**: Text input for user messages
- **Send Button**: Submit messages
- **Loading Indicator**: Shows during API calls

### Message Components
- **User Message**: Right-aligned, user styling
- **Bot Message**: Left-aligned, bot styling
- **Source Links**: Display information sources
- **Error Messages**: Handle API errors gracefully

## 🔧 Configuration

### Environment Variables
Create a `.env` file for configuration:

```bash
# Backend API URL
VITE_API_URL=http://localhost:8000

# Development settings
VITE_DEBUG=true
```

### API Configuration
```javascript
// src/config/api.js
export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  retries: 3
};
```

## 🧪 Testing

### Manual Testing
1. **Start Backend**: Ensure FastAPI server is running
2. **Start Frontend**: Run `npm run dev`
3. **Test Chat**: Send messages and verify responses
4. **Test Responsive**: Check mobile and desktop layouts
5. **Test Error Handling**: Disconnect backend and test errors

### Automated Testing
```bash
# Run tests (if configured)
npm run test

# Run tests in watch mode
npm run test:watch
```

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### Mobile Features
- Touch-friendly buttons
- Optimized input fields
- Swipe gestures (if implemented)
- Mobile-optimized layouts

## 🔒 Security

### CORS Configuration
The backend should be configured to allow requests from the frontend:

```python
# In backend/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Input Validation
- Sanitize user inputs before sending to API
- Validate message length and content
- Handle special characters properly

## 🚀 Deployment

### Build Process
```bash
# Create production build
npm run build

# Build output in dist/ directory
```

### Static Hosting
The frontend can be deployed to any static hosting service:

#### AWS S3 + CloudFront
```bash
# Upload to S3
aws s3 sync dist/ s3://your-bucket-name

# Configure CloudFront for CDN
```

#### Netlify
```bash
# Deploy to Netlify
netlify deploy --prod --dir=dist
```

#### Vercel
```bash
# Deploy to Vercel
vercel --prod
```

### Environment Configuration
For production, update environment variables:

```bash
# Production .env
VITE_API_URL=https://your-backend-api.com
VITE_DEBUG=false
```

## 🔧 Customization

### Styling
The frontend uses CSS modules or styled-components for styling:

```css
/* src/styles/Chat.css */
.chat-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.message {
  margin: 10px 0;
  padding: 10px;
  border-radius: 8px;
}
```

### Themes
Implement light/dark theme support:

```javascript
// Theme configuration
const themes = {
  light: {
    background: '#ffffff',
    text: '#000000',
    primary: '#007bff'
  },
  dark: {
    background: '#1a1a1a',
    text: '#ffffff',
    primary: '#4dabf7'
  }
};
```

## 🔍 Troubleshooting

### Common Issues

**Backend Connection Failed:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check CORS configuration
# Ensure backend allows frontend origin
```

**Build Errors:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node.js version
node --version  # Should be 16+
```

**Development Server Issues:**
```bash
# Check port availability
lsof -i :5173

# Use different port
npm run dev -- --port 3000
```

## 📈 Performance

### Optimization
- **Code Splitting**: Lazy load components
- **Bundle Analysis**: Monitor bundle size
- **Image Optimization**: Compress and optimize images
- **Caching**: Implement proper caching strategies

### Monitoring
- **Core Web Vitals**: Monitor performance metrics
- **Error Tracking**: Implement error monitoring
- **Analytics**: Track user interactions

## 🔄 Integration

### Backend Integration
The frontend is designed to work seamlessly with the FastAPI backend:
- JSON API communication
- Error handling and retry logic
- Session management
- Real-time updates

### Data Flow
```
User Input → Frontend → API Call → Backend → 
RAG Processing → Response → Frontend → Display
```

## 📚 Resources

### Documentation
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### Tools
- **React DevTools**: Browser extension for debugging
- **Vite DevTools**: Built-in development tools
- **Network Tab**: Monitor API calls and responses

## 🎯 Future Enhancements

- [ ] Real-time WebSocket communication
- [ ] File upload support
- [ ] Voice input/output
- [ ] Advanced theming
- [ ] Offline support
- [ ] Progressive Web App (PWA)
- [ ] Accessibility improvements
- [ ] Internationalization (i18n)
