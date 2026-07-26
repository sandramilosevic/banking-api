from loguru import logger
import logging


class InterceptHandler(logging.Handler):
    """
    A logging.Handler that intercepts standard `logging` records
    and redirects them to loguru, so that both stdlib logging
    and loguru output go through the same sink/formatting.
    """

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2

        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        # Forward the log record to loguru with the correct depth
        # (so the log shows the real call site) and pass along any
        # exception info so tracebacks are preserved.

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )
