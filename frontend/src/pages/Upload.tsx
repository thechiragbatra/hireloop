import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { api } from "@/lib/api"
import type { Profile } from "@/types"

export const Upload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [profile, setProfile] = useState<Profile | null>(null)
  const navigate = useNavigate()

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0])
      setError("")
    }
  }

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return

    setLoading(true)
    setError("")

    const formData = new FormData()
    formData.append("file", file)

    try {
      const res = await api.post("/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      setProfile(res.data.profile)
      navigate(`/dashboard?profileId=${res.data.profile.id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || "Upload failed")
    } finally {
      setLoading(false)
    }
  }

  const acceptedTypes = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  ]

  return (
    <div className="min-h-screen bg-secondary p-4 md:p-8">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center gap-2 mb-6">
          <Link to="/dashboard" className="text-muted-foreground hover:text-primary">
            ← Back to Dashboard
          </Link>
          <h1 className="text-2xl font-bold text-primary">Upload Resume</h1>
        </div>

        {error && (
          <div className="p-3 rounded bg-destructive/10 text-destructive text-sm border border-destructive/20 mb-4">
            {error}
          </div>
        )}

        <div className="bg-card p-6 rounded-xl border shadow-sm">
          <form onSubmit={handleUpload} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Select resume file</label>
              <input
                type="file"
                accept={acceptedTypes.join(",")}
                onChange={handleFileChange}
                className="block w-full text-sm text-muted-foreground file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-primary-foreground hover:file:bg-primary/90"
              />
              <p className="text-xs text-muted-foreground mt-1">
                PDF or DOCX only. Max 10 MB.
              </p>
            </div>

            {file && (
              <div className="flex items-center gap-2 p-3 bg-muted rounded border">
                <span className="text-sm">{file.name}</span>
                <span className="ml-auto text-xs text-muted-foreground">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !file}
              className="w-full py-3 px-4 bg-primary text-primary-foreground rounded font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Uploading..." : "Upload & Parse Resume"}
            </button>
          </form>
        </div>

        {profile && (
          <div className="mt-6 bg-card p-6 rounded-xl border shadow-sm">
            <h2 className="text-lg font-bold mb-4">Profile Extracted</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Skills</p>
                <p className="text-sm">{profile.skills.join(", ") || "—"}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Experience</p>
                <p className="text-sm">{profile.experience.length} entries</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Projects</p>
                <p className="text-sm">{profile.projects.length} entries</p>
              </div>
            </div>
            <div className="mt-4">
              <Link to={`/match?profileId=${profile.id}`} className="inline-flex items-center gap-2 text-primary font-medium hover:underline">
                Find matching jobs →
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
