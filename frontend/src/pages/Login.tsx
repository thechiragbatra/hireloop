import { useState } from "react"
import { supabase } from "@/lib/supabase"

export const Login: React.FC = () => {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")

    const { data, error: err } = await supabase.auth.signInWithPassword({
      email,
      password,
    })

    if (err) {
      setError(err.message)
      setLoading(false)
      return
    }

    if (data.user && data.session) {
      localStorage.setItem("supabase_auth_token", data.session.access_token)
      window.location.hash = "/dashboard"
    }
  }

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")

    const { error: err } = await supabase.auth.signUp({
      email,
      password,
    })

    if (err) {
      setError(err.message)
      setLoading(false)
      return
    }

    setError("Account created. Please check your email to confirm, then sign in.")
    setLoading(false)
  }

  const handleGoogleSignIn = async () => {
    setLoading(true)
    const { error: err } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}#/dashboard`,
      },
    })
    if (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-secondary px-4">
      <div className="max-w-md w-full space-y-6 bg-card p-8 rounded-xl border shadow-sm">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-primary mb-2">Hireloop</h1>
          <p className="text-muted-foreground">AI Job Copilot</p>
        </div>

        {error && (
          <div className="p-3 rounded bg-destructive/10 text-destructive text-sm border border-destructive/20">
            {error}
          </div>
        )}

        <form onSubmit={handleSignIn} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 rounded border input bg-background focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 rounded border input bg-background focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2 px-4 bg-primary text-primary-foreground rounded font-medium disabled:opacity-50"
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-card px-2 text-muted-foreground">Or continue with</span>
          </div>
        </div>

        <button
          onClick={handleGoogleSignIn}
          disabled={loading}
          className="w-full flex items-center justify-center gap-2 py-2 px-4 border border-input rounded bg-secondary text-sm font-medium hover:bg-accent disabled:opacity-50"
        >
          Sign in with Google
        </button>

        <p className="text-center text-sm text-muted-foreground">
          Don't have an account?{" "}
          <button
            type="button"
            onClick={handleSignUp}
            className="text-primary font-medium hover:underline"
          >
            Sign up
          </button>
        </p>
      </div>
    </div>
  )
}
