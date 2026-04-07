import { Navigate, Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import TopBar from './TopBar'
import { useAuth } from '../../contexts/AuthContext'

const AUTH_ENABLED = import.meta.env.VITE_AUTH_ENABLED === 'true'

export default function AppLayout() {
  const { user, loading } = useAuth()

  // Auth guard — only enforced when VITE_AUTH_ENABLED=true
  if (AUTH_ENABLED) {
    if (loading) {
      return (
        <div className="min-h-screen bg-[#F5F6F8] flex items-center justify-center">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-3 border-[#2D8D68] border-t-transparent rounded-full animate-spin" />
            <span className="text-sm text-gray-500 font-medium">Cargando sesión...</span>
          </div>
        </div>
      )
    }
    if (!user) {
      return <Navigate to="/login" replace />
    }
  }

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      <TopBar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto bg-[#F5F6F8]">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
