import { Navigate, useLocation } from "react-router-dom"
import { supabase } from "@/lib/supabase"
import type { AuthChangeEvent, Session } from "@supabase/supabase-js"
import { useEffect, useState } from "react"

interface ProtectedRouteProps {
  children: React.ReactNode
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const [user, setUser] = useState<{ id: string; email: string | null } | null>(null)
  const [loading, setLoading] = useState(true)
  const location = useLocation()

  useEffect(() => {
    const checkAuth = async () => {
      const { data } = await supabase.auth.getUser()
      setUser(
        data.user
          ? { id: data.user.id, email: data.user.email ?? null }
          : null
      )
      setLoading(false)
    }
    checkAuth()

    const { data: sub } = supabase.auth.onAuthStateChange(
      (_event: AuthChangeEvent, session: Session | null) => {
        setUser(
          session?.user
            ? { id: session.user.id, email: session.user.email ?? null }
            : null
        )
      }
    )
    return () => sub.subscription.unsubscribe()
  }, [])

  if (loading) return <div className="p-10 text-center">Loading...</div>

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  return <div>{children}</div>
}
