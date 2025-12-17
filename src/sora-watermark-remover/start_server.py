import argparse

import fire
import uvicorn
from loguru import logger

from sorawm.configs import LOGS_PATH
from sorawm.server.app import init_app

parser = argparse.ArgumentParser()
parser.add_argument("--host", default="0.0.0.0", help="host")
parser.add_argument("--port", default=5344, help="port")
parser.add_argument("--workers", default=1, type=int, help="workers")
args = parser.parse_args()
logger.add(LOGS_PATH / "log_file.log", rotation="1 week")


def start_server(port=args.port, host=args.host):
    logger.info(f"Starting server at {host}:{port}")
    app = init_app()
    config = uvicorn.Config(app, host=host, port=port, workers=args.workers)
    server = uvicorn.Server(config=config)
    try:
        server.run()
    finally:
        logger.info("Server shutdown.")


if __name__ == "__main__":
    fire.Fire(start_server)
