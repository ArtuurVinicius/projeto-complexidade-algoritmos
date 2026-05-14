import json
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

# Caminho do arquivo de resultados
RESULTS_PATH = os.path.join("dados_coletados", "resultados_simulacoes.json")

with open(RESULTS_PATH, encoding="utf-8") as f:
    resultados = json.load(f)

cenarios = [r["cenario"] for r in resultados]
algoritmos = ["dijkstra", "astar", "multiobjetivo"]

# Extrair tempos (minutos)
tempos = {alg: [r[alg]["tempo_min"] if alg in r and "tempo_min" in r[alg] else None for r in resultados] for alg in algoritmos}

# Preparar dados
x = np.arange(len(cenarios))
y_vals = {alg: np.array([v if v is not None else np.nan for v in tempos[alg]]) for alg in algoritmos}

# Scatter plot
fig, ax = plt.subplots(figsize=(max(10, len(cenarios)*0.35), 6))
markers = {"dijkstra": "o", "astar": "s", "multiobjetivo": "^"}
colors = {"dijkstra": "#1f77b4", "astar": "#ff7f0e", "multiobjetivo": "#2ca02c"}
offsets = {"dijkstra": -0.15, "astar": 0.0, "multiobjetivo": 0.15}
for alg in algoritmos:
    ax.scatter(x + offsets[alg], y_vals[alg], label=alg.title(), marker=markers[alg], color=colors[alg], alpha=0.9, s=40)

ax.set_ylabel('Tempo (minutos)')
ax.set_title('Scatter: Tempo por algoritmo e cenário')
ax.set_xticks(x)
# reduzir etiquetas se houver muitos cenários
if len(cenarios) > 25:
    labels = ['' if (i % 2 == 1) else s for i, s in enumerate(cenarios)]
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=7)
    mapping_file = 'cenario_index_mapping_scatter.txt'
    with open(mapping_file, 'w', encoding='utf-8') as mf:
        for i, s in enumerate(cenarios):
            mf.write(f"{i}: {s}\n")
else:
    ax.set_xticklabels(cenarios, rotation=45, ha='right', fontsize=8)

ax.grid(axis='y', linestyle='--', alpha=0.4)
ax.legend()
plt.tight_layout()
plt.savefig("grafico_simulacoes_scatter.png", dpi=200, bbox_inches='tight')
print('Arquivo salvo: grafico_simulacoes_scatter.png')
if 'mapping_file' in locals() and os.path.exists(mapping_file):
    print(f'Mapeamento de cenários salvo em: {mapping_file}')
plt.show()

# Line chart
fig, ax = plt.subplots(figsize=(max(10, len(cenarios)*0.35), 6))
for alg in algoritmos:
    ax.plot(x, y_vals[alg], label=alg.title(), marker=markers[alg], color=colors[alg])

ax.set_ylabel('Tempo (minutos)')
ax.set_title('Line Chart: Tempo por algoritmo e cenário')
ax.set_xticks(x)
ax.set_xticklabels(cenarios, rotation=75, ha='right', fontsize=8)
ax.grid(True, linestyle='--', alpha=0.4)
ax.legend()
plt.tight_layout()
plt.savefig("grafico_simulacoes_line.png", dpi=200, bbox_inches='tight')
plt.show()
