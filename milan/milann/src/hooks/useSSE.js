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

    // Use WebSocket for real-time communication
    const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:"
    const wsHost = window.location.hostname
    const wsPort = window.location.hostname === "localhost" ? ":8001" : ""
    const wsUrl = `${wsProtocol}//${wsHost}${wsPort}/ws/sse/${user.id}/?token=${token}`

    try {
      const websocket = new WebSocket(wsUrl)
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

          if (onEvent && data.type !== "heartbeat" && data.type !== "connected") {
            onEvent({ type: data.type, data: data.data || data })
          }
        } catch (err) {
          console.error("WebSocket: Error parsing message:", err)
        }
      }

      websocket.onclose = (event) => {
        console.log("WebSocket: Connection closed", event.code, event.reason)
        setIsConnected(false)
        websocketRef.current = null

        if (event.code !== 1000) {
          // Not a normal closure, attempt to reconnect
          attemptReconnect()
        }
      }

      websocket.onerror = (error) => {
        console.error("WebSocket: Connection error:", error)
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
      console.log("WebSocket: Max reconnection attempts reached")
      setError("Failed to reconnect after multiple attempts")
      return
    }

    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000)
    console.log(`WebSocket: Attempting to reconnect in ${delay}ms (attempt ${reconnectAttempts.current + 1})`)

    reconnectTimeoutRef.current = setTimeout(() => {
      reconnectAttempts.current++
      disconnect()
      connect()
    }, delay)
  }

  useEffect(() => {
    if (user) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [user])

  useEffect(() => {
    return () => {
      disconnect()
    }
  }, [])

  return {
    isConnected,
    error,
    reconnect: () => {
      disconnect()
      setTimeout(connect, 1000)
    },
  }
}
