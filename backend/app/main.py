from __future__ import annotations
from typing import Any
from uuid import UUID, uuid4
import httpx
from fastapi import FastAPI, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    supabase_url: str = ""
    supabase_publishable_key: str = ""
    cors_origins: str = "http://localhost:8080"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

settings = Settings()
app = FastAPI(title="ControleParaOsPais API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()], allow_credentials=False, allow_methods=["GET", "POST", "DELETE", "OPTIONS"], allow_headers=["Authorization", "Content-Type"])

class DeviceInput(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    note: str = Field(default="", max_length=160)

async def authenticated_user(authorization: str | None) -> dict[str, Any]:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Faça login para continuar.")
    token = authorization.split(" ", 1)[1].strip()
    if not token or not settings.supabase_url or not settings.supabase_publishable_key:
        raise HTTPException(status_code=401, detail="Token ausente ou backend não configurado.")
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(settings.supabase_url.rstrip("/") + "/auth/v1/user", headers={"apikey": settings.supabase_publishable_key, "Authorization": f"Bearer {token}"})
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail="Não foi possível validar a sessão.") from exc
    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Sessão inválida ou expirada.")
    user = resp.json()
    if not user.get("id"):
        raise HTTPException(status_code=401, detail="Usuário não identificado.")
    return user

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "ControleParaOsPais API"}

@app.get("/api/me")
async def me(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = await authenticated_user(authorization)
    return {"id": user["id"], "email": user.get("email")}

# Scaffold local: esta lista é temporária e desaparece quando o processo reinicia.
# Para produção, use tabelas Supabase com RLS; ver supabase/schema.sql.
_devices: dict[str, list[dict[str, str]]] = {}

@app.get("/api/devices")
async def get_devices(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user = await authenticated_user(authorization)
    return {"devices": _devices.get(user["id"], [])}

@app.post("/api/devices", status_code=201)
async def add_device(payload: DeviceInput, authorization: str | None = Header(default=None)) -> dict[str, str]:
    user = await authenticated_user(authorization)
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="Informe o nome do dispositivo.")
    row = {"id": str(uuid4()), "name": name, "note": payload.note.strip()}
    _devices.setdefault(user["id"], []).append(row)
    return row

@app.delete("/api/devices/{device_id}", status_code=204)
async def delete_device(device_id: UUID, authorization: str | None = Header(default=None)) -> Response:
    user = await authenticated_user(authorization)
    _devices[user["id"]] = [d for d in _devices.get(user["id"], []) if d["id"] != str(device_id)]
    return Response(status_code=204)
