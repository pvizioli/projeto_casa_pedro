#!/usr/bin/env bash
# Regera a planilha a partir de dados/*.json e publica no repositório.
# Feito para o GitHub Actions. Tolera corrida: se alguém (o site) commitar
# enquanto o robô roda, ele refaz a planilha sobre o estado novo e tenta de novo.
set -uo pipefail

gerar() {
  python scripts/build_planilha.py || return 1
  # LibreOffice já vem no runner: recalcula e grava os valores em cache
  rm -rf /tmp/recalc && mkdir -p /tmp/recalc
  if soffice --headless --calc --convert-to xlsx --outdir /tmp/recalc \
       planilha-q22-l8.xlsx >/dev/null 2>&1 && [ -s /tmp/recalc/planilha-q22-l8.xlsx ]; then
    mv /tmp/recalc/planilha-q22-l8.xlsx planilha-q22-l8.xlsx
    echo "Fórmulas recalculadas."
  else
    echo "Recalc indisponível — Excel/Sheets recalculam ao abrir."
  fi
}

for tentativa in 1 2 3; do
  git fetch -q origin main
  git checkout -q -B main origin/main   # sempre parte do estado mais recente
  gerar || { echo "Falha ao gerar a planilha."; exit 1; }

  git add planilha-q22-l8.xlsx
  if git diff --staged --quiet; then
    echo "Planilha sem alterações."
    exit 0
  fi

  git commit -q -m "Planilha atualizada automaticamente [skip ci]"
  if git push -q origin main 2>/dev/null; then
    echo "Planilha publicada (tentativa $tentativa)."
    exit 0
  fi
  echo "Push rejeitado — alguém commitou antes. Refazendo… ($tentativa/3)"
  sleep 5
done

echo "Não foi possível publicar após 3 tentativas."
exit 1
