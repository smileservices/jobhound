import logging

def create_logger(name, filename, level=logging.WARNING):
    logger = logging.getLogger(name)
    f_hand = logging.FileHandler(filename)
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_hand.setFormatter(f_format)
    logger.addHandler(f_hand)
    logger.setLevel(level)
