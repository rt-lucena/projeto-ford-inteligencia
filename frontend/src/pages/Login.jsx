import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/useAuth'
import { useTranslation } from 'react-i18next'
import { ATRIBUTOS } from '../data/attributesData'
import GlobalBackground from '../components/GlobalBackground'

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

const IDIOMAS = [
  { code: 'pt', label: 'PT' },
  { code: 'en', label: 'EN' },
  { code: 'es', label: 'ES' },
]

export default function Login() {
  const { login } = useAuth()
  const { t, i18n } = useTranslation()
  const navigate = useNavigate()

  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setErro('')

    const emailLimpo = email.trim()
    const senhaLimpa = senha.trim()

    if (!emailLimpo || !senhaLimpa) {
      setErro(t('login.erro_campos'))
      return
    }

    if (!EMAIL_REGEX.test(emailLimpo)) {
      setErro(t('login.erro_email'))
      return
    }

    setLoading(true)
    try {
      await new Promise(r => setTimeout(r, 800))
      const ok = await login(emailLimpo, senhaLimpa)

      if (ok) {
        navigate('/')
      } else {
        setErro(t('login.erro_credenciais'))
      }
    } catch (error) {
      setErro(t('login.erro_credenciais'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#04070e] relative overflow-hidden flex flex-col lg:flex-row">
      <GlobalBackground />

      {/* Painel esquerdo — só desktop */}
      <div className="hidden lg:flex lg:w-[55%] flex-col justify-between px-[60px] py-16 border-r border-[rgba(120,160,220,.12)] relative z-10">
        <div className="flex items-center gap-2">
          <span className="w-[6px] h-[6px] rounded-full bg-[#f5a524] animate-pulse" />
          <span className="font-mono text-[11px] tracking-[.18em] text-[#7e90ac] uppercase">{t('login.status')}</span>
        </div>

        <div>
          <div className="font-sans font-extrabold text-white text-[128px] leading-[.84] tracking-[-.05em]" style={{ fontStretch: '118%' }}>FORD</div>
          <div className="flex items-end gap-[22px]">
            <div className="font-sans font-extrabold text-[#1e6bff] text-[128px] leading-[.84] tracking-[-.05em]" style={{ fontStretch: '118%' }}>CI</div>
            <div className="font-mono text-[#7e90ac] text-sm pb-4">
              <div>{t('login.tagline_l1')}</div>
              <div>{t('login.tagline_l2', { count: ATRIBUTOS.length })}</div>
              <div>{t('login.tagline_l3')}</div>
            </div>
          </div>
        </div>

        <div className="flex gap-3.5">
          {[
            { v: String(ATRIBUTOS.length), k: t('login.stat_atributos') },
            { v: '4', k: t('login.stat_fontes') },
            { v: '92%', k: t('login.stat_confianca') },
          ].map(({ v, k }) => (
            <div key={k} className="flex-1 bg-[rgba(10,17,30,.7)] border border-[rgba(120,160,220,.14)] rounded-2xl px-[18px] py-4">
              <div className="font-sans font-extrabold text-white text-[30px] leading-none">{v}</div>
              <div className="font-mono text-[10px] tracking-[.1em] text-[#7e90ac] mt-[9px]">{k}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Painel direito — form (único no mobile) */}
      <div className="flex-1 flex items-center justify-center px-6 py-16 lg:px-[60px] relative z-10">
        <div className="w-full max-w-[400px]">

          {/* Cabeçalho — só mobile, no desktop isso já está no painel esquerdo */}
          <div className="lg:hidden flex items-center gap-2 mb-6">
            <span className="w-[6px] h-[6px] rounded-full bg-[#f5a524] animate-pulse" />
            <span className="font-mono text-[11px] tracking-[.18em] text-[#7e90ac] uppercase">{t('login.status')}</span>
          </div>
          <div className="lg:hidden mb-10">
            <h1 className="font-sans font-extrabold text-white text-[76px] leading-none tracking-[-.045em]" style={{ fontStretch: '118%' }}>
              FORD <span className="text-[#1e6bff]">CI</span>
            </h1>
            <p className="font-mono text-[#7e90ac] text-xs tracking-[.1em] mt-3 uppercase">{t('login.tagline_mobile')}</p>
          </div>

          <h2 className="font-sans font-extrabold text-white text-[34px] leading-none tracking-[-.03em]" style={{ fontStretch: '110%' }}>
            {t('login.titulo')}
          </h2>
          <p className="font-sans text-[#7e90ac] text-sm mt-2.5 mb-7">{t('login.subtitulo')}</p>

          <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
            <div className="flex flex-col gap-2">
              <label className="font-mono text-[10px] tracking-[.14em] text-[#7e90ac] uppercase">{t('login.email')}</label>
              <input
                type="email"
                placeholder={t('login.placeholder_email')}
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="bg-[rgba(12,22,42,.75)] border border-[rgba(120,160,220,.18)] border-b-2 border-b-[rgba(30,107,255,.55)] rounded-xl px-4 py-[15px] text-[15px] text-white placeholder-[#4c5a70] outline-none focus:border-[#1e6bff] transition font-medium"
              />
            </div>

            <div className="flex flex-col gap-2">
              <label className="font-mono text-[10px] tracking-[.14em] text-[#7e90ac] uppercase">{t('login.senha')}</label>
              <input
                type="password"
                placeholder={t('login.placeholder_senha')}
                value={senha}
                onChange={e => setSenha(e.target.value)}
                className="bg-[rgba(12,22,42,.75)] border border-[rgba(120,160,220,.18)] border-b-2 border-b-[rgba(30,107,255,.55)] rounded-xl px-4 py-[15px] text-[15px] text-white placeholder-[#4c5a70] outline-none focus:border-[#1e6bff] transition font-medium"
              />
            </div>

            {erro && (
              <div className="flex items-center gap-[9px] bg-[rgba(245,90,90,.09)] border border-[rgba(245,90,90,.3)] rounded-xl px-[14px] py-3">
                <span className="w-[5px] h-4 rounded bg-[#f55a5a] flex-none" />
                <p className="text-[#ff9a9a] text-sm">{erro}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="mt-1.5 bg-[#1e6bff] hover:bg-[#3d84ff] text-white font-bold text-[15px] h-14 px-[22px] rounded-[13px] flex items-center justify-between transition disabled:opacity-60"
              style={{ boxShadow: '0 12px 30px -12px rgba(30,107,255,.9)' }}
            >
              <span>{loading ? t('login.entrando') : t('login.btn_entrar')}</span>
              <span className="font-mono font-bold text-lg">→</span>
            </button>
          </form>

          <div className="flex items-center justify-between pt-1.5 mt-4">
            <span className="font-mono text-[11px] text-[#4c5a70]">{t('login.demo')}</span>
            <div className="flex gap-[5px]">
              {IDIOMAS.map(({ code, label }) => (
                <button
                  key={code}
                  onClick={() => i18n.changeLanguage(code)}
                  className={`rounded-[7px] px-[9px] py-[7px] font-mono font-bold text-[10px] transition
                    ${i18n.language === code ? 'bg-[#1e6bff] border border-[#1e6bff] text-white' : 'bg-transparent border border-[rgba(120,160,220,.2)] text-[#5d6b82]'}`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}