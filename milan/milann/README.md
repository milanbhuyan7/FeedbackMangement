# Feedback Tool - Production Ready with Real-Time Features

A comprehensive feedback management system built with React (Vite) frontend using **Bootstrap CSS** and Django backend with **Django Channels** for real-time WebSocket communication, connected to **Render PostgreSQL database** and using **email-based authentication**.

## 🌐 Live URLs

### Production Deployment
- **Frontend**: https://feedback-mangement.vercel.app/
- **Backend API**: https://feedbackmangement.onrender.com/api/
- **WebSocket**: wss://feedbackmangement.onrender.com/ws/sse/{user_id}/

### Development
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/
- **WebSocket**: ws://localhost:8000/ws/sse/{user_id}/

## 🚀 Features

### 🔐 Email-Based Authentication
- **Email as username** - Users login with their email address
- **Simple password authentication** - Password is just "password"
- **JWT-based authentication** with custom email backend
- Two user roles: Manager and Employee
- Role-based access control

### 🗄️ Render PostgreSQL Database
- **Cloud database** hosted on Render
- **Production-ready** PostgreSQL setup
- **Automatic connection** via DATABASE_URL
- **No local database setup** required

### ⚡ Optimized Real-Time Updates
- **On-demand WebSocket connections** - Only connects when users are active
- **Smart duplicate prevention** - Prevents double display of feedback
- **Connection status indicator** - Shows live/offline status
- **Automatic reconnection** with exponential backoff
- **No continuous polling** - Reduces server load and timeout errors

### 🎨 Modern Bootstrap UI
- **Bootstrap 5.3** for responsive design
- **Bootstrap Icons** for consistent iconography
- Clean, professional interface
- Mobile-responsive design

## 🔧 Fixed Issues

### ✅ SSE/WebSocket Optimization
- **Conditional connections** - Only sends events to connected users
- **Prevents duplicate data** - Smart state management prevents double display
- **Reduced timeouts** - No more continuous polling causing 10s timeout errors
- **Connection management** - Proper connect/disconnect lifecycle

### ✅ Production URLs
- **Automatic environment detection** - Switches between dev/prod URLs
- **CORS configuration** - Proper cross-origin setup for production
- **WebSocket URLs** - Both HTTP and HTTPS WebSocket support

### ✅ Performance Improvements
- **Increased timeout** - 30s timeout for production API calls
- **Smart reconnection** - Exponential backoff for WebSocket reconnection
- **Memory optimization** - Prevents memory leaks from continuous connections

## 🛠 Tech Stack

### Frontend
- **React 18** with Vite
- **Bootstrap 5.3** for styling and components
- **Bootstrap Icons** for iconography
- **WebSocket** for real-time communication (on-demand)
- **React Router** for navigation

### Backend
- **Django 4.2** with Django REST Framework
- **Django Channels 4.0** for WebSocket support
- **Daphne** ASGI server
- **Render PostgreSQL** database
- **Email authentication backend**
- **JWT Authentication** with Simple JWT

## 🔄 Real-Time Architecture

### WebSocket Events Supported:
- `new_feedback` - When a manager submits new feedback
- `feedback_updated` - When feedback is edited
- `feedback_deleted` - When feedback is removed
- `feedback_acknowledged` - When an employee acknowledges feedback
- `feedback_created` - Manager dashboard updates

### Smart Connection Management:
- **JWT-authenticated WebSocket connections**
- **User presence detection** - Only sends events to connected users
- **Automatic heartbeat** to keep connections alive
- **Graceful reconnection** with exponential backoff
- **Duplicate prevention** - Smart state management

## 🚀 Quick Start

### Prerequisites
- Node.js 16+
- Python 3.10+
- **No PostgreSQL setup required** - uses Render database ✅
- **No Redis required** - uses in-memory channel layer ✅

### Backend Setup

