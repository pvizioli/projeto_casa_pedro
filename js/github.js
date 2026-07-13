/* github.js — leitura e escrita de arquivos JSON direto no repositório
 * Usa a API de conteúdo do GitHub (contents API). Cada gravação vira um commit.
 * O token fica só no navegador (localStorage) — nunca é commitado.
 */
const GH = {
  // >>> AJUSTE AQUI <<<
  owner: 'pvizioli',          // seu usuário do GitHub
  repo: 'projeto_casa_pedro',     // nome do repositório
  branch: 'main',

  token() { return localStorage.getItem('gh_token') || ''; },
  setToken(t) { localStorage.setItem('gh_token', t.trim()); },
  temToken() { return !!this.token(); },

  url(caminho) {
    return `https://api.github.com/repos/${this.owner}/${this.repo}/contents/${caminho}?ref=${this.branch}`;
  },

  cabecalhos() {
    const h = { 'Accept': 'application/vnd.github+json' };
    if (this.token()) h['Authorization'] = `Bearer ${this.token()}`;
    return h;
  },

  // Lê um JSON do repositório. Retorna { dados, sha }.
  async ler(caminho) {
    const r = await fetch(this.url(caminho), { headers: this.cabecalhos(), cache: 'no-store' });
    if (!r.ok) throw new Error(`Falha ao ler ${caminho} (HTTP ${r.status})`);
    const j = await r.json();
    const texto = decodeURIComponent(escape(atob(j.content.replace(/\n/g, ''))));
    return { dados: JSON.parse(texto), sha: j.sha };
  },

  // Grava (commita) um JSON. Precisa do sha atual do arquivo.
  async gravar(caminho, dados, sha, mensagem) {
    const conteudo = btoa(unescape(encodeURIComponent(JSON.stringify(dados, null, 2))));
    const r = await fetch(this.url(caminho).split('?')[0], {
      method: 'PUT',
      headers: { ...this.cabecalhos(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: mensagem, content: conteudo, sha, branch: this.branch })
    });
    if (!r.ok) {
      const e = await r.json().catch(() => ({}));
      throw new Error(`Falha ao gravar ${caminho}: ${e.message || 'HTTP ' + r.status}`);
    }
    return r.json();
  }
};
