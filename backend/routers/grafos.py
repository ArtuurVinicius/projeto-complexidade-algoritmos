from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional

from backend.models.schemas import GraphCreateRequest
from backend.services import generate_graph, list_graphs, get_graph_entry, graph_to_json, delete_graph

router = APIRouter()


@router.post('/gerar')
def gerar_grafo(payload: GraphCreateRequest):
    params = payload.dict()
    try:
        meta = generate_graph(params)
        return JSONResponse(content=meta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/')
def listar_grafos(page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=200)):
    data = list_graphs(page=page, per_page=per_page)
    return JSONResponse(content=data)


@router.get('/{graph_id}')
def obter_grafo(graph_id: str, format: Optional[str] = Query('json'), max_nodes: int = Query(5000, ge=10)):
    entry = get_graph_entry(graph_id)
    if not entry:
        raise HTTPException(status_code=404, detail='Grafo não encontrado')

    if format in ('gpickle', 'file'):
        # return file download
        file_path = entry['filename']
        return FileResponse(path=file_path, filename=f"{graph_id}.gpickle", media_type='application/octet-stream')

    # default: return JSON serialized graph (D3-like)
    data = graph_to_json(graph_id, max_nodes=max_nodes)
    if data is None:
        raise HTTPException(status_code=404, detail='Grafo não encontrado ou corrompido')
    return JSONResponse(content=data)


@router.delete('/{graph_id}')
def deletar_grafo(graph_id: str):
    ok = delete_graph(graph_id)
    if not ok:
        raise HTTPException(status_code=404, detail='Grafo não encontrado')
    return JSONResponse(status_code=204, content={})