1. **Navigate to backend directory:**
   \`\`\`bash
   cd backend
   \`\`\`

2. **Create virtual environment:**
   \`\`\`bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   \`\`\`

3. **Install dependencies:**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

4. **Environment is pre-configured:**
   - DATABASE_URL points to Render PostgreSQL
   - Production URLs configured
   - No additional configuration needed

5. **Run migrations:**
   \`\`\`bash
   python manage.py makemigrations
   python manage.py migrate
   \`\`\`

6. **Create sample data:**
   \`\`\`bash
   python scripts/create_sample_data.py
   \`\`\`

7. **Check setup (optional):**
   \`\`\`bash
   python scripts/check_setup.py
   \`\`\`

8. **Start development server:**
   \`\`\`bash
   python manage.py runserver
   \`\`\`

### Frontend Setup

1. **Navigate to frontend directory:**
   \`\`\`bash
   cd ../  # Go back to root
   \`\`\`

2. **Install dependencies:**
   \`\`\`bash
   npm install
   \`\`\`

3. **Start development server:**
   \`\`\`bash
   npm run dev
   \`\`\`

## 🔑 Demo Accounts (Email Authentication)

After running the sample data script:

- **Manager**: `manager@company.com` / `password`
- **Employee**: `employee@company.com` / `password`
- **Employee 2**: `bob@company.com` / `password`

**Note:** Use email addresses as usernames for login.

## 🔄 Real-Time Testing

### Test Real-Time Updates:

1. **Open two browser windows:**
   - Window 1: Login as `manager@company.com` / `password`
   - Window 2: Login as `employee@company.com` / `password`

2. **Test scenarios:**
   - Manager submits feedback → Employee sees instant notification
   - Employee acknowledges feedback → Manager sees instant update
   - Manager edits feedback → Employee sees changes immediately
   - Manager deletes feedback → Employee sees removal instantly

3. **Connection status:**
   - Check the live indicator (🟢 Live / ⚠️ Offline) in the header
   - No more continuous polling or timeout errors

## 🌐 Deployment

### Backend (Render)
1. **Connect GitHub repository** to Render
2. **Set environment variables:**
   \`\`\`
   DATABASE_URL=postgresql://feedback_user:2YUjcbWrq9FmaPuSRCIQyqtilLxDAQvA@dpg-d1chjrndiees73c4pt50-a.oregon-postgres.render.com/feedback_grk6
   DEBUG=False
   SECRET_KEY=your-production-secret-key
   \`\`\`
3. **Deploy** - Render will automatically build and deploy

### Frontend (Vercel)
1. **Connect GitHub repository** to Vercel
2. **Set build command:** `npm run build`
3. **Set output directory:** `dist`
4. **Deploy** - Vercel will automatically build and deploy

## 📡 API Endpoints

### Authentication
- `POST /api/token/` - Login (use email as username)
- `POST /api/token/refresh/` - Refresh token
- `POST /api/register/` - Register new user

### User Management
- `GET /api/user/profile/` - Get current user profile
- `GET /api/team/` - Get team members (Manager only)

### Feedback Management
- `GET /api/feedbacks/` - List feedback
- `POST /api/feedbacks/` - Create feedback (Manager only)
- `PUT /api/feedbacks/{id}/` - Update feedback (Manager only)
- `DELETE /api/feedbacks/{id}/` - Delete feedback (Manager only)
- `POST /api/feedbacks/{id}/acknowledge/` - Acknowledge feedback (Employee only)

### Real-Time WebSocket
- **Development**: `ws://localhost:8000/ws/sse/{user_id}/?token={jwt_token}`
- **Production**: `wss://feedbackmangement.onrender.com/ws/sse/{user_id}/?token={jwt_token}`

## 🎯 Key Benefits

✅ **Production Ready** - Deployed on Render & Vercel  
✅ **Render PostgreSQL** - Cloud database, no local setup  
✅ **Email Authentication** - User-friendly login with email  
✅ **Optimized Real-time** - No continuous polling, prevents timeouts  
✅ **Smart Duplicate Prevention** - No more double display issues  
✅ **Connection Management** - Shows live/offline status  
✅ **Bootstrap UI** - Modern, responsive design  
✅ **Auto Environment Detection** - Works in dev and production  

## ⚠️ Important Notes

### Real-time Features:
- **On-demand connections** - WebSocket only connects when needed
- **Smart event handling** - Only sends events to connected users
- **Duplicate prevention** - Local state management prevents double display
- **Connection status** - Visual indicator shows connection state

### Production:
- **Automatic URL switching** - Detects environment and uses correct URLs
- **CORS configured** - Proper cross-origin setup for production
- **Security headers** - Production security settings enabled

## 🚀 GitHub Deployment

### Ready to Push:
\`\`\`bash
# Add all files
git add .

# Commit changes
git commit -m "Production ready: Fixed SSE issues, added production URLs, optimized real-time features"

# Push to GitHub
git push origin main
\`\`\`

### Environment Variables for Production:

**Render (Backend):**
\`\`\`env
DATABASE_URL=postgresql://feedback_user:2YUjcbWrq9FmaPuSRCIQyqtilLxDAQvA@dpg-d1chjrndiees73c4pt50-a.oregon-postgres.render.com/feedback_grk6
DEBUG=False
SECRET_KEY=your-production-secret-key-here
ALLOWED_HOSTS=feedbackmangement.onrender.com
\`\`\`

**Vercel (Frontend):**
\`\`\`env
VITE_API_BASE_URL=https://feedbackmangement.onrender.com/api
VITE_APP_NAME=Feedback Tool
\`\`\`

---

**🎉 Production Ready!** The application now features optimized real-time updates, prevents duplicate data display, eliminates timeout errors, and automatically switches between development and production URLs. Ready for GitHub deployment and live usage!
