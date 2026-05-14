"""
Coleta de dados de transporte público de Recife via OpenStreetMap (Overpass API).
Coleta paradas de ônibus, estações de metrô, ciclovias e vias para pedestres
na região entre Cinema São Luiz (Boa Vista) e Faculdade Nova Roma (Boa Viagem).
"""

import requests
import json
import os
import time

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
DATA_DIR = "dados_coletados"

# Bounding box cobrindo de Boa Vista até Boa Viagem (Recife-PE)
# Formato Overpass: sul, oeste, norte, leste
BBOX = "-8.1300, -34.9100, -8.0500, -34.8700"

# Coordenadas dos pontos de origem e destino
CINEMA_SAO_LUIZ = {"lat": -8.0631, "lon": -34.8771, "nome": "Cinema São Luiz (Boa Vista)"}
FACULDADE_NOVA_ROMA = {"lat": -8.1197, "lon": -34.9014, "nome": "Faculdade Nova Roma (Boa Viagem)"}


def salvar_json(dados, nome_arquivo):
    """Salva dados em arquivo JSON na pasta de dados."""
    os.makedirs(DATA_DIR, exist_ok=True)
    caminho = os.path.join(DATA_DIR, nome_arquivo)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f"  -> Salvo em: {caminho}")


def consultar_overpass(query, descricao="", max_tentativas=3):
    """Executa uma consulta na Overpass API com retry e tratamento de erros."""
    print(f"\n{'='*60}")
    print(f"  Coletando: {descricao}")
    print(f"{'='*60}")
    for tentativa in range(1, max_tentativas + 1):
        try:
            response = requests.post(OVERPASS_URL, data={"data": query}, timeout=180)
            response.raise_for_status()
            dados = response.json()
            total = len(dados.get("elements", []))
            print(f"  Elementos encontrados: {total}")
            return dados
        except requests.exceptions.RequestException as e:
            print(f"  Tentativa {tentativa}/{max_tentativas} falhou: {e}")
            if tentativa < max_tentativas:
                espera = 10 * tentativa
                print(f"  Aguardando {espera}s antes de tentar novamente...")
                time.sleep(espera)
    print(f"  ERRO: Todas as {max_tentativas} tentativas falharam.")
    return {"elements": []}


# ============================================================================
# 1. PARADAS DE ÔNIBUS
# ============================================================================

def coletar_paradas_onibus():
    """Coleta todas as paradas de ônibus na região."""
    query = f"""
    [out:json][timeout:60];
    (
      node["highway"="bus_stop"]({BBOX});
      node["public_transport"="platform"]["bus"="yes"]({BBOX});
      node["public_transport"="stop_position"]["bus"="yes"]({BBOX});
    );
    out body;
    """
    dados = consultar_overpass(query, "Paradas de Ônibus")
    paradas = []
    for el in dados.get("elements", []):
        parada = {
            "id": el["id"],
            "lat": el["lat"],
            "lon": el["lon"],
            "nome": el.get("tags", {}).get("name", "Sem nome"),
            "operador": el.get("tags", {}).get("operator", ""),
            "rede": el.get("tags", {}).get("network", ""),
            "ref": el.get("tags", {}).get("ref", ""),
            "tipo": "parada_onibus"
        }
        paradas.append(parada)
    salvar_json(paradas, "paradas_onibus.json")
    return paradas


# ============================================================================
# 2. ESTAÇÕES DE METRÔ
# ============================================================================

def coletar_estacoes_metro():
    """Coleta estações de metrô/trem na região."""
    query = f"""
    [out:json][timeout:60];
    (
      node["railway"="station"]({BBOX});
      node["railway"="halt"]({BBOX});
      node["station"="subway"]({BBOX});
      node["public_transport"="station"]({BBOX});
    );
    out body;
    """
    dados = consultar_overpass(query, "Estações de Metrô/Trem")
    estacoes = []
    for el in dados.get("elements", []):
        estacao = {
            "id": el["id"],
            "lat": el["lat"],
            "lon": el["lon"],
            "nome": el.get("tags", {}).get("name", "Sem nome"),
            "operador": el.get("tags", {}).get("operator", ""),
            "linha": el.get("tags", {}).get("line", ""),
            "tipo": "estacao_metro"
        }
        estacoes.append(estacao)
    salvar_json(estacoes, "estacoes_metro.json")
    return estacoes


