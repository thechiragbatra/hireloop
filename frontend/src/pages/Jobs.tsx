import { useState, useEffect } from "react"
import { Link, useSearchParams } from "react-router-dom"
import { api } from "@/lib/api"
import type { Job } from "@/types"

export const Jobs: React.FC = () => {
  const [searchParams] = useSearchParams()
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const fetchJobs = async (source?: string, query?: string) => {
    setLoading(true)
    setError("")
    try {
      const params: Record<string, string> = {}
      if (source) params.source = source
      if (query) params.query = query
      const res = await api.get("/jobs", { params })
      setJobs(res.data.jobs || [])
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to fetch jobs")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchJobs()
  }, [])

  const handleSelectJob = (job: Job) => {
    const profileId = searchParams.get("profileId") || ""
    if (!profileId) {
      const url = new URL(window.location.href)
      url.searchParams.set("noProfile", "true")
      window.history.pushState({}, "", url)
      return
    }
    window.location.hash = `/match?profileId=${profileId}&jobId=${job.id}`
  }

  const sources = [
    { id: "", label: "All sources" },
    { id: "remoteok", label: "RemoteOK" },
    { id: "greenhouse", label: "Greenhouse" },
    { id: "lever", label: "Lever" },
    { id: "ashby", label: "Ashby" },
    { id: "adzuna", label: "Adzuna" },
  ]

  return (
    <div className="min-h-screen bg-secondary p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center gap-2 mb-6">
          <Link to="/dashboard" className="text-muted-foreground hover:text-primary">
            ← Back to Dashboard
          </Link>
          <h1 className="text-2xl font-bold text-primary">Find Jobs</h1>
        </div>

        {error && (
          <div className="p-3 rounded bg-destructive/10 text-destructive text-sm border border-destructive/20 mb-4">
            {error}
          </div>
        )}

        <div className="bg-card p-6 rounded-xl border shadow-sm mb-6">
          <div className="flex flex-col md:flex-row gap-4 items-end">
            <div className="flex-1">
              <label className="block text-sm font-medium mb-2">Source</label>
              <select
                value={sources.find((s) => s.id === (searchParams.get("source") || ""))?.id || ""}
                onChange={(e) => {
                  const source = e.target.value
                  const url = new URL(window.location.href)
                  url.searchParams.set("source", source)
                  window.history.pushState({}, "", url)
                  fetchJobs(source, searchParams.get("query") || undefined)
                }}
                className="w-full px-3 py-2 rounded border input bg-background"
              >
                {sources.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex-1">
              <label className="block text-sm font-medium mb-2">Search query</label>
              <input
                type="text"
                value={searchParams.get("query") || ""}
                onChange={(e) => {
                  const query = e.target.value
                  const url = new URL(window.location.href)
                  url.searchParams.set("query", query)
                  window.history.pushState({}, "", url)
                  fetchJobs(searchParams.get("source") || undefined, query)
                }}
                className="w-full px-3 py-2 rounded border input bg-background"
                placeholder="e.g. Python, React, Berlin..."
              />
            </div>
            <button
              onClick={() => fetchJobs()}
              className="px-4 py-2 bg-secondary text-sm font-medium rounded hover:bg-accent"
            >
              Refresh
            </button>
          </div>
        </div>

        {loading ? (
          <div className="h-64 flex items-center justify-center">Loading jobs...</div>
        ) : jobs.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-muted-foreground">No jobs found.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {jobs.map((job) => (
              <div
                key={job.id}
                onClick={() => handleSelectJob(job)}
                className="p-4 rounded-lg border border-border hover:bg-accent cursor-pointer transition-colors group"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-primary">{job.title}</h3>
                    <p className="text-sm text-muted-foreground">{job.company}</p>
                    {job.location && (
                      <p className="text-xs text-muted-foreground">📍 {job.location}</p>
                    )}
                  </div>
                  <span className="text-xs font-medium bg-secondary px-2 py-1 rounded text-muted-foreground">
                    {job.source}
                  </span>
                </div>
                <p className="mt-2 text-sm text-muted-foreground line-clamp-2">
                  {job.description}
                </p>
                <div className="mt-3 flex items-center gap-2">
                  <span className="text-xs font-medium text-primary underline underline-offset-4 hover:decoration-primary">
                    View & Match →
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}

        {!searchParams.get("profileId") && (
          <div className="mt-8 p-4 bg-amber-50 rounded-lg border border-amber-200">
            <p className="text-sm text-amber-800">
              Please upload a resume first to see match scores.{" "}
              <Link to="/upload" className="font-medium underline">
                Upload resume
              </Link>
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
