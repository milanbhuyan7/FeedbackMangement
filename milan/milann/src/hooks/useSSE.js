"use client"

import { useEffect, useRef, useState } from "react"
import { useAuth } from "../contexts/AuthContext"

export const useSSE = (onEvent) => {
  const { user } = useAuth()
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState(null)
  const websocketRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5

  const connect = () => {
    if (!user || websocketRef.current) return

    const token = localStorage.getItem("token")
    if (!token) return

    // Convert HTTP URL to WebSocket URL
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api"
    const wsBaseUrl = apiBaseUrl.replace(/^https?:\/\//, '').replace('/api', '')
    const protocol = apiBaseUrl.startsWith('https') ? 'wss' : 'ws'
    const url = `${protocol}://${wsBaseUrl}/ws/sse/${user.id}/?token=${encodeURIComponent(token)}`

    try {
      console.log("WebSocket: Connecting to", url)
      const websocket = new WebSocket(url)
      websocketRef.current = websocket

      websocket.onopen = () => {
        console.log("WebSocket: Connection opened")
        setIsConnected(true)
        setError(null)
        reconnectAttempts.current = 0
      }

      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          console.log("WebSocket: Received message:", data)

          // Handle different message types
          if (data.type) {
            // Handle typed messages (new_feedback, feedback_updated, etc.)
            if (onEvent) {
              onEvent(data)
            }
          } else if (data.event) {
            // Handle event-based messages
            const eventData = {
              type: data.event,
              data: data.data || data
            }
            console.log(`WebSocket: ${data.event} received:`, eventData)
            if (onEvent) {
              onEvent(eventData)
            }
          } else {
            // Handle generic messages
            if (onEvent) {
              onEvent(data)
            }
          }
        } catch (err) {
          console.error("WebSocket: Error parsing message:", err)
        }
      }

      websocket.onclose = (event) => {
        console.log("WebSocket: Connection closed", event.code, event.reason)
        setIsConnected(false)
        websocketRef.current = null

        // Only attempt reconnect if it wasn't a clean close
        if (event.code !== 1000) {
          attemptReconnect()
        }
      }

      websocket.onerror = (event) => {
        console.error("WebSocket: Connection error:", event)
        setIsConnected(false)
        setError("WebSocket connection error")
      }

    } catch (err) {
      console.error("WebSocket: Failed to create connection:", err)
      setError(err.message)
      attemptReconnect()
    }
  }

  const disconnect = () => {
    if (websocketRef.current) {
      websocketRef.current.close(1000, "Client disconnect")
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
      console.log("WebSocket: Max reconnection attempts reached")
      setError("Failed to reconnect after multiple attempts")
      return
    }

    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000) // Exponential backoff, max 30s
    console.log(`WebSocket: Attempting to reconnect in ${delay}ms (attempt ${reconnectAttempts.current + 1})`)

    reconnectTimeoutRef.current = setTimeout(() => {
      reconnectAttempts.current++
      disconnect()
      connect()
    }, delay)
  }

  const sendMessage = (message) => {
    if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
      websocketRef.current.send(JSON.stringify(message))
    } else {
      console.warn("WebSocket: Cannot send message, connection not open")
    }
  }

  useEffect(() => {
    if (user) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [user])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect()
    }
  }, [])

  return {
    isConnected,
    error,
    sendMessage,
    reconnect: () => {
      disconnect()
      setTimeout(connect, 1000)
    },
  }
}