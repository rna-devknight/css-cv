import logging

# logging.basicConfig(level = logging.DEBUG)

logging.info("Info")
logging.debug("Debug")
logging.warning("Warning")
logging.error("Error")

def bungo():
    logging.critical("Critical error")

bungo()