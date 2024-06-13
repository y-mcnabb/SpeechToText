import argparse
import os

import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv

from app.api.main import api_router

app = FastAPI(debug=True)

app.include_router(api_router)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true")
    args = parser.parse_args()

    # TODO: Fix this for PROD
    if args.dev:
        load_dotenv(".dev.env")
        os.environ["AZURE_STORAGE_CONNECTION_STRING"] = (
           "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
        )

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
