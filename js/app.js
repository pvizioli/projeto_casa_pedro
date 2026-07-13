/* app.js — painel da obra Q22·L8 */
let ETAPAS = null, ETAPAS_SHA = null;
let COTS = null, COTS_SHA = null;
let ITENS = null;

const R$ = v => 'R$ ' + Number(v || 0).toLocaleString('pt-BR', { maximumFractionDigits: 0 });
const el = id => document.getElementById(id);

function msg(texto, ok = true) {
  const m = el('msg');
  m.textContent = texto;
  m.style.borderColor = ok ? 'var(--bp-green)' : 'var(--bp-amber)';
  m.style.display = 'block';
  clearTimeout(m._t);
  m._t = setTimeout(() => m.style.display = 'none', 5000);
}

/* ---------- carregamento ---------- */
async function carregar() {
  try {
    const [e, c, i] = await Promise.all([
      GH.ler('dados/etapas.json'),
      GH.ler('dados/cotacoes.json'),
      GH.ler('dados/itens.json')
    ]);
    ETAPAS = e.dados; ETAPAS_SHA = e.sha;
    COTS = c.dados; COTS_SHA = c.sha;
    ITENS = i.dados;
    renderTudo();
  } catch (err) {
    msg('Erro ao carregar dados: ' + err.message + '. Confira usuário/repo em js/github.js.', false);
  }
}

function renderTudo() {
  renderResumo();
  renderEtapas();
  renderFormCotacao();
  renderCotacoes();
  renderComparativo();
}

/* ---------- resumo ---------- */
function renderResumo() {
  const et = ETAPAS.etapas;
  const baixa = et.reduce((s, e) => s + e.estimativa_baixa, 0);
  const alta = et.reduce((s, e) => s + e.estimativa_alta, 0);
  const real = et.reduce((s, e) => s + (e.custo_real || 0), 0);
  // progresso geral ponderado pelo peso financeiro médio de cada etapa
  const pesoTotal = et.reduce((s, e) => s + (e.estimativa_baixa + e.estimativa_alta) / 2, 0);
  const prog = et.reduce((s, e) => s + (e.progresso / 100) * ((e.estimativa_baixa + e.estimativa_alta) / 2), 0) / pesoTotal * 100;
  const concluidas = et.filter(e => e.status === 'concluida').length;

  el('resumo').innerHTML = `
    <div class="grid-resumo">
      <div class="celula"><span class="lbl">Faixa estimada</span><span class="val">${R$(baixa)} – ${R$(alta)}</span></div>
      <div class="celula"><span class="lbl">Cotado / contratado</span><span class="val amber">${R$(real)}</span></div>
      <div class="celula"><span class="lbl">Etapas concluídas</span><span class="val green">${concluidas} / ${et.length}</span></div>
      <div class="celula"><span class="lbl">Cotações registradas</span><span class="val cyan">${COTS.cotacoes.length}</span></div>
    </div>
    <div class="barra"><div class="preenchido" style="width:${prog.toFixed(1)}%"></div>
      <div class="rotulo">AVANÇO GERAL ${prog.toFixed(1)}% (ponderado por custo)</div></div>`;
}

