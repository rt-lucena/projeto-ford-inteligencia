import { useState, useRef } from 'react'
import { GRUPOS_ATRIBUTOS, PRESETS, PRESET_IDS, ATRIBUTOS } from '../data/attributesData'
import { traduzirAtributo } from '../data/attributeLabels'
import { buscarEspecificacoesReais } from '../api'
import { useAuth } from '../context/useAuth'
import { useTranslation } from 'react-i18next'
import ResultadoComparacao from './ResultadoComparacao'
import ResumoDuelo from './ResumoDuelo'
import IAAoVivo from './IAAoVivo'

const SLOTS = [
  { tagKey: 'duelo.veiculo_01', cor: '#8fb6ff' },
  { tagKey: 'duelo.veiculo_02', cor: '#f5a524' },
]

export default function CompararVeiculos({ aoSalvar, itemHistorico }) {
  const { token } = useAuth()
  const { t, i18n } = useTranslation()
  const [v1, setV1] = useState({
    marca: itemHistorico?.veiculo1?.marca || '',
    modelo: itemHistorico?.veiculo1?.modelo || '',
    versao: itemHistorico?.veiculo1?.versao || '',
    ano: itemHistorico?.veiculo1?.ano || '',
  })
  const [v2, setV2] = useState({
    marca: itemHistorico?.veiculo2?.marca || '',
    modelo: itemHistorico?.veiculo2?.modelo || '',
    versao: itemHistorico?.veiculo2?.versao || '',
    ano: itemHistorico?.veiculo2?.ano || '',
  })
  const [preset, setPreset] = useState('tudo')
  const [selecionados, setSelecionados] = useState(
    itemHistorico ? itemHistorico.atributos : PRESETS.tudo
  )
  const [ajusteFino, setAjusteFino] = useState(false)
  const [resultado, setResultado] = useState(itemHistorico || null)
  const [loading, setLoading] = useState(false)
  const [pulando, setPulando] = useState(false)
  const [concluido, setConcluido] = useState(false)
  const [erro, setErro] = useState('')
  const camposRef = useRef([])

  function handleEnterCampo(e, index) {
    if (e.key !== 'Enter') return
    e.preventDefault()
    const proximo = camposRef.current[index + 1]
    if (proximo) {
      proximo.focus()
    } else {
      handleComparar()
    }
  }

  function toggle(atributo) {
    setPreset('custom')
    setSelecionados(prev =>
      prev.includes(atributo) ? prev.filter(a => a !== atributo) : [...prev, atributo]
    )
  }

  function aplicarPreset(id) {
    setPreset(id)
    setSelecionados(PRESETS[id])
  }

  async function handleComparar() {
    setErro('')

    const veiculo1 = { marca: v1.marca.trim(), modelo: v1.modelo.trim(), versao: v1.versao.trim(), ano: v1.ano.trim() }
    const veiculo2 = { marca: v2.marca.trim(), modelo: v2.modelo.trim(), versao: v2.versao.trim(), ano: v2.ano.trim() }

    if (!veiculo1.marca || !veiculo1.modelo || !veiculo1.versao || !veiculo1.ano) {
      setErro(t('pesquisa.erro_veiculo1'))
      return
    }
    if (!veiculo2.marca || !veiculo2.modelo || !veiculo2.versao || !veiculo2.ano) {
      setErro(t('pesquisa.erro_veiculo2'))
      return
    }
    if (
      veiculo1.marca.toLowerCase() === veiculo2.marca.toLowerCase() &&
      veiculo1.modelo.toLowerCase() === veiculo2.modelo.toLowerCase() &&
      veiculo1.versao.toLowerCase() === veiculo2.versao.toLowerCase() &&
      veiculo1.ano === veiculo2.ano
    ) {
      setErro(t('pesquisa.erro_iguais'))
      return
    }
    if (selecionados.length === 0) {
      setErro(t('pesquisa.erro_atributos'))
      return
    }

    setPulando(false)
    setConcluido(false)
    setLoading(true)
    try {
      const [specs1, specs2] = await Promise.all([
        buscarEspecificacoesReais(veiculo1.marca, veiculo1.modelo, veiculo1.versao, veiculo1.ano, token, selecionados),
        buscarEspecificacoesReais(veiculo2.marca, veiculo2.modelo, veiculo2.versao, veiculo2.ano, token, selecionados),
      ])

      const pesquisa = {
        tipo: 'comparacao',
        veiculo1: { ...veiculo1, specs: specs1 },
        veiculo2: { ...veiculo2, specs: specs2 },
        atributos: selecionados,
      }

      aoSalvar(pesquisa)
      setConcluido(true)
      await new Promise(r => setTimeout(r, 700))
      setResultado(pesquisa)
    } catch (err) {
      setErro(err.response?.data?.detail || 'Falha ao realizar a comparação com a IA. Tente novamente.')
    } finally {
      setLoading(false)
    }
  }

  if (resultado) {
    return <ResultadoComparacao resultado={resultado} onNova={() => setResultado(null)} />
  }

  if (loading) {
    if (pulando) {
      return (
        <div
          className="rounded-2xl p-10 flex flex-col items-center justify-center gap-4 text-center"
          style={{ background: 'linear-gradient(180deg,rgba(16,27,46,.95),rgba(9,16,29,.95))', border: '1px solid rgba(120,160,220,.14)', minHeight: 360 }}
        >
          <span className="w-6 h-6 rounded-full animate-spin" style={{ border: '2px solid rgba(30,107,255,.25)', borderTopColor: '#1e6bff' }} />
          <p className="font-mono text-xs text-[#7e90ac] uppercase tracking-[.14em]">{t('ia.extraindo')}</p>
        </div>
      )
    }
    return (
      <IAAoVivo
        marca="Duelo"
        modelo={`${v1.marca} ${v1.modelo} vs ${v2.marca} ${v2.modelo}`}
        versao=""
        ano=""
        totalAtributos={selecionados.length}
        concluido={concluido}
        onPular={() => setPulando(true)}
      />
    )
  }

  const estados = [
    { slot: SLOTS[0], state: v1, setState: setV1 },
    { slot: SLOTS[1], state: v2, setState: setV2 },
  ]

  return (
    <div className="flex flex-col gap-4">
      <div>
        <h2 className="font-sans font-extrabold text-white text-[28px] md:text-[36px] leading-none tracking-[-.03em]" style={{ fontStretch: '112%' }}>
          {t('duelo.titulo')}
        </h2>
        <p className="font-sans text-[#7e90ac] text-sm mt-2.5">{t('duelo.subtitulo')}</p>
      </div>

      <div className="flex flex-col gap-4 lg:grid lg:grid-cols-[1fr_44px_1fr] lg:gap-6 lg:items-stretch">
        <div
          className="rounded-[22px] p-6"
          style={{ background: 'linear-gradient(180deg,rgba(16,27,46,.95),rgba(9,16,29,.95))', border: '1px solid rgba(120,160,220,.14)', borderTop: `3px solid ${estados[0].slot.cor}` }}
        >
          <div className="flex items-center justify-between mb-[18px]">
            <span className="font-mono font-extrabold text-[11px] tracking-[.14em]" style={{ color: estados[0].slot.cor }}>{t(estados[0].slot.tagKey)}</span>
            <span className="font-mono text-[10px] text-[#5d6b82]">{estados[0].state.marca ? t('duelo.pronto') : t('duelo.vazio')}</span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
            {[
              { field: 'marca', label: t('pesquisa.marca'), placeholder: 'ex: Ford' },
              { field: 'modelo', label: t('pesquisa.modelo'), placeholder: 'ex: Ranger' },
              { field: 'versao', label: t('pesquisa.versao'), placeholder: 'ex: Raptor' },
              { field: 'ano', label: t('pesquisa.ano'), placeholder: 'ex: 2025' },
            ].map(({ field, label, placeholder }, i) => (
              <label key={field} className="flex flex-col gap-2">
                <span className="font-mono text-[9.5px] tracking-[.14em] text-[#6f8099] uppercase">{label}</span>
                <input
                  ref={el => (camposRef.current[i] = el)}
                  value={estados[0].state[field]}
                  onChange={e => estados[0].setState(prev => ({ ...prev, [field]: e.target.value }))}
                  onKeyDown={e => handleEnterCampo(e, i)}
                  placeholder={placeholder}
                  className="bg-[#080e1a] border border-[rgba(120,160,220,.16)] rounded-xl px-3 py-3 text-white placeholder-[#4c5a70] outline-none focus:border-[#1e6bff] transition font-semibold text-sm"
                />
              </label>
            ))}
          </div>
        </div>

        <div className="flex justify-center items-center">
          <div className="w-11 h-11 rounded-full flex items-center justify-center font-mono font-extrabold text-[15px]" style={{ background: 'rgba(245,165,36,.12)', border: '1px solid rgba(245,165,36,.3)', color: '#f5a524' }}>
            VS
          </div>
        </div>

        <div
          className="rounded-[22px] p-6"
          style={{ background: 'linear-gradient(180deg,rgba(16,27,46,.95),rgba(9,16,29,.95))', border: '1px solid rgba(120,160,220,.14)', borderTop: `3px solid ${estados[1].slot.cor}` }}
        >
          <div className="flex items-center justify-between mb-[18px]">
            <span className="font-mono font-extrabold text-[11px] tracking-[.14em]" style={{ color: estados[1].slot.cor }}>{t(estados[1].slot.tagKey)}</span>
            <span className="font-mono text-[10px] text-[#5d6b82]">{estados[1].state.marca ? t('duelo.pronto') : t('duelo.vazio')}</span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
            {[
              { field: 'marca', label: t('pesquisa.marca'), placeholder: 'ex: Toyota' },
              { field: 'modelo', label: t('pesquisa.modelo'), placeholder: 'ex: Hilux' },
              { field: 'versao', label: t('pesquisa.versao'), placeholder: 'ex: SR' },
              { field: 'ano', label: t('pesquisa.ano'), placeholder: 'ex: 2025' },
            ].map(({ field, label, placeholder }, i) => (
              <label key={field} className="flex flex-col gap-2">
                <span className="font-mono text-[9.5px] tracking-[.14em] text-[#6f8099] uppercase">{label}</span>
                <input
                  ref={el => (camposRef.current[4 + i] = el)}
                  value={estados[1].state[field]}
                  onChange={e => estados[1].setState(prev => ({ ...prev, [field]: e.target.value }))}
                  onKeyDown={e => handleEnterCampo(e, 4 + i)}
                  placeholder={placeholder}
                  className="bg-[#080e1a] border border-[rgba(120,160,220,.16)] rounded-xl px-3 py-3 text-white placeholder-[#4c5a70] outline-none focus:border-[#1e6bff] transition font-semibold text-sm"
                />
              </label>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_380px] gap-4 items-start">
        <div className="flex flex-col gap-4">
          <div className="rounded-2xl p-6" style={{ background: 'rgba(9,16,29,.9)', border: '1px solid rgba(120,160,220,.14)' }}>
            <div className="flex items-center justify-between mb-4">
              <span className="font-mono text-[10px] tracking-[.14em] text-[#6f8099] uppercase">{t('duelo.atributos_titulo')}</span>
              <span className="font-mono text-xs font-bold text-[#f5a524]">{selecionados.length}/{ATRIBUTOS.length}</span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5 mb-4">
              {PRESET_IDS.map(id => {
                const ativo = preset === id
                return (
                  <button
                    key={id}
                    onClick={() => aplicarPreset(id)}
                    className={`flex flex-col items-start gap-1.5 p-3.5 rounded-2xl border text-left transition ${
                      ativo ? 'border-[#1e6bff] bg-[#1e6bff]/15 text-white' : 'border-[rgba(120,160,220,.16)] bg-[#080e1a] text-[#8fa3c0]'
                    }`}
                  >
                    <span className="font-bold text-sm">{t(`presets.${id}`)}</span>
                    <span className="font-mono text-[10px] opacity-70">{PRESETS[id].length} {t('pesquisa.atrib_abbrev')}</span>
                  </button>
                )
              })}
            </div>

            <button
              onClick={() => setAjusteFino(v => !v)}
              className="w-full border border-dashed border-[rgba(120,160,220,.28)] rounded-xl py-2.5 text-[#8fb6ff] hover:border-[#1e6bff] hover:text-white font-mono text-[11.5px] transition"
            >
              {ajusteFino ? t('presets.fechar_ajuste') : t('presets.ajuste_fino')}
            </button>

            <div
              className="grid transition-[grid-template-rows] duration-300 ease-in-out"
              style={{ gridTemplateRows: ajusteFino ? '1fr' : '0fr' }}
            >
              <div className="overflow-hidden min-h-0">
                <div
                  className={`grid grid-cols-1 md:grid-cols-3 gap-6 mt-6 transition-opacity duration-300 ${
                    ajusteFino ? 'opacity-100 delay-100' : 'opacity-0'
                  }`}
                >
                  {Object.entries(GRUPOS_ATRIBUTOS).map(([grupoId, itens]) => (
                    <div key={grupoId}>
                      <div className="font-mono text-[9.5px] tracking-[.14em] text-[#5d6b82] uppercase mb-2.5">{t(`grupos.${grupoId}`)}</div>
                      <div className="flex flex-wrap gap-2">
                        {itens.map(atributo => {
                          const ativo = selecionados.includes(atributo)
                          return (
                            <button
                              key={atributo}
                              onClick={() => toggle(atributo)}
                              className={`px-3 py-2 rounded-full border text-sm transition ${
                                ativo ? 'border-[#1e6bff] bg-[#1e6bff]/15 text-white' : 'border-[rgba(120,160,220,.16)] bg-[#080e1a] text-[#7e90ac]'
                              }`}
                            >
                              {traduzirAtributo(atributo, i18n.language)}
                            </button>
                          )
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {erro && (
            <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/30 rounded-xl px-4 py-3">
              <span className="w-[5px] h-4 rounded bg-[#f55a5a] flex-none" />
              <p className="text-[#ff9a9a] text-sm">{erro}</p>
            </div>
          )}
        </div>

        <ResumoDuelo
          v1={v1}
          v2={v2}
          selecionados={selecionados}
          onComparar={handleComparar}
          disabled={selecionados.length === 0}
        />
      </div>
    </div>
  )
}