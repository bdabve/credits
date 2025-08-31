#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from rich.logging import RichHandler

# Configure the logger
FORMAT = "%(message)s"
logging.basicConfig(
    level="DEBUG",  # Change to INFO or ERROR as needed
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler()]
)

logger = logging.getLogger("rich")
# logging.getLogger("pymongo").setLevel(logging.WARNING)      # suppress Logging from pymongo
# logging.getLogger("matplotlib").setLevel(logging.WARNING)
