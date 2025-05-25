import uvicorn
from ddtrace import patch_all

patch_all()

if __name__ == "__main__":
    uvicorn.run(
        "core.server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        ws_ping_interval=300,
        ws_ping_timeout=300,
    )
