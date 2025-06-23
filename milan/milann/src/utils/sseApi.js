// Alternative SSE implementation using fetch with custom headers
export class SSEClient {
  constructor(url, options = {}) {
    this.url = url
    this.options = options
    this.controller = null
    this.eventListeners = new Map()
    this.isConnected = false
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
  }

  addEventListener(eventType, callback) {
    if (!this.eventListeners.has(eventType)) {
      this.eventListeners.set(eventType, [])
    }
    this.eventListeners.get(eventType).push(callback)
  }

  removeEventListener(eventType, callback) {
    if (this.eventListeners.has(eventType)) {
      const callbacks = this.eventListeners.get(eventType)
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  emit(eventType, data) {
    if (this.eventListeners.has(eventType)) {
      this.eventListeners.get(eventType).forEach((callback) => {
        try {
          callback(data)
        } catch (error) {
          console.error(`Error in SSE event listener for ${eventType}:`, error)
        }
      })
    }
  }

  async connect() {
    if (this.controller) {
      this.disconnect()
    }

    this.controller = new AbortController()

    try {
      const token = localStorage.getItem("token")
      if (!token) {
        throw new Error("No authentication token found")
      }

      const response = await fetch(this.url, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: "text/event-stream",
          "Cache-Control": "no-cache",
        },
        signal: this.controller.signal,
        ...this.options,
      })

      if (!response.ok) {
        throw new Error(`SSE connection failed: ${response.status} ${response.statusText}`)
      }

      this.isConnected = true
      this.reconnectAttempts = 0
      this.emit("open", { type: "connection_opened" })

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ""

      while (true) {
        const { done, value } = await reader.read()

        if (done) {
          console.log("SSE: Stream ended")
          break
        }

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split("\n")
        buffer = lines.pop() || "" // Keep incomplete line in buffer

        let eventType = "message"
        let eventData = ""

        for (const line of lines) {
          if (line.startsWith("event:")) {
            eventType = line.substring(6).trim()
          } else if (line.startsWith("data:")) {
            eventData = line.substring(5).trim()
          } else if (line === "") {
            // Empty line indicates end of event
            if (eventData) {
              try {
                const parsedData = JSON.parse(eventData)
                this.emit(eventType, { type: eventType, data: parsedData })
                this.emit("message", { type: eventType, data: parsedData })
              } catch (error) {
                console.error("Error parsing SSE data:", error)
              }
            }
            eventType = "message"
            eventData = ""
          }
        }
      }
    } catch (error) {
      if (error.name === "AbortError") {
        console.log("SSE: Connection aborted")
        return
      }

      console.error("SSE: Connection error:", error)
      this.isConnected = false
      this.emit("error", { type: "error", error: error.message })

      // Attempt reconnection
      this.attemptReconnect()
    }
  }

  disconnect() {
    if (this.controller) {
      this.controller.abort()
      this.controller = null
    }
    this.isConnected = false
    this.emit("close", { type: "connection_closed" })
  }

  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log("SSE: Max reconnection attempts reached")
      this.emit("error", { type: "max_reconnect_attempts", error: "Failed to reconnect" })
      return
    }

    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000)
    console.log(`SSE: Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts + 1})`)

    setTimeout(() => {
      this.reconnectAttempts++
      this.connect()
    }, delay)
  }
}

export const createSSEConnection = (baseUrl) => {
  const url = `${baseUrl}/sse/`
  return new SSEClient(url)
}
