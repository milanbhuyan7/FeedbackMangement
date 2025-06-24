"use client"

import { useEffect, useRef, useState } from "react"
import { useAuth } from "../contexts/AuthContext"

const INACTIVITY_TIMEOUT = 60000 // 60 seconds

export const useSSE = (onEvent) => {
  const { user } = useAuth()
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState(null)
  const websocketRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)
  const inactivityTimeoutRef = useRef(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5
  const isManuallyDisconnected = useRef(false)

  // Use port 8001 for localhost
  const getWsUrl = () => {
    const token = localStorage.getItem("token")
    if (!user || !token) return null
    let wsProtocol, wsHost, wsPort
    if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
      wsProtocol = "ws:"
      wsHost = "localhost"
      wsPort = ":8001"
    } else {
      wsProtocol = "wss:"
      wsHost = "feedbackmangement.onrender.com"
      wsPort = ""
    }
    return `${wsProtocol}//${wsHost}${wsPort}/ws/sse/${user.id}/?token=${token}`
  }

  const connect = () => {
    if (!user || websocketRef.current) return
    const wsUrl = getWsUrl()
    if (!wsUrl) return
    try {
      const websocket = new WebSocket(wsUrl)
      websocketRef.current = websocket
      websocket.onopen = () => {
        setIsConnected(true)
        setError(null)
        reconnectAttempts.current = 0
      }
      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (onEvent && data.type !== "heartbeat" && data.type !== "connected") {
            onEvent({ type: data.type, data: data.data || data })
          }
        } catch {}
      }
      websocket.onclose = (event) => {
        setIsConnected(false)
        websocketRef.current = null
        if (!isManuallyDisconnected.current && event.code !== 1000) {
          attemptReconnect()
        }
      }
      websocket.onerror = () => {
        setIsConnected(false)
        setError("WebSocket connection error")
      }
    } catch (err) {
      setError(err.message)
      attemptReconnect()
    }
  }

  const disconnect = () => {
    isManuallyDisconnected.current = true
    if (websocketRef.current) {
      websocketRef.current.close(1000, "Normal closure")
      websocketRef.current = null
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    setIsConnected(false)
    reconnectAttempts.current = 0
  }

  const attemptReconnect = () => {
    if (reconnectAttempts.current >= maxReconnectAttempts) {
      setError("Failed to reconnect after multiple attempts")
      return
    }
    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000)
    reconnectTimeoutRef.current = setTimeout(() => {
      reconnectAttempts.current++
      disconnect()
      isManuallyDisconnected.current = false
      connect()
    }, delay)
  }

  // Inactivity timer logic
  const resetInactivityTimer = () => {
    if (inactivityTimeoutRef.current) {
      clearTimeout(inactivityTimeoutRef.current)
    }
    inactivityTimeoutRef.current = setTimeout(() => {
      disconnect()
    }, INACTIVITY_TIMEOUT)
    // If not connected, connect on activity
    if (!isConnected && user) {
      isManuallyDisconnected.current = false
      connect()
    }
  }

  // Listen for user activity
  useEffect(() => {
    if (!user) return
    const activityEvents = [
      "mousemove",
      "keydown",
      "click",
      "scroll",
      "touchstart"
    ]
    const handleActivity = resetInactivityTimer
    activityEvents.forEach((event) => window.addEventListener(event, handleActivity))
    // Start timer on mount
    resetInactivityTimer()
    return () => {
      activityEvents.forEach((event) => window.removeEventListener(event, handleActivity))
      if (inactivityTimeoutRef.current) {
        clearTimeout(inactivityTimeoutRef.current)
        inactivityTimeoutRef.current = null
      }
      disconnect()
    }
    // eslint-disable-next-line
  }, [user])

  // Disconnect if user logs out
  useEffect(() => {
    if (!user) {
      disconnect()
    }
    // eslint-disable-next-line
  }, [user])

  return {
    isConnected,
    error,
    resetActivity: resetInactivityTimer,
  }
}
