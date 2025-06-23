"use client"

import { useState, useEffect, useCallback } from "react"
import { useAuth } from "../contexts/AuthContext"
import { useSSE } from "../hooks/useSSE"
import api from "../utils/api"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { LogOut, MessageSquare, CheckCircle, Clock, TrendingUp, Wifi, WifiOff } from "lucide-react"

const EmployeeDashboard = () => {
  const { user, logout } = useAuth()
  const [feedbacks, setFeedbacks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  // SSE event handler
  const handleSSEEvent = useCallback((event) => {
    console.log("Employee Dashboard - SSE Event:", event)

    switch (event.type) {
      case "new_feedback":
        // Add new feedback to the list
        setFeedbacks((prev) => {
          const prevArray = Array.isArray(prev) ? prev : []
          return [event.data, ...prevArray]
        })
        setSuccess("You have received new feedback!")
        setTimeout(() => setSuccess(""), 5000)
        break

      case "feedback_updated":
        // Update existing feedback
        setFeedbacks((prev) => {
          const prevArray = Array.isArray(prev) ? prev : []
          return prevArray.map((feedback) => (feedback.id === event.data.id ? event.data : feedback))
        })
        setSuccess("Your feedback has been updated!")
        setTimeout(() => setSuccess(""), 3000)
        break

      case "feedback_deleted":
        // Remove deleted feedback
        setFeedbacks((prev) => {
          const prevArray = Array.isArray(prev) ? prev : []
          return prevArray.filter((feedback) => feedback.id !== event.data.id)
        })
        setSuccess("A feedback has been removed!")
        setTimeout(() => setSuccess(""), 3000)
        break

      case "feedback_acknowledged":
        // Update acknowledgment status (this should be from our own action)
        setFeedbacks((prev) => {
          const prevArray = Array.isArray(prev) ? prev : []
          return prevArray.map((feedback) => (feedback.id === event.data.id ? event.data : feedback))
        })
        break

      default:
        console.log("Unhandled SSE event type:", event.type)
    }
  }, [])

  // Initialize SSE connection
  const { isConnected: sseConnected, error: sseError } = useSSE(handleSSEEvent)

  useEffect(() => {
    fetchFeedbacks()
  }, [])

  const fetchFeedbacks = async () => {
    try {
      const response = await api.get("/feedbacks/")

      // Handle paginated response for feedbacks
      const feedbackData = response.data
      if (feedbackData && feedbackData.results && Array.isArray(feedbackData.results)) {
        // Paginated response
        setFeedbacks(feedbackData.results)
      } else if (Array.isArray(feedbackData)) {
        // Direct array response
        setFeedbacks(feedbackData)
      } else {
        // Fallback to empty array
        setFeedbacks([])
      }
    } catch (error) {
      setError("Failed to fetch feedback: " + (error.response?.data?.detail || error.message))
      // Set empty array on error
      setFeedbacks([])
    } finally {
      setLoading(false)
    }
  }

  const handleAcknowledge = async (feedbackId) => {
    try {
      await api.post(`/feedbacks/${feedbackId}/acknowledge/`)
      // SSE will handle the update notification
      setSuccess("Feedback acknowledged successfully!")
      setTimeout(() => setSuccess(""), 3000)
    } catch (error) {
      setError("Failed to acknowledge feedback: " + (error.response?.data?.detail || error.message))
    }
  }

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case "positive":
        return "bg-green-100 text-green-800"
      case "negative":
        return "bg-red-100 text-red-800"
      default:
        return "bg-yellow-100 text-yellow-800"
    }
  }

  const getSentimentIcon = (sentiment) => {
    switch (sentiment) {
      case "positive":
        return "😊"
      case "negative":
        return "😔"
      default:
        return "😐"
    }
  }

  const getStats = () => {
    // Ensure feedbacks is always an array
    const feedbacksArray = Array.isArray(feedbacks) ? feedbacks : []
    const total = feedbacksArray.length
    const acknowledged = feedbacksArray.filter((f) => f.acknowledged).length
    const unacknowledged = total - acknowledged
    const sentimentCounts = feedbacksArray.reduce((acc, feedback) => {
      acc[feedback.sentiment] = (acc[feedback.sentiment] || 0) + 1
      return acc
    }, {})

    return { total, acknowledged, unacknowledged, sentimentCounts }
  }

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>
  }

  const stats = getStats()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Employee Dashboard</h1>
              <p className="text-gray-600">Welcome back, {user?.first_name || user?.username}</p>
            </div>
            <div className="flex items-center space-x-4">
              {/* SSE Connection Status */}
              <div className="flex items-center space-x-2">
                {sseConnected ? (
                  <div className="flex items-center text-green-600">
                    <Wifi className="h-4 w-4 mr-1" />
                    <span className="text-sm">Live</span>
                  </div>
                ) : (
                  <div className="flex items-center text-red-600">
                    <WifiOff className="h-4 w-4 mr-1" />
                    <span className="text-sm">Offline</span>
                  </div>
                )}
              </div>
              <Button onClick={logout} variant="outline">
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="mb-6 border-green-200 bg-green-50">
            <AlertDescription className="text-green-800">{success}</AlertDescription>
          </Alert>
        )}

        {sseError && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>Real-time connection error: {sseError}</AlertDescription>
          </Alert>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Feedback</CardTitle>
              <MessageSquare className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Acknowledged</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats.acknowledged}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pending</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">{stats.unacknowledged}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Positive Feedback</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats.sentimentCounts.positive || 0}</div>
            </CardContent>
          </Card>
        </div>

        {/* Feedback Timeline */}
        <Card>
          <CardHeader>
            <CardTitle>Feedback Timeline</CardTitle>
            <CardDescription>Your feedback history from managers</CardDescription>
          </CardHeader>
          <CardContent>
            {!Array.isArray(feedbacks) || feedbacks.length === 0 ? (
              <div className="text-center py-8">
                <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No feedback received yet</p>
              </div>
            ) : (
              <div className="space-y-6">
                {feedbacks.map((feedback, index) => (
                  <div key={feedback.id} className="relative">
                    {/* Timeline line */}
                    {index !== feedbacks.length - 1 && (
                      <div className="absolute left-6 top-12 w-0.5 h-full bg-gray-200"></div>
                    )}

                    <div className="flex items-start space-x-4">
                      {/* Timeline dot */}
                      <div
                        className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center text-lg ${feedback.acknowledged ? "bg-green-100" : "bg-blue-100"
                          }`}
                      >
                        {getSentimentIcon(feedback.sentiment)}
                      </div>

                      {/* Feedback content */}
                      <div className="flex-1 min-w-0">
                        <Card className={`${!feedback.acknowledged ? "ring-2 ring-blue-200" : ""}`}>
                          <CardHeader className="pb-3">
                            <div className="flex justify-between items-start">
                              <div>
                                <CardTitle className="text-lg">
                                  Feedback from {feedback.manager.first_name} {feedback.manager.last_name}
                                </CardTitle>
                                <CardDescription>
                                  {new Date(feedback.created_at).toLocaleDateString("en-US", {
                                    year: "numeric",
                                    month: "long",
                                    day: "numeric",
                                    hour: "2-digit",
                                    minute: "2-digit",
                                  })}
                                </CardDescription>
                              </div>
                              <div className="flex items-center space-x-2">
                                <Badge className={getSentimentColor(feedback.sentiment)}>{feedback.sentiment}</Badge>
                                {feedback.acknowledged && (
                                  <Badge variant="outline" className="text-green-600 border-green-200">
                                    <CheckCircle className="h-3 w-3 mr-1" />
                                    Acknowledged
                                  </Badge>
                                )}
                              </div>
                            </div>
                          </CardHeader>

                          <CardContent className="space-y-4">
                            <div className="grid md:grid-cols-2 gap-4">
                              <div className="space-y-2">
                                <h4 className="font-medium text-green-700 flex items-center">
                                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                                  Strengths
                                </h4>
                                <p className="text-sm text-gray-700 bg-green-50 p-3 rounded-lg">{feedback.strengths}</p>
                              </div>

                              <div className="space-y-2">
                                <h4 className="font-medium text-orange-700 flex items-center">
                                  <span className="w-2 h-2 bg-orange-500 rounded-full mr-2"></span>
                                  Areas to Improve
                                </h4>
                                <p className="text-sm text-gray-700 bg-orange-50 p-3 rounded-lg">
                                  {feedback.areas_to_improve}
                                </p>
                              </div>
                            </div>

                            {!feedback.acknowledged && (
                              <div className="pt-4 border-t">
                                <Button onClick={() => handleAcknowledge(feedback.id)} className="w-full sm:w-auto">
                                  <CheckCircle className="h-4 w-4 mr-2" />
                                  Acknowledge Feedback
                                </Button>
                              </div>
                            )}

                            {feedback.acknowledged && (
                              <div className="pt-4 border-t">
                                <p className="text-sm text-green-600 flex items-center">
                                  <CheckCircle className="h-4 w-4 mr-2" />
                                  Acknowledged on {new Date(feedback.acknowledged_at).toLocaleDateString()}
                                </p>
                              </div>
                            )}
                          </CardContent>
                        </Card>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default EmployeeDashboard
