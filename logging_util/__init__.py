"""
All logger shoud be instantiated and specified here.
"""

import config
from logging_util.logger_factory import get_me_logger

email_logger = get_me_logger(
    name="email",
    path=config.log_path_email,
    stream=config.stream_handler
)

resource_logger = get_me_logger(
    name="resource",
    path=config.log_path_resource,
    stream=config.stream_handler
)

err_log = get_me_logger(
    name="error",
    path=config,
    stream=config.stream_handler
)
