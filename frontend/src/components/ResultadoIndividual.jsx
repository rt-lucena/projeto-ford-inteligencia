import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { traduzirAtributo } from '../data/attributeLabels'
import { capitalizarPalavras } from '../utils/texto'

const PRIORIDADE_HERO = ['Potência', 'Torque', 'Aceleração 0-100 km/h']

const ABREVIACOES_UNIDADE = {
  segundos: 's', segundo: 's', seg: 's', s: 's',
  cavalos: 'cv', cv: 'cv',
  'kgf.m': 'kgfm', 'kgf·m': 'kgfm', kgfm: 'kgfm',
  'n.m': 'Nm', nm: 'Nm', Nm: 'Nm',
  rpm: 'rpm',
}

function abreviarUnidade(unidade) {
  if (!unidade) return unidade
  const chave = unidade.toLowerCase().replace(/\s+/g, '')
  return ABREVIACOES_UNIDADE[chave] || unidade
}

function extrairNumeroEUnidade(valor) {
  const texto = String(valor)
  const m = texto.match(/^([\d.,]+)\s*([^\s\d]*)/)
  if (!m) return { numero: texto, unidade: '' }
  return { numero: m[1], unidade: abreviarUnidade(m[2]) }
}

function StatCard({ label, valor, unidade }) {
  const [exibido, setExibido] = useState(0)

  useEffect(() => {
    const alvo = parseFloat(String(valor).replace(',', '.'))
    // eslint-disable-next-line react-hooks/set-state-in-effect -- fallback síncrono quando `valor` não é numérico
    if (Number.isNaN(alvo)) { setExibido(valor); return }
    const decimais = (String(valor).split(/[.,]/)[1] || '').length
    const duracao = 900
    const inicio = performance.now()
    let frame
    function passo(agora) {
      const p = Math.min((agora - inicio) / duracao, 1)
      const facilitado = 1 - Math.pow(1 - p, 3)
      setExibido((alvo * facilitado).toFixed(decimais))
      if (p < 1) frame = requestAnimationFrame(passo)
    }
    frame = requestAnimationFrame(passo)
    return () => cancelAnimationFrame(frame)
  }, [valor])

  return (
    <div className="flex-1 min-w-0 overflow-hidden bg-[rgba(4,7,14,.5)] border border-[rgba(120,160,220,.14)] rounded-2xl px-3 sm:px-[18px] py-3 sm:py-4">
      <div className="font-mono text-[8.5px] sm:text-[9px] tracking-[.1em] text-[#7e90ac] uppercase truncate">{label}</div>
      <div className="flex items-baseline flex-wrap gap-x-1 mt-2 sm:mt-2.5">
        <span className="font-sans font-extrabold text-white text-[20px] sm:text-[30px] leading-none">{exibido}</span>
        <span className="font-mono font-semibold text-[9px] sm:text-xs text-[#8fb6ff] leading-none">{unidade}</span>
      </div>
    </div>
  )
}

function SpecCard({ atributo, valor, index, idioma }) {
  const { t } = useTranslation()
  const [pronto, setPronto] = useState(false)
  const encontrado = valor !== 'Não disponível'

  useEffect(() => {
    const id = requestAnimationFrame(() => setPronto(true))
    return () => cancelAnimationFrame(id)
  }, [])

  return (
    <div
      style={{ animation: 'fcd-rise .4s ease both', animationDelay: `${Math.min(index * 40, 400)}ms` }}
      className="bg-[rgba(10,17,30,.9)] border border-[rgba(120,160,220,.12)] hover:border-[rgba(30,107,255,.4)] hover:-translate-y-[2px] rounded-2xl p-5 transition-all duration-300"
    >
      <span className="font-mono font-semibold text-[11px] tracking-[.1em] text-[#6f8099] uppercase">{traduzirAtributo(atributo, idioma)}</span>
      <div className="font-sans font-bold text-[17px] leading-[1.35] text-[#e8eef8] mt-3 min-h-[46px]">{valor}</div>
      <div className="flex items-center gap-2.5 mt-3.5">
        <div className="flex-1 h-[3px] rounded-full bg-[rgba(120,160,220,.12)] overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-700 ease-out"
            style={{ width: pronto ? (encontrado ? '100%' : '8%') : '0%', background: encontrado ? '#3ed598' : '#5d6b82' }}
          />
        </div>
        <span
          className="font-mono font-semibold text-[9.5px] uppercase whitespace-nowrap"
          style={{ color: encontrado ? '#3ed598' : '#5d6b82' }}
        >
          {encontrado ? t('resultado.encontrado') : t('resultado.indisponivel')}
        </span>
      </div>
    </div>
  )
}