# ============================================================================
# 3. LINHAS DE ÔNIBUS (ROTAS)
# ============================================================================

def coletar_linhas_onibus():
    """Coleta rotas/linhas de ônibus que passam na região."""
    query = f"""
    [out:json][timeout:90];
    (
      relation["type"="route"]["route"="bus"]({BBOX});
    );
    out body geom;
    """
    dados = consultar_overpass(query, "Linhas de Ônibus (rotas)")
    linhas = []
    for el in dados.get("elements", []):
        tags = el.get("tags", {})
        linha = {
            "id": el["id"],
            "ref": tags.get("ref", ""),
            "nome": tags.get("name", "Sem nome"),
            "operador": tags.get("operator", ""),
            "rede": tags.get("network", ""),
            "de": tags.get("from", ""),
            "para": tags.get("to", ""),
            "tipo": "linha_onibus"
        }
        # Extrair geometria da rota
        membros_paradas = []
        for membro in el.get("members", []):
            if membro.get("role") in ("stop", "platform") and "lat" in membro and "lon" in membro:
                membros_paradas.append({
                    "ref": membro.get("ref", ""),
                    "lat": membro["lat"],
                    "lon": membro["lon"],
                    "role": membro["role"]
                })
        linha["paradas"] = membros_paradas
        linhas.append(linha)
    salvar_json(linhas, "linhas_onibus.json")
    return linhas


# ============================================================================
# 4. LINHAS DE METRÔ (ROTAS)
# ============================================================================

def coletar_linhas_metro():
    """Coleta rotas de metrô/trem na região."""
    query = f"""
    [out:json][timeout:90];
    (
      relation["type"="route"]["route"="subway"]({BBOX});
      relation["type"="route"]["route"="light_rail"]({BBOX});
      relation["type"="route"]["route"="train"]({BBOX});
    );
    out body geom;
    """
    dados = consultar_overpass(query, "Linhas de Metrô/Trem")
    linhas = []
    for el in dados.get("elements", []):
        tags = el.get("tags", {})
        linha = {
            "id": el["id"],
            "ref": tags.get("ref", ""),
            "nome": tags.get("name", "Sem nome"),
            "operador": tags.get("operator", ""),
            "de": tags.get("from", ""),
            "para": tags.get("to", ""),
            "tipo": "linha_metro"
        }
        membros_estacoes = []
        for membro in el.get("members", []):
            if membro.get("role") in ("stop", "platform") and "lat" in membro and "lon" in membro:
                membros_estacoes.append({
                    "ref": membro.get("ref", ""),
                    "lat": membro["lat"],
                    "lon": membro["lon"],
                    "role": membro["role"]
                })
        linha["estacoes"] = membros_estacoes
        linhas.append(linha)
    salvar_json(linhas, "linhas_metro.json")
    return linhas


# ============================================================================
# 5. CICLOVIAS
# ============================================================================

def coletar_ciclovias():
    """Coleta ciclovias e ciclofaixas na região."""
    query = f"""
    [out:json][timeout:60];
    (
      way["highway"="cycleway"]({BBOX});
      way["cycleway"="lane"]({BBOX});
      way["cycleway"="track"]({BBOX});
      way["cycleway:left"~"."]({BBOX});
      way["cycleway:right"~"."]({BBOX});
    );
    out body geom;
    """
    dados = consultar_overpass(query, "Ciclovias e Ciclofaixas")
    ciclovias = []
    for el in dados.get("elements", []):
        tags = el.get("tags", {})
        ciclovia = {
            "id": el["id"],
            "nome": tags.get("name", ""),
            "tipo_via": tags.get("highway", tags.get("cycleway", "")),
            "superficie": tags.get("surface", ""),
            "geometria": el.get("geometry", []),
            "tipo": "ciclovia"
        }
        ciclovias.append(ciclovia)
    salvar_json(ciclovias, "ciclovias.json")
    return ciclovias


# ============================================================================
# 6. VIAS PARA PEDESTRES (CALÇADAS E CAMINHOS)
# ============================================================================

