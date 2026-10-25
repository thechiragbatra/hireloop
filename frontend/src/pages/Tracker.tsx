import { useState, useEffect } from "react"
import { Link, useSearchParams } from "react-router-dom"
import { api } from "@/lib/api"
import type { ApplicationRecord } from "@/types"

export const Tracker: React.FC = () => {
  const [searchParams] = useSearchParams()
  const [records, setRecords] = useState<ApplicationRecord[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const statusFilter = searchParams.get("status") || ""

  const fetchRecords = async () => {
    setLoading(true)
    try {
      const params: Record<string, string> = {}
      if (statusFilter) params.status = statusFilter
      const res = await api.get("/tracker", { params })
      setRecords(res.data.items || [])
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load tracker")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRecords()
  }, [statusFilter])

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this application record?")) return
    try {
      await api.delete(`/tracker/${id}`)
      setRecords(records.filter((r) => r.id !== id))
    } catch (err: any) {
      setError(err.response?.data?.detail || "Delete failed")
    }
  }

  const handleUpdateStatus = async (id: string, status: string) => {
    try {
      const record = records.find((r) => r.id === id)
      if (!record) return
      await api.put(`/tracker/${id}`, { ...record, status })
      setRecords(records.map((r) => (r.id === id ? { ...r, status } : r)))
    } catch (err: any) {
      setError(err.response?.data?.detail || "Update failed")
    }
  }

  return (
    <div className="min-h-screen bg-secondary p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center gap-2 mb-6">
          <Link to="/dashboard" className="text-muted-foreground hover:text-primary">
            ← Back to Dashboard
          </Link>
          <h1 className="text-2xl font-bold text-primary">Application Tracker</h1>
        </div>

        {error && (
          <div className="p-3 rounded bg-destructive/10 text-destructive text-sm border border-destructive/20 mb-4">
            {error}
          </div>
        )}

        <div className="bg-card p-6 rounded-xl border shadow-sm mb-6">
          <div className="flex gap-2">
            {["", "saved", "applied", "interview", "offer", "rejected"].map((s) => (
              <button
                key={s}
                onClick={() => {
                  const url = new URL(window.location.href)
                  url.searchParams.set("status", s)
                  window.history.pushState({}, "", url)
                  fetchRecords()
                }}
                className={`px-3 py-1 rounded text-xs font-medium border ${
                  statusFilter === s ? "bg-primary text-primary-foreground border-primary" : "bg-secondary text-muted-foreground border-border hover:bg-accent"
                }`}
              >
                {s || "All"}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="h-64 flex items-center justify-center">Loading applications...</div>
        ) : records.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-muted-foreground">No applications tracked yet.</p>
            <Link to="/jobs" className="text-primary font-medium hover:underline mt-2 inline-block">
              Find jobs →
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b bg-secondary">
                  <th className="px-4 py-3 text-sm font-medium text-muted-foreground">Company</th>
                  <th className="px-4 py-3 text-sm font-medium text-muted-foreground">Role</th>
                  <th className="px-4 py-3 text-sm font-medium text-muted-foreground">Score</th>
                  <th className="px-4 py-3 text-sm font-medium text-muted-foreground">Status</th>
                  <th className="px-4 py-3 text-sm font-medium text-muted-foreground">Date</th>
                  <th className="px-4 py-3 text-sm font-medium text-muted-foreground">Actions</th>
                </tr>
              </thead>
              <tbody>
                {records.map((r) => (
                  <tr key={r.id} className="border-b last:border-0">
                    <td className="px-4 py-3">{r.company}</td>
                    <td className="px-4 py-3">{r.role}</td>
                    <td className="px-4 py-3">{r.match_score.toFixed(0)}%</td>
                    <td className="px-4 py-3">
                      <select
                        value={r.status}
                        onChange={(e) => handleUpdateStatus(r.id, e.target.value)}
                        className="text-sm bg-transparent border-none focus:ring-0"
                      >
                        <option value="saved">Saved</option>
                        <option value="applied">Applied</option>
                        <option value="interview">Interview</option>
                        <option value="offer">Offer</option>
                        <option value="rejected">Rejected</option>
                      </select>
                    </td>
                    <td className="px-4 py-3 text-sm text-muted-foreground">
                      {new Date(r.date).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => handleDelete(r.id)}
                        className="text-xs text-destructive hover:underline"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
