import { useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/useAuth'
import { useTranslation } from 'react-i18next'

const NAV_ITEMS = [
  { path: '/', match: ['/'], labelKey: 'nav.pesquisa', meta: '01' },
  { path: '/duelo', match: ['/duelo'], labelKey: 'nav.duelo', meta: '02' },
  { path: '/historico', match: ['/historico'], labelKey: 'nav.historico', meta: '03' },
]

const IDIOMAS = [
  { code: 'pt', label: 'PT' },
  { code: 'en', label: 'EN' },
  { code: 'es', label: 'ES' },
]

export default function Sidebar() {
  const { user, logout } = useAuth()
  const { t, i18n } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <aside className="w-[248px] shrink-0 border-r border-[rgba(120,160,220,.12)] bg-[rgba(6,11,20,.7)] flex flex-col px-[18px] py-[26px]">
      <div className="flex items-baseline gap-2 px-2 pb-[26px]">
        <span className="font-sans font-extrabold text-white text-[22px] leading-none" style={{ fontStretch: '114%', letterSpacing: '-.03em' }}>FORD</span>
        <span className="font-sans font-extrabold text-[#1e6bff] text-[22px] leading-none" style={{ fontStretch: '114%', letterSpacing: '-.03em' }}>CI</span>
      </div>

      <nav className="flex flex-col gap-1">
        {NAV_ITEMS.map(({ path, match, labelKey, meta }) => {
          const ativo = match.includes(location.pathname)
          return (
            <button
              key={path}
              onClick={() => navigate(path)}
              className={`flex items-center gap-[11px] px-[14px] py-[13px] rounded-[13px] transition-all duration-300 ease-out text-left active:scale-[0.97]
                ${ativo ? 'bg-[rgba(30,107,255,.16)] text-white' : 'text-[#7e90ac] hover:text-white hover:bg-[rgba(30,107,255,.07)] hover:translate-x-[2px]'}`}
            >
              <span className={`w-[3px] rounded-full transition-all duration-300 ease-out ${ativo ? 'h-[18px] bg-[#1e6bff]' : 'h-[10px] bg-[rgba(120,160,220,.3)]'}`} />
              <span className="font-sans font-semibold text-[13.5px]">{t(labelKey)}</span>
              <span className="ml-auto font-mono text-[10px] opacity-[.55]">{meta}</span>
            </button>
          )
        })}
      </nav>

      <div className="mt-auto flex flex-col gap-3">
        <div className="flex items-center gap-1 border border-[rgba(120,160,220,.2)] rounded-lg p-1 self-start">
          {IDIOMAS.map(({ code, label }) => (
            <button
              key={code}
              onClick={() => i18n.changeLanguage(code)}
              className={`px-2 py-1 rounded text-xs font-bold font-mono transition
                ${i18n.language === code ? 'bg-[#1e6bff] text-white' : 'text-[#5d6b82] hover:text-white'}`}
            >
              {label}
            </button>
          ))}
        </div>

        <div className="border border-[rgba(120,160,220,.14)] rounded-2xl p-[14px]">
          <div className="flex items-center gap-2">
            <span className="w-[6px] h-[6px] rounded-full bg-[#3ed598] animate-pulse" />
            <span className="font-mono font-semibold text-[9.5px] tracking-[.12em] text-[#3ed598]">{t('nav.groq_ativo')}</span>
          </div>
          <div className="font-mono text-[11px] leading-[1.5] text-[#5d6b82] mt-[9px]">
            groq api · gpt-oss-20b<br />consenso · automaistv, caranddriver, motor1
          </div>
        </div>

        <button
          onClick={handleLogout}
          className="flex items-center gap-[10px] border border-[rgba(120,160,220,.14)] hover:border-[rgba(245,90,90,.4)] rounded-2xl px-[14px] py-[12px] text-[#8fa3c0] hover:text-[#ff9a9a] transition"
        >
          <span className="w-[26px] h-[26px] rounded-full bg-[rgba(30,107,255,.18)] flex items-center justify-center font-mono font-bold text-[10px] text-[#8fb6ff]">
            FC
          </span>
          <span className="font-sans font-semibold text-xs truncate max-w-[110px]">{user?.email}</span>
          <span className="ml-auto font-mono font-bold text-xs">⏻</span>
        </button>
      </div>
    </aside>
  )
}