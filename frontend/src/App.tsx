import { useState, useEffect } from "react"
import {
  HashRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom"
import { supabase } from "@/lib/supabase"
import { Navbar } from "@/components/Navbar"
import { Login } from "@/pages/Login"
import { Dashboard } from "@/pages/Dashboard"
import { Upload } from "@/pages/Upload"
import { Jobs } from "@/pages/Jobs"
import { Match } from "@/pages/Match"
import { Tailor } from "@/pages/Tailor"
import { Tracker } from "@/pages/Tracker"
import { ApplyKit } from "@/pages/ApplyKit"

export const App: React.FC = () => {
  const [user, setUser] = useState<{ id: string; email: string | null } | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const checkAuth = async () => {
      const { data } = await supabase.auth.getUser()
      setUser(data.user ? { id: data.user.id, email: data.user.email ?? null } : null)
      setLoading(false)
    }
    checkAuth()

    const { data: sub } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ? { id: session.user.id, email: session.user.email ?? null } : null)
    })
    return () => sub.subscription.unsubscribe()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-secondary">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <Router>
      <div className="min-h-screen bg-background">
        {!user ? (
          <>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/" element={<Navigate to="/login" replace />} />
              <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
          </>
        ) : (
          <>
            <Navbar
              user={user}
              onLogin={() => {}}
              onLogout={() => {
                supabase.auth.signOut()
                window.location.hash = "/login"
              }}
            />
            <Routes>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/upload" element={<Upload />} />
              <Route path="/jobs" element={<Jobs />} />
              <Route path="/match/:jobId" element={<Match />} />
              <Route path="/match" element={<Match />} />
              <Route path="/tailor" element={<Tailor />} />
              <Route path="/tracker" element={<Tracker />} />
              <Route path="/apply-kit/:profileId/:jobId" element={<ApplyKit />} />
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </>
        )}
      </div>
    </Router>
  )
}

export default App