def coletar_vias_pedestres():
    """Coleta vias para pedestres (calçadas, passarelas, etc.)."""
    query = f"""
    [out:json][timeout:60];
    (
      way["highway"="footway"]({BBOX});
      way["highway"="pedestrian"]({BBOX});
      way["highway"="path"]["foot"="yes"]({BBOX});
      way["foot"="designated"]({BBOX});
    );
    out body geom;
    """
    dados = consultar_overpass(query, "Vias para Pedestres")
    vias = []
    for el in dados.get("elements", []):
        tags = el.get("tags", {})
        via = {
            "id": el["id"],
            "nome": tags.get("name", ""),
            "tipo_via": tags.get("highway", ""),
            "superficie": tags.get("surface", ""),
            "geometria": el.get("geometry", []),
            "tipo": "via_pedestre"
        }
        vias.append(via)
    salvar_json(vias, "vias_pedestres.json")
    return vias


# ============================================================================
# 7. REDE VIÁRIA PRINCIPAL (RUAS E AVENIDAS)
# ============================================================================

def coletar_rede_viaria():
    """Coleta a rede viária principal (ruas, avenidas) em duas partes para evitar timeout."""
    # Parte 1: vias principais (primary, secondary, trunk)
    query1 = f"""
    [out:json][timeout:120];
    (
      way["highway"~"^(primary|secondary|trunk)$"]({BBOX});
    );
    out body geom;
    """
    dados1 = consultar_overpass(query1, "Rede Viária - Vias Principais")
    time.sleep(3)

    # Parte 2: vias secundárias (tertiary, residential)
    query2 = f"""
    [out:json][timeout:120];
    (
      way["highway"~"^(tertiary|residential)$"]({BBOX});
    );
    out body geom;
    """
    dados2 = consultar_overpass(query2, "Rede Viária - Vias Secundárias")

    # Combinar resultados
    dados = {"elements": dados1.get("elements", []) + dados2.get("elements", [])}
    vias = []
    for el in dados.get("elements", []):
        tags = el.get("tags", {})
        via = {
            "id": el["id"],
            "nome": tags.get("name", "Sem nome"),
            "tipo_via": tags.get("highway", ""),
            "mao_unica": tags.get("oneway", "no"),
            "faixas": tags.get("lanes", ""),
            "velocidade_max": tags.get("maxspeed", ""),
            "superficie": tags.get("surface", ""),
            "geometria": el.get("geometry", []),
            "tipo": "via_principal"
        }
        vias.append(via)
    salvar_json(vias, "rede_viaria.json")
    return vias


# ============================================================================
# EXECUÇÃO PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  COLETA DE DADOS DE TRANSPORTE - RECIFE/PE")
    print(f"  Origem: {CINEMA_SAO_LUIZ['nome']}")
    print(f"  Destino: {FACULDADE_NOVA_ROMA['nome']}")
    print(f"  Bounding Box: {BBOX}")
    print("=" * 60)

    resultados = {}

    # Coletar cada tipo de dado com pausa entre requisições
    # (a Overpass API limita requisições simultâneas)
    resultados["paradas_onibus"] = coletar_paradas_onibus()
    time.sleep(5)

    resultados["estacoes_metro"] = coletar_estacoes_metro()
    time.sleep(5)

    resultados["linhas_onibus"] = coletar_linhas_onibus()
    time.sleep(5)

    resultados["linhas_metro"] = coletar_linhas_metro()
    time.sleep(5)

    resultados["ciclovias"] = coletar_ciclovias()
    time.sleep(5)

    resultados["vias_pedestres"] = coletar_vias_pedestres()
    time.sleep(5)

    resultados["rede_viaria"] = coletar_rede_viaria()

    # Resumo final
    print("\n" + "=" * 60)
    print("  RESUMO DA COLETA")
    print("=" * 60)
    for categoria, dados in resultados.items():
        print(f"  {categoria:20s}: {len(dados):5d} elementos")

    # Salvar resumo com metadados
    resumo = {
        "origem": CINEMA_SAO_LUIZ,
        "destino": FACULDADE_NOVA_ROMA,
        "bbox": BBOX,
        "totais": {k: len(v) for k, v in resultados.items()},
        "total_geral": sum(len(v) for v in resultados.values())
    }
    salvar_json(resumo, "resumo_coleta.json")

    print(f"\n  Total geral: {resumo['total_geral']} elementos coletados")
    print(f"  Dados salvos na pasta: {DATA_DIR}/")
    print("=" * 60)