/* ---------- etapas ---------- */
function renderEtapas() {
  el('lista-etapas').innerHTML = ETAPAS.etapas.map(e => `
    <div class="etapa ${e.status}" data-id="${e.id}">
      <div class="topo">
        <div style="display:flex;gap:10px;align-items:baseline">
          <span class="num">${String(e.id).padStart(2, '0')}</span>
          <div><h3>${e.nome}</h3><div class="faixa">${R$(e.estimativa_baixa)} – ${R$(e.estimativa_alta)}</div></div>
        </div>
        <span class="badge ${e.status}">${{ nao_iniciada: 'não iniciada', em_andamento: 'em andamento', concluida: 'concluída' }[e.status]}</span>
      </div>
      <div class="obs">${e.obs}</div>
      <div class="controles">
        <label class="lbl" style="margin:0">status</label>
        <select data-campo="status">
          <option value="nao_iniciada" ${e.status === 'nao_iniciada' ? 'selected' : ''}>não iniciada</option>
          <option value="em_andamento" ${e.status === 'em_andamento' ? 'selected' : ''}>em andamento</option>
          <option value="concluida" ${e.status === 'concluida' ? 'selected' : ''}>concluída</option>
        </select>
        <label class="lbl" style="margin:0">avanço</label>
        <input type="range" min="0" max="100" step="5" value="${e.progresso}" data-campo="progresso">
        <span class="prog-val">${e.progresso}%</span>
        <label class="lbl" style="margin:0">custo real R$</label>
        <input type="number" min="0" step="100" value="${e.custo_real || 0}" data-campo="custo_real" style="width:110px">
      </div>
      <div class="mini-barra"><div style="width:${e.progresso}%"></div></div>
    </div>`).join('');

  el('lista-etapas').querySelectorAll('.etapa').forEach(card => {
    const id = +card.dataset.id;
    card.querySelectorAll('[data-campo]').forEach(ctrl => {
      ctrl.addEventListener('change', () => {
        const e = ETAPAS.etapas.find(x => x.id === id);
        const campo = ctrl.dataset.campo;
        e[campo] = campo === 'status' ? ctrl.value : +ctrl.value;
        if (campo === 'status' && ctrl.value === 'concluida') e.progresso = 100;
        if (campo === 'progresso' && +ctrl.value === 100) e.status = 'concluida';
        if (campo === 'progresso' && +ctrl.value > 0 && +ctrl.value < 100 && e.status === 'nao_iniciada') e.status = 'em_andamento';
        renderEtapas(); renderResumo(); renderComparativo();
        el('salvar-etapas').classList.remove('oculto');
      });
    });
  });
}

async function salvarEtapas() {
  const b = el('salvar-etapas');
  b.disabled = true;
  try {
    ETAPAS.atualizado = new Date().toISOString().slice(0, 10);
    const r = await GH.gravar('dados/etapas.json', ETAPAS, ETAPAS_SHA, 'Atualiza avanço das etapas');
    ETAPAS_SHA = r.content.sha;
    b.classList.add('oculto');
    msg('Avanço salvo no repositório ✓');
  } catch (err) { msg(err.message, false); }
  b.disabled = false;
}

/* ---------- cotações ---------- */
function renderFormCotacao() {
  const cats = [...new Set(ITENS.itens.map(i => i.categoria))];
  el('cot-categoria').innerHTML = cats.map(c => `<option>${c}</option>`).join('');
  atualizaItens();
  el('cot-etapa').innerHTML = ETAPAS.etapas.map(e =>
    `<option value="${e.id}">${String(e.id).padStart(2, '0')} — ${e.nome}</option>`).join('');
}

function atualizaItens() {
  const cat = el('cot-categoria').value;
  el('cot-item').innerHTML = ITENS.itens.filter(i => i.categoria === cat)
    .map(i => `<option value="${i.id}">${i.item}${i.quantidade ? ` (${i.quantidade} ${i.unidade || ''})` : ''}</option>`).join('');
  preencheQtde();
}

function preencheQtde() {
  const it = ITENS.itens.find(i => i.id === el('cot-item').value);
  if (it && it.quantidade) el('cot-qtde').value = it.quantidade;
}

async function salvarCotacao(ev) {
  ev.preventDefault();
  const b = el('btn-cotacao'); b.disabled = true;
  try {
    const it = ITENS.itens.find(i => i.id === el('cot-item').value);
    const preco = parseFloat(el('cot-preco').value);
    const qtde = parseFloat(el('cot-qtde').value) || 1;
    const c = {
      id: 'C' + String(COTS.cotacoes.length + 1).padStart(3, '0'),
      item_id: it.id, item: it.item, categoria: it.categoria,
      etapa: +el('cot-etapa').value,
      fornecedor: el('cot-fornecedor').value.trim(),
      preco_unit: preco, quantidade: qtde,
      total: +(preco * qtde).toFixed(2),
      data: new Date().toISOString().slice(0, 10),
      obs: el('cot-obs').value.trim()
    };
    COTS.cotacoes.push(c);
    const r = await GH.gravar('dados/cotacoes.json', COTS, COTS_SHA,
      `Cotação: ${c.item} — ${c.fornecedor} (${R$(c.total)})`);
    COTS_SHA = r.content.sha;
    ev.target.reset(); preencheQtde();
    renderCotacoes(); renderResumo();
    msg('Cotação commitada no repositório ✓');
  } catch (err) {
    COTS.cotacoes.pop();
    msg(err.message, false);
  }
  b.disabled = false;
}

