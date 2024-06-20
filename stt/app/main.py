import argparse

import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv

from app.api.main import api_router

app = FastAPI(debug=True)

app.include_router(api_router)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true")
    parser.add_argument("--local", action="store_true")
    parser.add_argument("--prod", action="store_true")
    args = parser.parse_args()

    # TODO: Fix this for PROD
    if args.dev:
        load_dotenv("stt/.dev.env")
    elif args.local:
        load_dotenv("stt/.local.env")
    elif args.prod:
        raise NotImplementedError("PROD is not implemented yet")
    else:
        raise EnvironmentError("Please specify a valid environment")
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="debug",
        workers=5,
        limit_concurrency=5,
        limit_max_requests=5,
    )
