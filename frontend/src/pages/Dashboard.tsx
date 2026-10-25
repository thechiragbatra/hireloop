import { Link, useSearchParams } from "react-router-dom"

export const Dashboard: React.FC = () => {
  const [searchParams] = useSearchParams()

  return (
    <div className="min-h-screen bg-secondary p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-2 mb-8">
          <h1 className="text-2xl font-bold text-primary">Dashboard</h1>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <div className="bg-card p-6 rounded-xl border shadow-sm">
            <h3 className="font-medium text-sm mb-4 text-primary">1. Upload Resume</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Parse your PDF/DOCX resume into a structured profile with skills, experience, and projects.
            </p>
            <Link
              to="/upload"
              className="inline-flex items-center gap-2 text-primary font-medium hover:underline"
            >
              Upload →
            </Link>
          </div>

          <div className="bg-card p-6 rounded-xl border shadow-sm">
            <h3 className="font-medium text-sm mb-4 text-primary">2. Find Jobs</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Search public job sources (RemoteOK, Greenhouse, Lever, Ashby, Adzuna) and see match scores.
            </p>
            <Link
              to={`/jobs${searchParams.get("profileId") ? `?profileId=${searchParams.get("profileId")}` : ""}`}
              className="inline-flex items-center gap-2 text-primary font-medium hover:underline"
            >
              Find Jobs →
            </Link>
          </div>

          <div className="bg-card p-6 rounded-xl border shadow-sm">
            <h3 className="font-medium text-sm mb-4 text-primary">3. Track Applications</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Save and track your job applications with match scores and status.
            </p>
            <Link
              to="/tracker"
              className="inline-flex items-center gap-2 text-primary font-medium hover:underline"
            >
              View Tracker →
            </Link>
          </div>
        </div>

        {searchParams.get("profileId") && (
          <div className="bg-card p-6 rounded-xl border shadow-sm">
            <h3 className="font-medium text-sm mb-4 text-primary">Your Profile</h3>
            <p className="text-sm text-muted-foreground">
              Profile ID: <span className="font-mono text-xs">{searchParams.get("profileId")}</span>
            </p>
            <Link
              to={`/jobs?profileId=${searchParams.get("profileId")}`}
              className="inline-flex items-center gap-2 text-primary font-medium hover:underline mt-2"
            >
              Find matching jobs →
            </Link>
          </div>
        )}

        <div className="bg-card p-6 rounded-xl border shadow-sm mt-8">
          <h3 className="font-medium text-sm mb-4 text-primary">How it works</h3>
          <ol className="list-decimal list-inside space-y-2 text-sm text-muted-foreground">
            <li>Upload your resume (PDF/DOCX) — it's parsed into a structured profile.</li>
            <li>Browse jobs from public sources — each is scored against your profile.</li>
            <li>Tailor your resume using only facts from your profile — with source citations.</li>
            <li>Verify faithfulness — ensure no fabricated claims.</li>
            <li>Generate an apply kit (tailored resume + cover letter) for manual submission.</li>
            <li>Track your applications in the tracker.</li>
          </ol>
        </div>
      </div>
    </div>
  )
}
