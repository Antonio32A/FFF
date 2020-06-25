import logging
import coloredlogs


class Logger:
    """
    Custom logging class
    """
    def __init__(self, level):
        self.logger = logging.getLogger(__name__)
        self.logging_format = "[%(asctime)s] [%(levelname)s]: %(message)s"
        logging.basicConfig(
            level=level,
            format=self.logging_format,
            datefmt='%H:%M:%S'
        )
        coloredlogs.install(level=level)

        self.file_handler = logging.FileHandler("bot.log")
        self.file_handler.setLevel(level)
        self.file_handler.setFormatter(logging.Formatter(self.logging_format))
        self.logger.addHandler(self.file_handler)

        self.disabled_loggers = [
            "discord.client",
            "discord.gateway",
            "discord.state",
            "discord.http",
            "websockets.protocol",
            "websockets.client",
            "google.auth.transport.requests",
            "urllib3.connectionpool",
            "urllib3.util.retry",
            "asyncio",
            "matplotlib.font_manager"
        ]
        for disabled_logger in self.disabled_loggers:
            disabled_logger = logging.getLogger(disabled_logger)
            disabled_logger.disabled = True
