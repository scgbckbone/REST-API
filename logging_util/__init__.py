"""
All logger shoud be instantiated and specified here.
"""

import config
from logging_util.logger_factory import get_me_logger

email_logger = get_me_logger(
    name="email",
    path=config.log_path_email,
    stream=config.debug_local
)

resource_logger = get_me_logger(
    name="resource",
    path=config.log_path_resource,
    stream=config.debug_local
)

err_log = get_me_logger(
    name="error",
    path=config,
    stream=config.debug_local
)
