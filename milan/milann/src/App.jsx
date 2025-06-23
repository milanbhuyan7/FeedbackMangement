"use client"
import Login from "./components/Login"
import ManagerDashboard from "./components/ManagerDashboard"
import EmployeeDashboard from "./components/EmployeeDashboard"

// Add at the top after imports:
const APP_NAME = import.meta.env.VITE_APP_NAME || "Feedback Tool"
const APP_VERSION = import.meta.env.VITE_APP_VERSION || "1.0.0"

// Update the main App component to use AuthProvider and routing:
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import { AuthProvider, useAuth } from "./contexts/AuthContext"

// Mock user data for preview
const mockUsers = {
  manager: {
    id: 1,
    username: "manager",
    first_name: "John",
    last_name: "Manager",
    email: "manager@company.com",
    is_manager: true,
  },
  employee: {
    id: 2,
    username: "employee",
    first_name: "Jane",
    last_name: "Employee",
    email: "employee@company.com",
    is_manager: false,
  },
}

// Mock team data
const mockTeam = [
  {
    id: 2,
    username: "employee",
    first_name: "Jane",
    last_name: "Employee",
    email: "employee@company.com",
    is_manager: false,
  },
  {
    id: 3,
    username: "employee2",
    first_name: "Bob",
    last_name: "Smith",
    email: "bob@company.com",
    is_manager: false,
  },
]

// Mock feedback data
const mockFeedbacks = [
  {
    id: 1,
    employee: mockTeam[0],
    manager: mockUsers.manager,
    strengths: "Excellent communication skills and always meets deadlines. Shows great initiative in problem-solving.",
    areas_to_improve: "Could benefit from learning more advanced technical skills and taking on leadership roles.",
    sentiment: "positive",
    acknowledged: false,
    created_at: "2024-01-15T10:30:00Z",
    acknowledged_at: null,
  },
  {
    id: 2,
    employee: mockTeam[1],
    manager: mockUsers.manager,
    strengths: "Very reliable and detail-oriented. Great team player who helps others.",
    areas_to_improve: "Needs to work on time management and prioritizing tasks more effectively.",
    sentiment: "neutral",
    acknowledged: true,
    created_at: "2024-01-10T14:20:00Z",
    acknowledged_at: "2024-01-11T09:15:00Z",
  },
]

// Protected Route Component
const ProtectedRoute = ({ children, requiredRole = null }) => {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p>Loading...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (requiredRole && user.is_manager !== (requiredRole === "manager")) {
    return <Navigate to={user.is_manager ? "/manager" : "/employee"} replace />
  }

  return children
}

// Main App Routes
const AppRoutes = () => {
  const { user } = useAuth()

  return (
    <Routes>
      <Route
        path="/login"
        element={user ? <Navigate to={user.is_manager ? "/manager" : "/employee"} replace /> : <Login />}
      />
      <Route
        path="/manager"
        element={
          <ProtectedRoute requiredRole="manager">
            <ManagerDashboard user={mockUsers.manager} team={mockTeam} feedbacks={mockFeedbacks} />
          </ProtectedRoute>
        }
      />
      <Route
        path="/employee"
        element={
          <ProtectedRoute requiredRole="employee">
            <EmployeeDashboard
              user={mockUsers.employee}
              feedbacks={mockFeedbacks.filter((f) => f.employee.id === mockUsers.employee?.id)}
            />
          </ProtectedRoute>
        }
      />
      <Route
        path="/"
        element={
          user ? <Navigate to={user.is_manager ? "/manager" : "/employee"} replace /> : <Navigate to="/login" replace />
        }
      />
    </Routes>
  )
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <AppRoutes />
        </div>
      </Router>
    </AuthProvider>
  )
}

export default App
