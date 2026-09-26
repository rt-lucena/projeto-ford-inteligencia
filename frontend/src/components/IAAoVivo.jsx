import { useState, useEffect, useRef } from 'react'
import { useTranslation } from 'react-i18next'

const AZUL = '#1e6bff'
const AMBAR = '#f5a524'
const MUTED = '#7e90ac'
const STAGE_META = ['3 FONTES', 'SCRAPY', 'CONSENSO', 'GROQ', 'POSTGRES']

export default function IAAoVivo({ marca, modelo, versao, ano, totalAtributos, concluido, onPular }) {
  const { t } = useTranslation()
  const [stage, setStage] = useState(1)
  const [elapsed, setElapsed] = useState(0)
  const [logs, setLogs] = useState([])
  const timersRef = useRef([])
  const seqRef = useRef([])

  useEffect(() => {
    const seq = [
      { st: 1, at: 300, cor: MUTED, txt: t('ia.log_requisicao', { marca, modelo, versao, ano }) },
      { st: 1, at: 700, cor: '#4c5a70', txt: t('ia.log_fila') },
      { st: 2, at: 1200, cor: MUTED, txt: t('ia.log_crawl') },
      { st: 2, at: 1750, cor: '#3ed598', txt: t('ia.log_fontes_ok') },
      { st: 2, at: 2200, cor: '#3ed598', txt: t('ia.log_artigos_ok') },
      { st: 3, at: 2700, cor: MUTED, txt: t('ia.log_consenso') },
      { st: 3, at: 3200, cor: '#3ed598', txt: t('ia.log_divergencias') },
      { st: 4, at: 3700, cor: '#8fb6ff', txt: t('ia.log_groq') },
      { st: 4, at: 4400, cor: '#3ed598', txt: t('ia.log_campos', { n: totalAtributos }) },
      { st: 5, at: 4900, cor: MUTED, txt: t('ia.log_validando') },
      { st: 5, at: 5400, cor: AMBAR, txt: t('ia.log_gravado') },
    ]
    seqRef.current = seq

    const iv = setInterval(() => setElapsed(e => +(e + 0.1).toFixed(1)), 100)
    const timers = seq.map(s =>
      setTimeout(() => {
        setStage(s.st)
        setLogs(prev => [{ t: s.txt, cor: s.cor }, ...prev])
      }, s.at)
    )
    timersRef.current = [iv, ...timers]

    return () => {
      timersRef.current.forEach(id => { clearTimeout(id); clearInterval(id) })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [marca, modelo, versao, ano, totalAtributos])

  // Quando a resposta real da API chega, encerra a dramatização: completa
  // qualquer log que ainda não tinha aparecido e só então vai pra 100% de verdade.
  useEffect(() => {
    if (!concluido) return
    timersRef.current.forEach(id => { clearTimeout(id); clearInterval(id) })
    // eslint-disable-next-line react-hooks/set-state-in-effect -- sincroniza com a prop `concluido`, não é loop de estado
    setStage(5)
    setLogs(prev => {
      const jaMostrados = new Set(prev.map(l => l.t))
      const faltando = seqRef.current.filter(s => !jaMostrados.has(s.txt))
      return [...faltando.map(s => ({ t: s.txt, cor: s.cor })).reverse(), ...prev]
    })
  }, [concluido])

  const pct = concluido ? 100 : stage >= 5 ? 96 : Math.round((stage / 5) * 100)
  const etapas = [t('ia.etapa_fontes'), t('ia.etapa_paginas'), t('ia.etapa_consenso'), t('ia.etapa_ia'), t('ia.etapa_validando')]

  return (
    <div
      className="rounded-2xl p-6 md:p-10 relative overflow-hidden flex flex-col"
      style={{ background: 'linear-gradient(180deg,rgba(16,27,46,.95),rgba(9,16,29,.95))', border: '1px solid rgba(120,160,220,.14)', minHeight: 520 }}
    >
      <div
        className="absolute left-0 right-0 top-0 h-[2px] opacity-55 pointer-events-none"
        style={{ background: 'linear-gradient(90deg,transparent,#1e6bff,transparent)', animation: 'fcd-scan 3s linear infinite' }}
      />

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-[11px]">
          <span className="w-4 h-4 rounded-full animate-spin" style={{ border: '2px solid rgba(30,107,255,.25)', borderTopColor: '#1e6bff' }} />
          <span className="font-mono font-bold text-xs tracking-[.16em] text-[#8fb6ff] uppercase">{t('ia.extraindo')}</span>
        </div>
        <div className="flex items-center gap-[18px]">
          <span className="font-mono text-xs text-[#5d6b82]">{elapsed.toFixed(1)}s</span>
          <button
            onClick={onPular}
            className="bg-transparent border border-[rgba(120,160,220,.2)] rounded-[10px] px-[14px] py-[10px] text-[#7e90ac] hover:border-[#1e6bff] hover:text-white font-mono font-semibold text-[11px] transition uppercase"
          >
            {t('ia.pular')}
          </button>
        </div>
      </div>

      <div className="flex items-end gap-[26px] mt-[34px]">
        <div className="font-sans font-extrabold text-white leading-[.9] text-[64px] md:text-[96px] tracking-[-.05em]" style={{ fontStretch: '114%' }}>
          {pct}<span className="text-[#1e6bff]" style={{ fontSize: '38%' }}>%</span>
        </div>
        <div className="flex-1 pb-4">
          <div className="h-[6px] rounded-full bg-[rgba(120,160,220,.12)] overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{ background: 'linear-gradient(90deg,#0a2a6b,#1e6bff)', width: `${pct}%` }}
            />
          </div>
          {stage >= 5 && !concluido && (
            <p className="font-mono text-[10px] text-[#5d6b82] mt-2 animate-pulse">{t('ia.ainda_validando')}</p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-8">
        {etapas.map((label, i) => {
          const n = i + 1
          const feito = stage > n || (concluido && stage >= n)
          const ativo = stage === n && !feito
          return (
            <div
              key={label}
              className="rounded-2xl p-[18px] transition-all"
              style={{
                background: ativo ? 'rgba(30,107,255,.12)' : 'rgba(10,17,30,.85)',
                border: `1px solid ${ativo ? 'rgba(30,107,255,.45)' : 'rgba(120,160,220,.12)'}`,
              }}
            >
              <div className="flex items-center justify-between">
                <span
                  className="w-[10px] h-[10px] rounded-full"
                  style={{
                    background: feito ? '#3ed598' : ativo ? '#1e6bff' : 'rgba(120,160,220,.18)',
                    boxShadow: ativo ? '0 0 0 5px rgba(30,107,255,.18)' : 'none',
                    animation: ativo ? 'fcd-pulse 1.2s infinite' : 'none',
                  }}
                />
                <span className="font-mono text-[9.5px] text-[#4c5a70]">{STAGE_META[i]}</span>
              </div>
              <div
                className="font-sans font-semibold text-sm mt-4"
                style={{ color: feito ? '#8fa3c0' : ativo ? '#fff' : '#3d4a5e' }}
              >
                {label}
              </div>
            </div>
          )
        })}
      </div>

      <div className="mt-[22px] flex-1 min-h-0 bg-[#060b14] border border-[rgba(120,160,220,.12)] rounded-2xl px-5 py-[18px] overflow-hidden flex flex-col-reverse">
        <div>
          {logs.map((l, i) => (
            <div
              key={i}
              className="font-mono text-[12.5px] leading-[1.85]"
              style={{ color: l.cor, animation: 'fcd-rise .2s ease both' }}
            >
              {l.t}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}