"""Centralized logging configuration for the application."""

from __future__ import annotations

import logging
import logging.config


def configure_logging(log_level: str, log_format: str) -> None:
    """Configure application and server loggers with a shared formatter."""
    resolved_level = log_level.upper()

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": log_format,
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "level": resolved_level,
                }
            },
            "root": {
                "handlers": ["default"],
                "level": resolved_level,
            },
            "loggers": {
                "uvicorn": {
                    "handlers": ["default"],
                    "level": resolved_level,
                    "propagate": False,
                },
                "uvicorn.error": {
                    "handlers": ["default"],
                    "level": resolved_level,
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["default"],
                    "level": resolved_level,
                    "propagate": False,
                },
                "schedule_builder": {
                    "handlers": ["default"],
                    "level": resolved_level,
                    "propagate": False,
                },
            },
        }
    )


def get_logger(name: str) -> logging.Logger:
    """Return a named logger for module-level use."""
    return logging.getLogger(name)
