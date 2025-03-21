import os.path
from datetime import datetime
import logging
import logging.config
from colorlog import ColoredFormatter
import config


def setup_logger():
    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(log_color)s%(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
    logger = logging.getLogger("example")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    return logger


g_logger = setup_logger()


def debug(outstr):
    g_logger.debug(outstr)


def info(outstr):
    g_logger.info(outstr)


def warning(outstr):
    g_logger.warning(outstr)


def error(outstr):
    g_logger.error(outstr)


def critical(outstr):
    g_logger.critical(outstr)


def Logger(strLogDir):
    log_dir = config.LOGS
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")

    log_subdir = os.path.join(log_dir, year, month)
    if not os.path.exists(log_subdir):
        os.makedirs(log_subdir)

    strFilePathAndName = os.path.join(log_subdir, "log_")
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(message)s", datefmt="%Y/%m/%d %H:%M:%S"
    )
    logging.basicConfig(
        filename="%s%s.log" % (strFilePathAndName, datetime.now().strftime("%y_%m_%d")),
        format="%(asctime)s | %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
        filemode="a",
        level=logging.INFO,
    )

    log_obj = logging.getLogger()
    log_obj.setLevel(logging.DEBUG)

    return log_obj


def setFileLogMode(strLogDir):
    g_logger = Logger(strLogDir)


def setLevel(nVal):
    g_logger.setLevel(nVal)
