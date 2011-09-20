#!/usr/bin/python
#
# Tim Hawes <me@timhawes.com>
# 20th September 2011

import logging
import logging.handlers
import os
import sys

def logging_wizard(stderr_level=logging.INFO,
                   syslog_level=logging.INFO,
                   facility=logging.handlers.SysLogHandler.LOG_USER,
                   ident=os.path.basename(sys.argv[0])):
    logger = logging.getLogger()
    logger.setLevel(min(stderr_level, syslog_level))

    stream_format_string = ident + ": %(message)s"
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(fmt=stream_format_string))
    stream_handler.setLevel(stderr_level)
    logger.addHandler(stream_handler)

    syslog_format_string = ident + "[%(process)s]: %(message)s"
    syslog_handler = logging.handlers.SysLogHandler(address="/dev/log", facility=facility)
    syslog_handler.log_format_string = "<%d>%s"
    syslog_handler.setFormatter(logging.Formatter(fmt=syslog_format_string))
    syslog_handler.setLevel(syslog_level)
    logger.addHandler(syslog_handler)

if __name__ == "__main__":
    logging_wizard()
    logging.debug("debug message")
    logging.info("info message")
    logging.warn("warn message")
    logging.error("error message")
    logging.critical("critical message")
