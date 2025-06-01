import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.insert(0, PROJECT_ROOT)
from src.infraestructure.persistence.database.init import init_database
from src.infraestructure.api.routers import process_router, ctq_router, study_router
print("Inicializando base de datos...")
init_database()
# Crear instancia de la aplicación FastAPI
app = FastAPI(
    title="API Analizador de Capacidad de Procesos",
    description="API para calcular y gestionar índices de capacidad (Cp, Cpk, Cpm, etc.)",
    version="0.1.0"
)

# Configurar CORS (Cross-Origin Resource Sharing)
origins = os.getenv('ALLOWED_ORIGINS', '*').split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Lista de orígenes permitidos
    allow_credentials=True, # Permitir cookies (si usas autenticación basada en cookies)
    allow_methods=["*"],    # Permitir todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],    # Permitir todas las cabeceras
)


# Incluir los routers en la aplicación principal
app.include_router(process_router.router) # El router de procesos que creamos antes
app.include_router(ctq_router.router)
app.include_router(study_router.router) # El router de estudios que creamos antes


# Endpoint raíz simple para verificar que la API está funcionando
@app.get("/", tags=["Root"])
async def read_root():
    """Endpoint raíz de bienvenida."""
    return {"message": "Bienvenido a la API del Analizador de Capacidad v0.1.0"}

