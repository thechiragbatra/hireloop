import { useState, useEffect } from "react"
import { Link, useSearchParams, useNavigate } from "react-router-dom"
import { api } from "@/lib/api"
import type { MatchResult } from "@/types"

export const Match: React.FC = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [match, setMatch] = useState<MatchResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const profileId = searchParams.get("profileId") || ""

  useEffect(() => {
    const loadData = async () => {
      if (!profileId) return
      setLoading(true)
      try {
        const matchRes = await api.post("/match", {
          profile_id: profileId,
          jobs: [],
        })
        setMatch(matchRes.data.matches?.[0] || null)
      } catch (err: any) {
        setError(err.response?.data?.detail || "Failed to load match")
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [profileId])

  const handleTailor = () => {
    const jobId = searchParams.get("jobId") || ""
    navigate(`/tailor?profileId=${profileId}&jobId=${jobId}`)
  }

  return (
    <div className="min-h-screen bg-secondary p-4 md:p-8">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center gap-2 mb-6">
          <Link to="/jobs" className="text-muted-foreground hover:text-primary">
            ← Back to Jobs
          </Link>
          <h1 className="text-2xl font-bold text-primary">Match Details</h1>
        </div>

        {error && (
          <div className="p-3 rounded bg-destructive/10 text-destructive text-sm border border-destructive/20 mb-4">
            {error}
          </div>
        )}

        {!loading && match && (
          <div className="bg-card p-6 rounded-xl border shadow-sm">
            <h2 className="text-lg font-bold text-primary">Match Score</h2>
            <div className="flex items-center gap-4 mb-6">
              <div className="flex-1">
                <p className="text-sm text-muted-foreground">Match quality</p>
              </div>
              <div className="text-right">
                <span className={`px-3 py-1 rounded-full font-semibold text-xs ${
                  match.score >= 70 ? "bg-green-100 text-green-700" : match.score >= 40 ? "bg-amber-100 text-amber-700" : "bg-red-100 text-red-700"
                }`}>
                  {match.score.toFixed(0)}%
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <h3 className="font-medium text-sm mb-2 text-primary">Why this matches</h3>
                <ul className="space-y-2 text-sm">
                  {match.reasons.map((r, i) => (
                    <li key={i} className="flex items-start gap-2 text-muted-foreground">
                      <span className="text-green-500">✓</span>
                      {r}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h3 className="font-medium text-sm mb-2 text-primary">Missing skills</h3>
                <ul className="space-y-2 text-sm">
                  {match.missing_skills.length > 0 ? (
                    match.missing_skills.map((s, i) => (
                      <li key={i} className="flex items-start gap-2 text-muted-foreground">
                        <span className="text-red-500">✗</span>
                        {s}
                      </li>
                    ))
                  ) : (
                    <p className="text-sm text-green-600">No major gaps!</p>
                  )}
                </ul>
              </div>
            </div>

            <div className="flex gap-4">
              <button
                onClick={handleTailor}
                disabled={loading}
                className="flex-1 py-3 px-6 bg-primary text-primary-foreground rounded font-medium disabled:opacity-50"
              >
                Tailor Resume →
              </button>
              <Link to="/tracker" className="flex-1 py-3 px-6 bg-secondary text-sm font-medium rounded text-center hover:bg-accent">
                Back to Tracker
              </Link>
            </div>
          </div>
        )}

        {loading && !error && (
          <div className="h-64 flex items-center justify-center">Loading match...</div>
        )}
      </div>
    </div>
  )
}
