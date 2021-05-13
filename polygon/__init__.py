# This file is distributed as a part of the polygon project (justaprudev.github.io/polygon)
# By justaprudev

import logging
from utility import env
from .polygon import Polygon
from telethon.sessions import StringSession

# Configure rootLogger
logging.basicConfig(level=logging.INFO)
log_formatter = logging.Formatter(
    fmt="[%(levelname)s %(asctime)s] Module '%(module)s', function '%(funcName)s' at line %(lineno)d -> %(message)s",
    datefmt="%d/%m/%Y %T %p",
)
logger = logging.getLogger()
file_handler = logging.FileHandler("polygon.log")
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

# Get credentials from env and start polygon
session = env.SESSION
if session:
    logger.info("Polygon is now online!")
    polygon = Polygon(
        session=StringSession(session),
        api_id=env.APP_ID,
        api_hash=env.API_HASH,
    )
    polygon.run_until_disconnected()
else:
    logger.info("Please set your session string to SESSION enviroment variable.")