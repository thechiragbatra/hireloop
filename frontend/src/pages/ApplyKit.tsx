import { useState, useEffect } from "react"
import { Link, useParams } from "react-router-dom"
import { api } from "@/lib/api"
import type { ApplyKit as ApplyKitType } from "@/types"

export const ApplyKit: React.FC = () => {
  const { profileId, jobId } = useParams()
  const [kit, setKit] = useState<ApplyKitType | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    const loadKit = async () => {
      if (!profileId || !jobId) return
      setLoading(true)
      try {
        const res = await api.get(`/apply-kit/${profileId}/${jobId}`)
        setKit(res.data)
      } catch (err: any) {
        setError(err.response?.data?.detail || "Failed to load apply kit")
      } finally {
        setLoading(false)
      }
    }
    loadKit()
  }, [profileId, jobId])

  const handleDownload = (content: string, filename: string) => {
    const blob = new Blob([content], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="min-h-screen bg-secondary p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-2 mb-6">
          <Link to="/dashboard" className="text-muted-foreground hover:text-primary">
            ← Back to Dashboard
          </Link>
          <h1 className="text-2xl font-bold text-primary">Apply Kit</h1>
        </div>

        {error && (
          <div className="p-3 rounded bg-destructive/10 text-destructive text-sm border border-destructive/20 mb-4">
            {error}
          </div>
        )}

        {loading ? (
          <div className="h-64 flex items-center justify-center">Generating apply kit...</div>
        ) : kit ? (
          <div className="space-y-6">
            <div className="bg-card p-6 rounded-xl border shadow-sm">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="text-lg font-bold">Job {kit.job_id}</h2>
                  <p className="text-sm text-muted-foreground">Profile {kit.profile_id}</p>
                </div>
                <p className="text-xs text-muted-foreground">{kit.note}</p>
              </div>

              <div className="mb-6">
                <h3 className="font-medium text-sm mb-2 text-primary">Tailored Resume</h3>
                <div className="space-y-3">
                  {kit.tailored_resume.bullets.map((b, i) => (
                    <div key={i} className="p-3 rounded border border-border bg-muted/50">
                      <p className="text-sm">{b.text}</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        Sources: {b.source_ids.join(", ")}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="mb-6">
                <h3 className="font-medium text-sm mb-2 text-primary">Cover Letter</h3>
                <div className="p-4 rounded border border-border bg-muted/50 text-sm whitespace-pre-wrap">
                  {kit.cover_letter || "Cover letter not generated."}
                </div>
              </div>

              <div className="flex gap-4">
                <button
                  onClick={() =>
                    handleDownload(
                      kit.tailored_resume.bullets.map((b) => b.text).join("\n\n"),
                      `resume-${kit.job_id}.txt`
                    )
                  }
                  className="flex-1 py-3 px-6 bg-primary text-primary-foreground rounded font-medium"
                >
                  Download Resume
                </button>
                <button
                  onClick={() => handleDownload(kit.cover_letter, `cover-letter-${kit.job_id}.txt`)}
                  className="flex-1 py-3 px-6 bg-secondary text-sm font-medium rounded text-center hover:bg-accent"
                >
                  Download Cover Letter
                </button>
              </div>
            </div>

            <div className="p-4 bg-amber-50 rounded-lg border border-amber-200">
              <p className="text-sm text-amber-800">
                <strong>Important:</strong> This kit is generated for manual submission only. Hireloop does not auto-submit applications.
              </p>
            </div>
          </div>
        ) : (
          <div className="text-center py-20">
            <p className="text-muted-foreground">No apply kit found.</p>
            <Link to="/dashboard" className="text-primary font-medium hover:underline mt-2 inline-block">
              Back to Dashboard →
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}
