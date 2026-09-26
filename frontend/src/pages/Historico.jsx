import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Trash2, X } from 'lucide-react'
import { obterHistorico, removerDoHistorico, limparHistorico } from '../utils/historico'
import { calcularVantagem } from '../utils/duelo'
import { capitalizarPalavras } from '../utils/texto'

function metaItem(item, t) {
  if (item.tipo === 'individual') {
    const total = Object.keys(item.specs).length
    const encontrados = Object.values(item.specs).filter(v => v !== 'Não disponível').length
    return t('historico.meta_individual', { total, encontrados })
  }
  const total = item.atributos.length
  const v1 = item.atributos.filter(a => calcularVantagem(a, item.veiculo1.specs[a], item.veiculo2.specs[a]).vencedor === 1).length
  const v2 = item.atributos.filter(a => calcularVantagem(a, item.veiculo1.specs[a], item.veiculo2.specs[a]).vencedor === 2).length
  return t('historico.meta_comparacao', { total, v1, v2 })
}

function tituloItem(item) {
  if (item.tipo === 'individual') {
    return capitalizarPalavras(`${item.marca} ${item.modelo} ${item.versao}`)
  }
  const nome1 = capitalizarPalavras(`${item.veiculo1.marca} ${item.veiculo1.modelo}`)
  const nome2 = capitalizarPalavras(`${item.veiculo2.marca} ${item.veiculo2.modelo}`)
  return `${nome1} vs ${nome2}`
}

export default function Historico() {
  const { t } = useTranslation()
  const [historico, setHistorico] = useState(() => obterHistorico())
  const navigate = useNavigate()

  function remover(id) {
    setHistorico(removerDoHistorico(id))
  }

  function limparTudo() {
    setHistorico([])
    limparHistorico()
  }

  function abrir(item) {
    const destino = item.tipo === 'comparacao' ? '/duelo' : '/'
    navigate(destino, { state: { itemHistorico: item } })
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-10 lg:py-16">

      <div className="flex items-end justify-between flex-wrap gap-4">
        <div>
          <h2 className="font-sans font-extrabold text-white text-[32px] md:text-[40px] leading-none tracking-[-.035em]" style={{ fontStretch: '112%' }}>
            {t('historico.titulo')}
          </h2>
          <p className="font-sans text-[#7e90ac] text-sm mt-2.5">
            {historico.length} {historico.length !== 1 ? t('historico.realizadas') : t('historico.realizada')}
          </p>
        </div>
        {historico.length > 0 && (
          <button
            onClick={limparTudo}
            className="flex items-center gap-2 border border-[rgba(245,90,90,.3)] hover:border-[#f55a5a] text-[#ff9a9a] hover:text-white font-mono font-semibold text-[11px] px-4 py-3 rounded-[11px] transition"
          >
            <Trash2 size={14} /> {t('historico.limpar').toUpperCase()}
          </button>
        )}
      </div>

      {historico.length === 0 ? (
        <div className="mt-7 border border-dashed border-[rgba(120,160,220,.2)] rounded-[22px] p-16 flex flex-col items-center gap-[18px]">
          <span className="font-mono text-xs text-[#5d6b82] uppercase tracking-[.1em]">{t('historico.vazio')}</span>
          <button
            onClick={() => navigate('/')}
            className="bg-[#1e6bff] hover:bg-[#3d84ff] text-white font-sans font-semibold text-sm rounded-xl px-[22px] py-3.5 transition"
          >
            {t('historico.primeira_pesquisa')}
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mt-7">
          {historico.map((item, index) => {
            const cor = item.tipo === 'comparacao' ? '#f5a524' : '#8fb6ff'
            const bg = item.tipo === 'comparacao' ? 'rgba(245,165,36,.12)' : 'rgba(30,107,255,.14)'
            return (
              <div
                key={item.id}
                onClick={() => abrir(item)}
                className="relative rounded-[20px] p-[22px] cursor-pointer transition-all duration-300 hover:border-[rgba(30,107,255,.5)] hover:-translate-y-[2px]"
                style={{
                  background: 'rgba(10,17,30,.9)',
                  border: '1px solid rgba(120,160,220,.12)',
                  borderTop: `3px solid ${cor}`,
                  animation: 'fcd-rise .4s ease both',
                  animationDelay: `${Math.min(index * 50, 400)}ms`,
                }}
              >
                <button
                  onClick={e => { e.stopPropagation(); remover(item.id) }}
                  className="absolute top-4 right-4 text-[#5d6b82] hover:text-[#ff9a9a] transition"
                >
                  <X size={15} />
                </button>

                <div className="flex items-center justify-between pr-6">
                  <span
                    className="font-mono font-bold text-[9.5px] tracking-[.12em] uppercase px-2.5 py-[7px] rounded-full"
                    style={{ color: cor, background: bg }}
                  >
                    {item.tipo === 'comparacao' ? t('historico.comparacao') : t('historico.pesquisa_individual')}
                  </span>
                  <span className="font-mono text-[10px] text-[#4c5a70]">{item.data}</span>
                </div>

                <div className="font-sans font-bold text-[17px] leading-[1.3] text-white mt-4">{tituloItem(item)}</div>
                <div className="font-mono text-[11px] text-[#6f8099] mt-3">{metaItem(item, t)}</div>
              </div>
            )
          })}
        </div>
      )}

    </div>
  )
}