export default function ResultadoIndividual({ resultado, onNova }) {
  const { t, i18n } = useTranslation()
  const { marca, modelo, versao, ano, specs } = resultado

  const total = Object.keys(specs).length
  const encontradosCount = Object.values(specs).filter(v => v !== 'Não disponível').length

  const heroStats = PRIORIDADE_HERO
    .filter(attr => specs[attr] && specs[attr] !== 'Não disponível')
    .slice(0, 3)
    .map(attr => {
      const { numero, unidade } = extrairNumeroEUnidade(specs[attr])
      return {
        key: attr,
        label: attr === 'Aceleração 0-100 km/h' ? '0-100' : traduzirAtributo(attr, i18n.language),
        valor: numero,
        unidade,
      }
    })

  const watermark = heroStats[0]?.valor

  function exportarCSV() {
    const linhas = [
      ['Veículo', `${capitalizarPalavras(marca)} ${capitalizarPalavras(modelo)} ${capitalizarPalavras(versao)} ${ano}`],
      [''],
      [t('resultado.atributo'), t('resultado.especificacao'), t('resultado.status')],
      ...Object.entries(specs).map(([atributo, valor]) => [
        traduzirAtributo(atributo, i18n.language),
        valor,
        valor !== 'Não disponível' ? t('resultado.encontrado') : t('resultado.nao_disponivel')
      ])
    ]

    const csv = linhas.map(l => l.map(c => `"${c}"`).join(',')).join('\n')
    const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${marca}-${modelo}-${versao}-${ano}.csv`.replace(/\s+/g, '-')
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <button
          onClick={onNova}
          className="bg-transparent border-none text-[#7e90ac] hover:text-white font-mono font-semibold text-[11px] flex items-center gap-2 transition"
        >
          <span className="text-base">←</span> {t('resultado.nova_pesquisa')}
        </button>
        <button
          onClick={exportarCSV}
          className="border border-[rgba(30,107,255,.4)] bg-[rgba(30,107,255,.16)] hover:bg-[rgba(30,107,255,.3)] hover:text-white rounded-[11px] px-4 py-[11px] text-[#8fb6ff] font-sans font-semibold text-xs transition"
        >
          {t('resultado.exportar')}
        </button>
      </div>

      <div
        className="relative mt-4 rounded-[26px] overflow-hidden border border-[rgba(120,160,220,.16)]"
        style={{ background: 'linear-gradient(120deg,#0a2a6b,#081326 62%)' }}
      >
        {watermark && (
          <div
            className="absolute right-4 md:right-8 -top-2 md:-top-8 font-sans font-extrabold leading-none pointer-events-none select-none text-[90px] md:text-[200px]"
            style={{ fontStretch: '118%', letterSpacing: '-.06em', color: 'rgba(255,255,255,.05)' }}
          >
            {watermark}
          </div>
        )}
        <div className="relative p-5 sm:p-6 md:p-8 flex flex-col md:flex-row md:items-end justify-between gap-5 md:gap-10">
          <div>
            <div className="font-mono text-[11px] tracking-[.16em] text-[#8fb6ff] uppercase">{marca} · {ano}</div>
            <div
              className="font-sans font-extrabold text-white leading-none tracking-[-.04em] mt-3.5 text-[32px] md:text-[56px]"
              style={{ fontStretch: '110%' }}
            >
              {capitalizarPalavras(modelo)} {capitalizarPalavras(versao)}
            </div>
          </div>
          {heroStats.length > 0 && (
            <div className="flex gap-2 sm:gap-3">
              {heroStats.map(({ key, label, valor, unidade }) => (
                <StatCard key={key} label={label} valor={valor} unidade={unidade} />
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="mt-8 mb-1">
        <span className="font-mono font-semibold text-[10px] tracking-[.14em] text-[#6f8099] uppercase">
          {t('resultado.ficha_tecnica')} · <span style={{ color: '#3ed598' }}>{t('resultado.contagem', { encontrados: encontradosCount, total })}</span>
        </span>
      </div>
      <p className="font-mono text-[10px] text-[#4c5a70] mb-4">{t('resultado.fonte_pipeline')}</p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {Object.entries(specs).map(([atributo, valor], index) => (
          <SpecCard key={atributo} atributo={atributo} valor={valor} index={index} idioma={i18n.language} />
        ))}
      </div>
    </div>
  )
}