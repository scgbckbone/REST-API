import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

frmttr = logging.Formatter(
    '%(asctime)-30s, %(levelName)-15s, %(name)-15s, %(message)s'
)

file_handler = logging.FileHandler("/var/www/html/items-rest/resources/requests_log/reqlog.log")
file_handler.setLevel(logging.ERROR)

file_handler.setFormatter(frmttr)
logger.addHandler(file_handler)
