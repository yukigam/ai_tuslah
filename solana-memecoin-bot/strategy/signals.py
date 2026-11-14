from fastapi import FastAPI, Request, HTTPException
from config.settings import settings

app = FastAPI()


@app.post("/webhook/axiom")
async def axiom_webhook(request: Request):
    secret = request.headers.get("x-webhook-secret", "")
    if settings.axiom_webhook_secret and secret != settings.axiom_webhook_secret:
        raise HTTPException(status_code=401, detail="bad secret")
    payload = await request.json()
    # payload expected: {action: buy|sell, token: mint, amount_sol: float}
    return {"status": "received", "payload": payload}
