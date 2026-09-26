import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/useAuth'
import { useTranslation } from 'react-i18next'

const IDIOMAS = [
  { code: 'pt', label: 'PT' },
  { code: 'en', label: 'EN' },
  { code: 'es', label: 'ES' },
]

export default function MobileHeader() {
  const { user, logout } = useAuth()
  const { t, i18n } = useTranslation()
  const navigate = useNavigate()
  const [aberto, setAberto] = useState(false)

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <div className="fixed z-40" style={{ top: 'calc(env(safe-area-inset-top, 0px) + 16px)', right: 16 }}>
      <button
        onClick={() => setAberto(v => !v)}
        className="w-9 h-9 rounded-full flex items-center justify-center font-mono font-bold text-[11px] text-[#8fb6ff]"
        style={{
          background: 'rgba(30,107,255,.18)',
          border: '1px solid rgba(120,160,220,.2)',
          transition: 'transform 200ms ease',
          transform: aberto ? 'scale(0.9)' : 'scale(1)',
        }}
      >
        FC
      </button>

      {aberto && <div className="fixed inset-0 z-[-1]" onClick={() => setAberto(false)} />}

      <div
        className="absolute top-11 right-0 w-[200px] origin-top-right"
        style={{
          opacity: aberto ? 1 : 0,
          transform: aberto ? 'scale(1) translateY(0)' : 'scale(0.9) translateY(-10px)',
          transition: aberto
            ? 'opacity 250ms ease, transform 350ms cubic-bezier(.34,1.56,.64,1)'
            : 'opacity 180ms ease, transform 180ms ease',
          pointerEvents: aberto ? 'auto' : 'none',
        }}
      >
        <div
          className="rounded-2xl p-3 flex flex-col gap-3"
          style={{ background: 'rgba(8,14,26,.95)', backdropFilter: 'blur(18px)', border: '1px solid rgba(120,160,220,.18)', boxShadow: '0 18px 40px -14px rgba(0,0,0,.9)' }}
        >
          <span className="font-sans text-xs text-[#8fa3c0] truncate">{user?.email}</span>
          <div className="flex items-center gap-1 border border-[rgba(120,160,220,.2)] rounded-lg p-1 self-start">
            {IDIOMAS.map(({ code, label }) => (
              <button
                key={code}
                onClick={() => i18n.changeLanguage(code)}
                className={`px-2 py-1 rounded text-xs font-bold font-mono transition
                  ${i18n.language === code ? 'bg-[#1e6bff] text-white' : 'text-[#5d6b82]'}`}
              >
                {label}
              </button>
            ))}
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center justify-between border border-[rgba(120,160,220,.14)] rounded-xl px-3 py-2.5 text-[#8fa3c0] text-sm font-sans font-semibold"
          >
            {t('nav.sair')}
            <span className="font-mono font-bold text-xs">⏻</span>
          </button>
        </div>
      </div>
    </div>
  )
}