import { useState } from "react"
import { Link, useSearchParams, useNavigate } from "react-router-dom"
import { api } from "@/lib/api"
import type { TailoredResume, FaithfulnessReport } from "@/types"

export const Tailor: React.FC = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [tailored, setTailored] = useState<TailoredResume | null>(null)
  const [faithfulness, setFaithfulness] = useState<FaithfulnessReport | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const profileId = searchParams.get("profileId") || ""
  const jobId = searchParams.get("jobId") || ""

  const handleTailor = async () => {
    if (!profileId || !jobId) return
    setLoading(true)
    setError("")
    try {
      const res = await api.post(`/tailor?profile_id=${profileId}&job_id=${jobId}`)
      setTailored(res.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || "Tailoring failed")
    } finally {
      setLoading(false)
    }
  }

  const handleVerify = async () => {
    if (!tailored || !profileId) return
    try {
      const res = await api.post("/verify", {
        profile_id: profileId,
        tailored: tailored,
      })
      setFaithfulness(res.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || "Verification failed")
    }
  }

  const handleApplyKit = () => {
    navigate(`/apply-kit/${profileId}/${jobId}`)
  }

  return (
    <div className="min-h-screen bg-secondary p-4 md:p-8">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center gap-2 mb-6">
          <Link to="/jobs" className="text-muted-foreground hover:text-primary">
            ← Back to Jobs
          </Link>
          <h1 className="text-2xl font-bold text-primary">Tailor Resume</h1>
        </div>

        {error && (
          <div className="p-3 rounded bg-destructive/10 text-destructive text-sm border border-destructive/20 mb-4">
            {error}
          </div>
        )}

        {!profileId || !jobId ? (
          <div className="text-center py-20">
            <p className="text-muted-foreground">Please select a profile and job first.</p>
            <Link to="/jobs" className="text-primary font-medium hover:underline mt-2 inline-block">
              Find jobs →
            </Link>
          </div>
        ) : (
          <>
            <div className="bg-card p-6 rounded-xl border shadow-sm mb-6">
              <div className="flex justify-between items-center mb-4">
                <div>
                  <h2 className="text-lg font-bold">Profile</h2>
                  <p className="text-sm text-muted-foreground">{profileId}</p>
                </div>
                <div>
                  <h2 className="text-lg font-bold">Job</h2>
                  <p className="text-sm text-muted-foreground">{jobId}</p>
                </div>
              </div>
              <button
                onClick={handleTailor}
                disabled={loading}
                className="w-full py-3 px-4 bg-primary text-primary-foreground rounded font-medium disabled:opacity-50"
              >
                {loading ? "Tailoring..." : "Generate Tailored Resume"}
              </button>
            </div>

            {tailored && (
              <div className="bg-card p-6 rounded-xl border shadow-sm mb-6">
                <h2 className="text-lg font-bold mb-4">Tailored Resume</h2>
                {tailored.summary && (
                  <div className="mb-4">
                    <p className="text-sm font-medium text-muted-foreground">Summary</p>
                    <p className="text-sm">{tailored.summary}</p>
                  </div>
                )}
                <div className="space-y-3">
                  {tailored.bullets.map((b, i) => (
                    <div key={i} className="p-3 rounded border border-border bg-muted/50">
                      <p className="text-sm">{b.text}</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        Sources: {b.source_ids.join(", ")}
                      </p>
                    </div>
                  ))}
                </div>
                <div className="mt-4 flex gap-3">
                  <button
                    onClick={handleVerify}
                    disabled={!!faithfulness}
                    className="flex-1 py-2 px-4 bg-secondary text-sm font-medium rounded hover:bg-accent"
                  >
                    Verify Faithfulness
                  </button>
                  <button
                    onClick={handleApplyKit}
                    className="flex-1 py-2 px-4 bg-primary text-primary-foreground rounded font-medium hover:bg-primary/90"
                  >
                    Generate Apply Kit →
                  </button>
                </div>
              </div>
            )}

            {faithfulness && (
              <div className="bg-card p-6 rounded-xl border shadow-sm mb-6">
                <h2 className="text-lg font-bold mb-4">Faithfulness Report</h2>
                <div className="flex items-center gap-6 mb-4">
                  <div className="text-right">
                    <div className="text-2xl font-bold text-primary">
                      {(faithfulness.overall_score * 100).toFixed(0)}%
                    </div>
                    <div className="text-xs text-muted-foreground">Faithfulness Score</div>
                  </div>
                  <div className="text-sm">
                    <p>{faithfulness.supported_bullets}/{faithfulness.total_bullets} bullets supported</p>
                  </div>
                </div>
                {faithfulness.unsupported.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-destructive mb-2">Unsupported claims:</p>
                    <ul className="space-y-1 text-sm text-destructive/80">
                      {faithfulness.unsupported.map((u, i) => (
                        <li key={i} className="pl-4 list-disc">{u}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
