import logging

def setup_logger(name, level=logging.INFO, save_to_file=False):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    ch = logging.StreamHandler()
    ch.setLevel(level)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    
    logger.addHandler(ch)

    if save_to_file:
        fh = logging.FileHandler(f"{name}.log")
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    
    return logger

api_logger = setup_logger("chzzk.api", logging.DEBUG)
ws_logger = setup_logger("chzzk.websocket", logging.DEBUG)
server_logger = setup_logger("chzzk.server", logging.INFO)
client_logger = setup_logger("chzzk.client", logging.DEBUG)
chat_logger = setup_logger("chzzk.chat", logging.INFO)
command_logger = setup_logger("chzzk.command", logging.INFO, save_to_file=True)
