from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import grafos


app = FastAPI(title='Transport Graphs API')

# Allow CORS for all origins (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


app.include_router(grafos.router, prefix='/grafos', tags=['grafos'])


@app.get('/health')
def health():
    return {'status': 'ok'}
