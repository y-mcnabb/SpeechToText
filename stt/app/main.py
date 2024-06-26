import argparse

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from loguru import logger

from app.api.main import api_router

app = FastAPI(debug=True)

app.include_router(api_router)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true")
    parser.add_argument("--local", action="store_true")
    parser.add_argument("--prod", action="store_true")
    args = parser.parse_args()
    env_loaded_succesfully = False

    # TODO: Fix this for PROD
    if args.dev:
        env_loaded_succesfully = load_dotenv(".dev.env")
    elif args.local:
        env_loaded_succesfully = load_dotenv(".local.env")
    elif args.prod:
        raise NotImplementedError("PROD is not implemented yet")
    else:
        raise EnvironmentError("Please specify a valid environment")

    if not env_loaded_succesfully:
        logger.warning("Unable to load environment variables!")

    uvicorn.run(
        "stt.app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="debug",
        workers=5,
        limit_concurrency=5,
        limit_max_requests=5,
    )
