from fastapi import FastAPI, Request

app = FastAPI(title="example-webhook")


@app.post("/webhook")
async def consume_webhook(request: Request) -> dict:
    payload = await request.json()
    print(payload)
    return {"received": True, "payload": payload}
