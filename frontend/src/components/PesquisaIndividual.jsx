import { useState, useRef, useMemo } from 'react'
import { GRUPOS_ATRIBUTOS, PRESETS, PRESET_IDS, ATRIBUTOS } from '../data/attributesData'
import { traduzirAtributo } from '../data/attributeLabels'
import { buscarEspecificacoesReais } from '../api'
import { useAuth } from '../context/useAuth'
import { useTranslation } from 'react-i18next'
import { obterHistorico } from '../utils/historico'
import ResultadoIndividual from './ResultadoIndividual'
import ResumoConsulta from './ResumoConsulta'
import IAAoVivo from './IAAoVivo'

export default function PesquisaIndividual({ aoSalvar, itemHistorico }) {
  const { token } = useAuth()
  const { t, i18n } = useTranslation()
  const [marca, setMarca] = useState(itemHistorico?.marca || '')
  const [modelo, setModelo] = useState(itemHistorico?.modelo || '')
  const [versao, setVersao] = useState(itemHistorico?.versao || '')
  const [ano, setAno] = useState(itemHistorico?.ano || '')
  const [preset, setPreset] = useState('tudo')
  const [selecionados, setSelecionados] = useState(
    itemHistorico ? Object.keys(itemHistorico.specs) : PRESETS.tudo
  )
  const [ajusteFino, setAjusteFino] = useState(false)
  const [resultado, setResultado] = useState(itemHistorico || null)
  const [loading, setLoading] = useState(false)
  const [pulando, setPulando] = useState(false)
  const [concluido, setConcluido] = useState(false)
  const [erro, setErro] = useState('')
  const camposRef = useRef([])

  const sugestoes = useMemo(() => {
    const vistos = new Set()
    const lista = []
    for (const item of obterHistorico()) {
      if (item.tipo !== 'individual') continue
      const chave = `${item.marca}|${item.modelo}|${item.versao}|${item.ano}`
      if (vistos.has(chave)) continue
      vistos.add(chave)
      lista.push(item)
      if (lista.length >= 5) break
    }
    return lista
  }, [])

  function handleEnterCampo(e, index) {
    if (e.key !== 'Enter') return
    e.preventDefault()
    const proximo = camposRef.current[index + 1]
    if (proximo) {
      proximo.focus()
    } else {
      handleBuscar()
    }
  }

  function aplicarSugestao(item) {
    setMarca(item.marca)
    setModelo(item.modelo)
    setVersao(item.versao)
    setAno(item.ano)
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

  async function handleBuscar() {
    setErro('')
    const m = marca.trim(), mo = modelo.trim(), v = versao.trim(), a = ano.trim()

    if (!m || !mo || !v || !a) {
      setErro(t('pesquisa.erro_campos'))
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
      const specs = await buscarEspecificacoesReais(m, mo, v, a, token, selecionados)
      const pesquisa = { tipo: 'individual', marca: m, modelo: mo, versao: v, ano: a, specs }
      aoSalvar(pesquisa)
      setConcluido(true)
      await new Promise(r => setTimeout(r, 700))
      setResultado(pesquisa)
    } catch (err) {
      setErro(err.response?.data?.detail || 'Erro ao conectar com a inteligência artificial. Tente novamente.')
    } finally {
      setLoading(false)
    }
  }

  if (resultado) {
    return <ResultadoIndividual resultado={resultado} onNova={() => setResultado(null)} />
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
        marca={marca}
        modelo={modelo}
        versao={versao}
        ano={ano}
        totalAtributos={selecionados.length}
        concluido={concluido}
        onPular={() => setPulando(true)}
      />
    )
  }

  return (
    <div className="flex flex-col gap-4">
      <div>
        <h2 className="font-sans font-extrabold text-white text-[28px] md:text-[36px] leading-none tracking-[-.03em]" style={{ fontStretch: '112%' }}>
          {t('pesquisa.pagina_titulo')}
        </h2>
        <p className="font-sans text-[#7e90ac] text-sm mt-2.5">{t('pesquisa.pagina_subtitulo')}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_380px] gap-4 items-start">
        <div className="flex flex-col gap-4">
          <div className="rounded-2xl p-6" style={{ background: 'linear-gradient(180deg,rgba(16,27,46,.95),rgba(9,16,29,.95))', border: '1px solid rgba(120,160,220,.14)' }}>
            <div className="font-mono text-[10px] tracking-[.14em] text-[#6f8099] uppercase mb-4">{t('pesquisa.identificacao_veiculo')}</div>

            <div className="mb-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                {[
                  { label: t('pesquisa.marca'), value: marca, set: setMarca, placeholder: t('pesquisa.placeholder_marca') },
                  { label: t('pesquisa.modelo'), value: modelo, set: setModelo, placeholder: t('pesquisa.placeholder_modelo') },
                  { label: t('pesquisa.versao'), value: versao, set: setVersao, placeholder: t('pesquisa.placeholder_versao') },
                  { label: t('pesquisa.ano'), value: ano, set: setAno, placeholder: t('pesquisa.placeholder_ano') },
                ].map(({ label, value, set, placeholder }, index) => (
                  <div key={label} className="flex flex-col gap-2">
                    <label className="font-mono text-[9.5px] tracking-[.14em] text-[#6f8099] uppercase">{label}</label>
                    <input
                      ref={el => (camposRef.current[index] = el)}
                      placeholder={placeholder}
                      value={value}
                      onChange={e => set(e.target.value)}
                      onKeyDown={e => handleEnterCampo(e, index)}
                      className="bg-[#080e1a] border border-[rgba(120,160,220,.16)] rounded-xl px-4 py-3.5 text-white placeholder-[#4c5a70] outline-none focus:border-[#1e6bff] transition font-semibold"
                    />
                  </div>
                ))}
              </div>

              {sugestoes.length > 0 && (
                <div className="flex flex-wrap gap-[7px] mt-3">
                  {sugestoes.map((s, i) => (
                    <button
                      key={i}
                      onClick={() => aplicarSugestao(s)}
                      className="rounded-full px-3 py-[7px] font-mono text-[11.5px] transition"
                      style={{ background: 'rgba(30,107,255,.1)', border: '1px solid rgba(30,107,255,.28)', color: '#8fb6ff' }}
                    >
                      {s.modelo} {s.versao} {String(s.ano).slice(-2)}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div className="flex items-center justify-between mb-4">
              <span className="font-mono text-[10px] tracking-[.14em] text-[#6f8099] uppercase">{t('presets.titulo')}</span>
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

        <ResumoConsulta
          marca={marca}
          modelo={modelo}
          versao={versao}
          ano={ano}
          selecionados={selecionados}
          onExtrair={handleBuscar}
          disabled={selecionados.length === 0}
        />
      </div>
    </div>
  )
}