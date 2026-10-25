import { Link, useLocation, useNavigate } from "react-router-dom"
import { signOut } from "@/lib/supabase"

interface NavbarProps {
  user: { id: string; email: string | null } | null
  onLogin: () => void
  onLogout: () => void
}

export const Navbar: React.FC<NavbarProps> = ({ user, onLogin, onLogout }) => {
  const location = useLocation()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await signOut()
    onLogout()
    navigate("/login")
  }

  return (
    <nav className="fixed top-0 w-full z-50 bg-card border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <Link to="/" className="flex items-center gap-2 font-bold text-xl text-primary">
            <span className="bg-primary p-1 rounded text-primary-foreground">H</span>
            Hireloop
          </Link>
          <div className="hidden md:flex gap-6 items-center">
            <Link
              to="/dashboard"
              className={`text-sm font-medium ${
                location.pathname === "#/dashboard" ? "text-primary" : "text-muted-foreground"
              }`}
            >
              Dashboard
            </Link>
            <Link
              to="/jobs"
              className={`text-sm font-medium ${
                location.pathname === "#/jobs" ? "text-primary" : "text-muted-foreground"
              }`}
            >
              Jobs
            </Link>
            <Link
              to="/tracker"
              className={`text-sm font-medium ${
                location.pathname === "#/tracker" ? "text-primary" : "text-muted-foreground"
              }`}
            >
              Tracker
            </Link>
            {user ? (
              <>
                <Link
                  to="/upload"
                  className="text-sm font-medium text-muted-foreground"
                >
                  Upload Resume
                </Link>
                <button onClick={handleLogout} className="text-sm text-destructive">
                  Sign out ({user.email})
                </button>
              </>
            ) : (
              <button onClick={onLogin} className="bg-primary text-primary-foreground px-4 py-2 rounded text-sm font-medium">
                Sign in
              </button>
            )}
          </div>
          <div className="md:hidden">
            <button
              onClick={onLogin}
              className="bg-primary text-primary-foreground px-3 py-1.5 rounded text-sm"
            >
              Sign in
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}
