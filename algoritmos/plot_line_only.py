import json
import matplotlib
matplotlib.use('Agg')  # backend não interativo para salvar imagens sem exibir
import matplotlib.pyplot as plt
# tentar aplicar um estilo; se o estilo não existir no ambiente, usar fallback
try:
    plt.style.use('seaborn-whitegrid')
except Exception:
    try:
        plt.style.use('ggplot')
    except Exception:
        pass
import numpy as np
import os

RESULTS_PATH = os.path.join("dados_coletados", "resultados_simulacoes.json")
OUT_FILE = "grafico_simulacoes_line.png"

with open(RESULTS_PATH, encoding="utf-8") as f:
    resultados = json.load(f)

cenarios = [r["cenario"] for r in resultados]
algoritmos = ["dijkstra", "astar", "multiobjetivo"]

# Extrair tempos (minutos) e tratar None
tempos = {alg: [r[alg]["tempo_min"] if alg in r and "tempo_min" in r[alg] else np.nan for r in resultados] for alg in algoritmos}

x = np.arange(len(cenarios))
markers = {"dijkstra": "o", "astar": "s", "multiobjetivo": "^"}
colors = {"dijkstra": "#1f77b4", "astar": "#ff7f0e", "multiobjetivo": "#2ca02c"}

fig, ax = plt.subplots(figsize=(max(10, len(cenarios)*0.4), 6))
for alg in algoritmos:
    y = np.array(tempos[alg], dtype=float)
    ax.plot(x, y, label=alg.title(), marker=markers[alg], color=colors[alg], linewidth=1.5, markersize=5, alpha=0.9)

ax.set_ylabel('Tempo (minutos)')
ax.set_title('Line Chart: Tempo por algoritmo e cenário')
ax.set_xticks(x)
# reduzir etiquetas se houver muitos cenários para evitar poluição
if len(cenarios) > 25:
    # mostrar apenas índices pares para rótulos longos
    labels = ['' if (i % 2 == 1) else s for i, s in enumerate(cenarios)]
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=7)
    # adicionar legenda de legenda numérica no topo (índice -> cenário) salvamos mapping
    mapping_file = 'cenario_index_mapping.txt'
    with open(mapping_file, 'w', encoding='utf-8') as mf:
        for i, s in enumerate(cenarios):
            mf.write(f"{i}: {s}\n")
else:
    ax.set_xticklabels(cenarios, rotation=45, ha='right', fontsize=8)
ax.grid(True, linestyle='--', alpha=0.4)
ax.legend()
plt.tight_layout()
plt.savefig(OUT_FILE, dpi=200, bbox_inches='tight')
print(f'Arquivo salvo: {OUT_FILE}')
if 'mapping_file' in locals() and os.path.exists(mapping_file):
    print(f'Mapeamento de cenários salvo em: {mapping_file}')
