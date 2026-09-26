import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { useAuth } from './context/useAuth'
import AppLayout from './components/AppLayout'
import Login from './pages/Login'
import Pesquisa from './pages/Pesquisa'
import Duelo from './pages/Duelo'
import Historico from './pages/Historico'

function RotaProtegida() {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" />
  return (
    <AppLayout>
      <Outlet />
    </AppLayout>
  )
}

function Rotas() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<RotaProtegida />}>
        <Route path="/" element={<Pesquisa />} />
        <Route path="/duelo" element={<Duelo />} />
        <Route path="/historico" element={<Historico />} />
      </Route>
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Rotas />
      </AuthProvider>
    </BrowserRouter>
  )
}