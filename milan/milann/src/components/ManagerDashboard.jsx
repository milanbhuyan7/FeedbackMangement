"use client"

import { useState, useEffect, useCallback } from "react"
import { useAuth } from "../contexts/AuthContext"
import { useSSE } from "../hooks/useSSE"
import api from "../utils/api"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { LogOut, Users, MessageSquare, TrendingUp, Plus, Edit, Trash2, Wifi, WifiOff } from "lucide-react"

const ManagerDashboard = () => {
  const { user, logout } = useAuth()
  const [team, setTeam] = useState([])
  const [feedbacks, setFeedbacks] = useState([])
  const [loading, setLoading] = useState(true)
  const [showFeedbackForm, setShowFeedbackForm] = useState(false)
  const [editingFeedback, setEditingFeedback] = useState(null)
  const [formData, setFormData] = useState({
    employee_id: "",
    strengths: "",
    areas_to_improve: "",
    sentiment: "neutral",
  })
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  // SSE event handler
  const handleSSEEvent = useCallback((event) => {
    console.log("Manager Dashboard - SSE Event:", event)

    switch (event.type) {
      case "feedback_created":
        // Add new feedback to the list
        setFeedbacks((prev) => {
          if (!Array.isArray(prev)) {
            console.warn("Previous feedbacks is not an array, resetting to empty array")
            return event.data ? [event.data] : []
          }
          return event.data ? [event.data, ...prev] : prev
        })
        setSuccess("New feedback submitted successfully!")
        setTimeout(() => setSuccess(""), 3000)
        break

      case "feedback_updated":
        // Update existing feedback
        setFeedbacks((prev) => {
          if (!Array.isArray(prev)) {
            console.warn("Previous feedbacks is not an array, resetting to empty array")
            return event.data ? [event.data] : []
          }
          return prev.map((feedback) => (feedback.id === event.data.id ? event.data : feedback))
        })
        setSuccess("Feedback updated successfully!")
        setTimeout(() => setSuccess(""), 3000)
        break

      case "feedback_deleted":
        // Remove deleted feedback
        setFeedbacks((prev) => {
          if (!Array.isArray(prev)) {
            console.warn("Previous feedbacks is not an array, resetting to empty array")
            return []
          }
          return prev.filter((feedback) => feedback.id !== event.data.id)
        })
        setSuccess("Feedback deleted successfully!")
        setTimeout(() => setSuccess(""), 3000)
        break

      case "feedback_acknowledged":
        // Update acknowledgment status
        setFeedbacks((prev) => {
          if (!Array.isArray(prev)) {
            console.warn("Previous feedbacks is not an array, resetting to empty array")
            return event.data ? [event.data] : []
          }
          return prev.map((feedback) => (feedback.id === event.data.id ? event.data : feedback))
        })
        setSuccess(`Feedback acknowledged by ${event.data.employee?.first_name || 'User'}!`)
        setTimeout(() => setSuccess(""), 3000)
        break

      default:
        console.log("Unhandled SSE event type:", event.type)
    }
  }, [])

  // Initialize SSE connection
  const { isConnected: sseConnected, error: sseError } = useSSE(handleSSEEvent)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [teamResponse, feedbackResponse] = await Promise.all([api.get("/team/"), api.get("/feedbacks/")])
      setTeam(Array.isArray(teamResponse.data) ? teamResponse.data : [])

      // Handle paginated response for feedbacks
      const feedbackData = feedbackResponse.data
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
      setError("Failed to fetch data: " + (error.response?.data?.detail || error.message))
      // Ensure arrays are set even on error
      setTeam([])
      setFeedbacks([])
    } finally {
      setLoading(false)
    }
  }

  const handleSubmitFeedback = async (e) => {
    e.preventDefault()
    setError("")
    setSuccess("")

    try {
      if (editingFeedback) {
        await api.put(`/feedbacks/${editingFeedback.id}/`, formData)
        // SSE will handle the update notification
      } else {
        await api.post("/feedbacks/", formData)
        // SSE will handle the creation notification
      }

      setFormData({
        employee_id: "",
        strengths: "",
        areas_to_improve: "",
        sentiment: "neutral",
      })
      setShowFeedbackForm(false)
      setEditingFeedback(null)
    } catch (error) {
      setError(error.response?.data?.detail || error.response?.data?.employee_id?.[0] || "Failed to submit feedback")
    }
  }

  const handleEditFeedback = (feedback) => {
    setEditingFeedback(feedback)
    setFormData({
      employee_id: feedback.employee.id.toString(),
      strengths: feedback.strengths,
      areas_to_improve: feedback.areas_to_improve,
      sentiment: feedback.sentiment,
    })
    setShowFeedbackForm(true)
  }

  const handleDeleteFeedback = async (feedbackId) => {
    if (window.confirm("Are you sure you want to delete this feedback?")) {
      try {
        await api.delete(`/feedbacks/${feedbackId}/`)
        // SSE will handle the deletion notification
      } catch (error) {
        setError("Failed to delete feedback")
      }
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

  const getSentimentStats = () => {
    // Ensure feedbacks is an array before using reduce
    if (!Array.isArray(feedbacks)) {
      console.warn("feedbacks is not an array:", feedbacks)
      return {}
    }

    const stats = feedbacks.reduce((acc, feedback) => {
      acc[feedback.sentiment] = (acc[feedback.sentiment] || 0) + 1
      return acc
    }, {})
    return stats
  }

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>
  }

  const stats = getSentimentStats()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Manager Dashboard</h1>
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

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="team">Team</TabsTrigger>
            <TabsTrigger value="feedback">Feedback</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Team Members</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{team.length}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Feedback</CardTitle>
                  <MessageSquare className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{Array.isArray(feedbacks) ? feedbacks.length : 0}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Positive Feedback</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">{stats.positive || 0}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Acknowledged</CardTitle>
                  <MessageSquare className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{Array.isArray(feedbacks) ? feedbacks.filter((f) => f.acknowledged).length : 0}</div>
                </CardContent>
              </Card>
            </div>

            {/* Recent Feedback */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Feedback</CardTitle>
                <CardDescription>Latest feedback submissions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Array.isArray(feedbacks) ? feedbacks.slice(0, 5).map((feedback) => (
                    <div key={feedback.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex-1">
                        <p className="font-medium">
                          {feedback.employee.first_name} {feedback.employee.last_name}
                        </p>
                        <p className="text-sm text-gray-600 truncate">{feedback.strengths}</p>
                        <p className="text-xs text-gray-500">{new Date(feedback.created_at).toLocaleDateString()}</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={getSentimentColor(feedback.sentiment)}>{feedback.sentiment}</Badge>
                        {feedback.acknowledged && <Badge variant="outline">Acknowledged</Badge>}
                      </div>
                    </div>
                  )) : (
                    <p className="text-gray-500 text-center py-4">No feedback available</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="team" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Team Members</CardTitle>
                <CardDescription>Manage your team and their feedback</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {team.map((member) => {
                    const memberFeedbacks = Array.isArray(feedbacks) ? feedbacks.filter((f) => f.employee.id === member.id) : []
                    return (
                      <Card key={member.id}>
                        <CardContent className="p-4">
                          <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                              <span className="text-blue-600 font-medium">
                                {member.first_name?.[0] || member.username[0]}
                              </span>
                            </div>
                            <div className="flex-1">
                              <p className="font-medium">
                                {member.first_name} {member.last_name}
                              </p>
                              <p className="text-sm text-gray-600">{member.email}</p>
                            </div>
                          </div>
                          <div className="mt-4 flex justify-between text-sm">
                            <span>Feedback: {memberFeedbacks.length}</span>
                            <span>Acknowledged: {memberFeedbacks.filter((f) => f.acknowledged).length}</span>
                          </div>
                        </CardContent>
                      </Card>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="feedback" className="space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-xl font-semibold">Feedback Management</h2>
                <p className="text-gray-600">Submit and manage feedback for your team</p>
              </div>
              <Button onClick={() => setShowFeedbackForm(true)}>
                <Plus className="h-4 w-4 mr-2" />
                New Feedback
              </Button>
            </div>

            {showFeedbackForm && (
              <Card>
                <CardHeader>
                  <CardTitle>{editingFeedback ? "Edit Feedback" : "Submit New Feedback"}</CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmitFeedback} className="space-y-4">
                    <div>
                      <Label htmlFor="employee">Employee</Label>
                      <Select
                        value={formData.employee_id}
                        onValueChange={(value) => setFormData({ ...formData, employee_id: value })}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select an employee" />
                        </SelectTrigger>
                        <SelectContent>
                          {team.map((member) => (
                            <SelectItem key={member.id} value={member.id.toString()}>
                              {member.first_name} {member.last_name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label htmlFor="strengths">Strengths</Label>
                      <Textarea
                        id="strengths"
                        placeholder="What are this employee's strengths?"
                        value={formData.strengths}
                        onChange={(e) => setFormData({ ...formData, strengths: e.target.value })}
                        required
                      />
                    </div>

                    <div>
                      <Label htmlFor="areas_to_improve">Areas to Improve</Label>
                      <Textarea
                        id="areas_to_improve"
                        placeholder="What areas could this employee improve on?"
                        value={formData.areas_to_improve}
                        onChange={(e) => setFormData({ ...formData, areas_to_improve: e.target.value })}
                        required
                      />
                    </div>

                    <div>
                      <Label htmlFor="sentiment">Overall Sentiment</Label>
                      <Select
                        value={formData.sentiment}
                        onValueChange={(value) => setFormData({ ...formData, sentiment: value })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="positive">Positive</SelectItem>
                          <SelectItem value="neutral">Neutral</SelectItem>
                          <SelectItem value="negative">Negative</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="flex space-x-2">
                      <Button type="submit">{editingFeedback ? "Update Feedback" : "Submit Feedback"}</Button>
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => {
                          setShowFeedbackForm(false)
                          setEditingFeedback(null)
                          setFormData({
                            employee_id: "",
                            strengths: "",
                            areas_to_improve: "",
                            sentiment: "neutral",
                          })
                        }}
                      >
                        Cancel
                      </Button>
                    </div>
                  </form>
                </CardContent>
              </Card>
            )}

            {/* Feedback List */}
            <Card>
              <CardHeader>
                <CardTitle>All Feedback</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Array.isArray(feedbacks) ? feedbacks.map((feedback) => (
                    <div key={feedback.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h4 className="font-medium">
                            {feedback.employee.first_name} {feedback.employee.last_name}
                          </h4>
                          <p className="text-sm text-gray-600">{new Date(feedback.created_at).toLocaleDateString()}</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className={getSentimentColor(feedback.sentiment)}>{feedback.sentiment}</Badge>
                          {feedback.acknowledged && <Badge variant="outline">Acknowledged</Badge>}
                          <Button size="sm" variant="outline" onClick={() => handleEditFeedback(feedback)}>
                            <Edit className="h-3 w-3" />
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => handleDeleteFeedback(feedback.id)}>
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <div>
                          <p className="text-sm font-medium text-green-700">Strengths:</p>
                          <p className="text-sm">{feedback.strengths}</p>
                        </div>
                        <div>
                          <p className="text-sm font-medium text-orange-700">Areas to Improve:</p>
                          <p className="text-sm">{feedback.areas_to_improve}</p>
                        </div>
                      </div>
                    </div>
                  )) : (
                    <p className="text-gray-500 text-center py-4">No feedback available</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default ManagerDashboard
