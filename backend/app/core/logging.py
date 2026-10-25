import logging
import sys


def setup_logging(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("hireloop")
    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger


def log_safe(logger: logging.Logger, message: str, **kwargs) -> None:
    """
    Log only IDs, sizes, and timings. Never log resume text or profile content.
    """
    safe_kwargs = {k: v for k, v in kwargs.items() if k not in ("text", "content", "resume", "profile_text")}
    logger.info(message, extra=safe_kwargs)
