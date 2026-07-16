# Residência Q22·L8 — Painel de Obra

Site estático (GitHub Pages) para acompanhar a construção: avanço das 13 etapas,
registro de cotações de fornecedores e comparativo cotado × estimado.
Cada gravação feita pelo site vira um **commit** nos arquivos `dados/*.json`.

## Estrutura

```
projeto_casa_pedro/
├── index.html            → painel (etapas, cotações, comparativo)
├── blueprints.html       → as 6 folhas do estudo preliminar (F-01–F-06)
├── css/estilo.css
├── js/
│   ├── github.js         → leitura/escrita via API do GitHub (⚠ ajustar owner/repo)
│   └── app.js
└── dados/
    ├── etapas.json       → 13 etapas c/ faixa de custo, status, % e custo real
    ├── itens.json        → catálogo de 116 itens cotáveis (da planilha)
    └── cotacoes.json     → cotações registradas pelo site
```

## Montagem — passo a passo

### 1. Criar o repositório
1. GitHub → **New repository** → nome `projeto_casa_pedro` → **Private** → Create.
2. Envie todos os arquivos desta pasta (arraste na página "uploading an existing file"
   ou via git: `git init && git add . && git commit -m "Painel inicial" && git push`).
3. **Renomeie seu arquivo de blueprints para `blueprints.html`** e suba junto.

### 2. Ajustar o site para o seu repositório
Abra `js/github.js` e edite as duas primeiras linhas:
```js
owner: 'SEU_USUARIO',        // ← seu usuário do GitHub
repo:  'projeto_casa_pedro',
```

### 3. Ativar o GitHub Pages
Repo → **Settings → Pages** → Source: `Deploy from a branch` →
Branch: `main` / `/ (root)` → Save.
O site fica em `https://SEU_USUARIO.github.io/projeto_casa_pedro/`.

> Repositório privado: Pages exige plano Pro. Alternativas grátis: deixar o repo
> público (os valores das cotações ficam visíveis) ou abrir o `index.html`
> localmente no navegador — a API funciona do mesmo jeito.

### 4. Gerar o token (grava as cotações)
1. GitHub → foto de perfil → **Settings → Developer settings →
   Personal access tokens → Fine-grained tokens → Generate new token**.
2. Repository access: **Only select repositories** → `projeto_casa_pedro`.
3. Permissions → Repository permissions → **Contents: Read and write**. Só isso.
4. Expiração: 90 dias (renova depois). Gere e copie.
5. No site, clique **Token** e cole. Fica salvo apenas no seu navegador.
   **Nunca commite o token em nenhum arquivo.**

### 5. Usar
- **Etapas**: mude status/avanço/custo real → botão *Salvar avanço* (1 commit).
- **Cotações**: escolha categoria → item (quantidade já vem da planilha) →
  fornecedor e preço → *Salvar cotação* (1 commit). Com 2+ cotações do mesmo
  item, a mais barata fica verde.
- **Comparativo**: faixa estimada por etapa vs. custo real/cotado.

## Planilha automática

`planilha-q22-l8.xlsx` é **gerada pelo GitHub Actions**, nunca à mão.

Fluxo: você lança uma cotação no site → o site commita `dados/cotacoes.json` →
o workflow `.github/workflows/planilha.yml` dispara → `scripts/build_planilha.py`
lê os JSONs, monta o .xlsx (Resumo, Etapas, Itens, Cotações, Comparativo, Revisões),
o LibreOffice recalcula as fórmulas e o bot commita o arquivo → o link
**⤓ Planilha .xlsx** no painel passa a servir a versão nova (~1 min).

Editar o .xlsx à mão é inútil: a próxima geração sobrescreve. A fonte é o site.

Se o workflow não aparecer em Actions, confira que o arquivo
`.github/workflows/planilha.yml` está no repositório (um token sem permissão de
*Workflows* não consegue enviá-lo — nesse caso, suba-o pela interface do GitHub).

## Observações
- Os dados continuam legíveis no repo (JSON) — dá para versionar, reverter e
  auditar qualquer cotação pelo histórico de commits.
- O celular funciona normalmente: mesmo site, mesmo token.
- Se duas pessoas gravarem ao mesmo tempo pode dar conflito de `sha`;
  basta recarregar a página e salvar de novo.
