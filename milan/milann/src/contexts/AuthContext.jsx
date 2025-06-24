"use client"

import { createContext, useContext, useState, useEffect } from "react"
import api from "../utils/api"

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("token")
    if (token) {
      fetchUserProfile()
    } else {
      setLoading(false)
    }
  }, [])

  const fetchUserProfile = async () => {
    try {
      const response = await api.get("/user/profile/")
      setUser(response.data)
    } catch (error) {
      console.error("Failed to fetch user profile:", error)
      logout()
    } finally {
      setLoading(false)
    }
  }

  const login = async (email, password) => {
    try {
      const response = await api.post("/token/", {
        username: email, // Send email as username
        password,
      })

      const { access, refresh, user: userData } = response.data
      localStorage.setItem("token", access)
      localStorage.setItem("refreshToken", refresh)

      if (userData) {
        setUser(userData)
      } else {
        await fetchUserProfile()
      }

      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || "Login failed. Please check your email and password.",
      }
    }
  }

  const logout = () => {
    localStorage.removeItem("token")
    localStorage.removeItem("refreshToken")
    setUser(null)
  }

  const value = {
    user,
    login,
    logout,
    loading,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