function renderCotacoes() {
  if (!COTS.cotacoes.length) {
    el('tabela-cotacoes').innerHTML = '<p class="obs" style="color:var(--bp-dim)">Nenhuma cotação ainda. A primeira que você salvar aparece aqui e vira um commit em dados/cotacoes.json.</p>';
    return;
  }
  // marca a mais barata por item
  const melhor = {};
  COTS.cotacoes.forEach(c => {
    if (!melhor[c.item_id] || c.total < melhor[c.item_id]) melhor[c.item_id] = c.total;
  });
  const linhas = [...COTS.cotacoes].reverse().map(c => `
    <tr class="${c.total === melhor[c.item_id] && COTS.cotacoes.filter(x => x.item_id === c.item_id).length > 1 ? 'melhor' : ''}">
      <td>${c.data}</td><td>${c.item}</td><td>${c.fornecedor}</td>
      <td class="num">${c.quantidade}</td>
      <td class="num">${R$(c.preco_unit)}</td>
      <td class="num">${R$(c.total)}</td>
      <td>${c.obs || ''}</td>
    </tr>`).join('');
  el('tabela-cotacoes').innerHTML = `<table>
    <thead><tr><th>Data</th><th>Item</th><th>Fornecedor</th><th class="num">Qtde</th><th class="num">Unit.</th><th class="num">Total</th><th>Obs</th></tr></thead>
    <tbody>${linhas}</tbody></table>
    <p class="obs" style="color:var(--bp-green);font-size:11px;margin-top:6px">Linhas em verde = menor preço entre cotações do mesmo item.</p>`;
}

/* ---------- comparativo cotado × estimado ---------- */
function renderComparativo() {
  const maxAlta = Math.max(...ETAPAS.etapas.map(e => e.estimativa_alta));
  el('comparativo').innerHTML = ETAPAS.etapas.map(e => {
    const cotado = COTS.cotacoes.filter(c => c.etapa === e.id).reduce((s, c) => s + c.total, 0);
    const real = e.custo_real || cotado;
    const pB = e.estimativa_baixa / maxAlta * 100, pA = e.estimativa_alta / maxAlta * 100;
    const pR = Math.min(real / maxAlta * 100, 100);
    return `<div class="comp-linha">
      <span class="num" style="color:rgba(220,235,255,.4);font-family:'Saira Condensed';font-weight:700">${String(e.id).padStart(2, '0')}</span>
      <div class="comp-wrap">
        <div style="display:flex;justify-content:space-between;font-size:11px">
          <span>${e.nome}</span>
          <span class="${real > e.estimativa_alta ? 'amber' : real ? 'green' : ''}">${real ? R$(real) : '—'}</span>
        </div>
        <div class="comp-track">
          <div class="comp-faixa" style="left:${pB}%;width:${pA - pB}%"></div>
          ${real ? `<div class="comp-real" style="left:${pR}%"></div>` : ''}
        </div>
      </div>
      <span style="font-size:10.5px;color:var(--bp-dim)">faixa ${R$(e.estimativa_baixa)}–${R$(e.estimativa_alta)}</span>
    </div>`;
  }).join('');
}

/* ---------- token ---------- */
function configurarToken() {
  const t = prompt('Cole seu Personal Access Token (fine-grained) do GitHub.\nEle fica salvo só neste navegador.');
  if (t) { GH.setToken(t); el('token-aviso').classList.add('oculto'); msg('Token salvo. Gravações habilitadas ✓'); }
}

/* ---------- navegação ---------- */
function trocarAba(aba) {
  document.querySelectorAll('nav button[data-aba]').forEach(b => b.classList.toggle('ativo', b.dataset.aba === aba));
  document.querySelectorAll('main > section').forEach(s => s.classList.toggle('oculto', s.id !== 'aba-' + aba));
}

document.addEventListener('DOMContentLoaded', () => {
  if (GH.temToken()) el('token-aviso').classList.add('oculto');
  document.querySelectorAll('nav button[data-aba]').forEach(b => b.addEventListener('click', () => trocarAba(b.dataset.aba)));
  el('btn-token').addEventListener('click', configurarToken);
  el('salvar-etapas').addEventListener('click', salvarEtapas);
  el('form-cotacao').addEventListener('submit', salvarCotacao);
  el('cot-categoria').addEventListener('change', atualizaItens);
  el('cot-item').addEventListener('change', preencheQtde);
  carregar();
});
