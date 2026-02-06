import time
import httpx
from app.config import settings

_token_cache = {"value": None, "exp": 0}

async def _get_token() -> str:
    now = time.time()
    if _token_cache["value"] and now < _token_cache["exp"] - 30:
        return _token_cache["value"]

    async with httpx.AsyncClient(base_url=settings.SYNC_BASE_URL, timeout=20) as client:
        r = await client.post("/api/partner/v1/auth-token", json={
            "client_id": settings.SYNC_CLIENT_ID,
            "client_secret": settings.SYNC_CLIENT_SECRET
        })
        r.raise_for_status()
        data = r.json()
        token = data["access_token"]
        expires_in = int(data.get("expires_in", 3600))
        _token_cache["value"] = token
        _token_cache["exp"] = now + expires_in
        return token

async def create_pix_cash_in(amount_brl: float, description: str, client_data: dict) -> dict:
    token = await _get_token()
    async with httpx.AsyncClient(base_url=settings.SYNC_BASE_URL, timeout=20) as client:
        r = await client.post(
            "/api/partner/v1/cash-in",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            json={
                "amount": amount_brl,
                "description": description,
                "webhook_url": settings.BASE_URL.rstrip("/") + "/syncpay/webhook",
                "client": client_data
            }
        )
        r.raise_for_status()
        return r.json()

async def get_transaction(identifier: str) -> dict:
    token = await _get_token()
    async with httpx.AsyncClient(base_url=settings.SYNC_BASE_URL, timeout=20) as client:
        r = await client.get(
            f"/api/partner/v1/transaction/{identifier}",
            headers={"Authorization": f"Bearer {token}"}
        )
        r.raise_for_status()
        return r.json()
  
