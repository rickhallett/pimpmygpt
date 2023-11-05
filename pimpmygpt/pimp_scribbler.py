import logging


class PimpScribbler(object):
    _instance = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PimpScribbler, cls).__new__(cls)
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.DEBUG)  # Set level of logger

            debug_handler = logging.FileHandler('./pimpmygpt/logs/debug.log')
            debug_handler.setLevel(logging.DEBUG)

            error_handler = logging.FileHandler('./pimpmygpt/logs/error.log')
            error_handler.setLevel(logging.ERROR)

            info_handler = logging.FileHandler('./pimpmygpt/logs/info.log')
            info_handler.setLevel(logging.INFO)

            # Create formatters and add it to handlers
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            debug_handler.setFormatter(formatter)
            error_handler.setFormatter(formatter)
            info_handler.setFormatter(formatter)

            # Add handlers to the logger
            logger.addHandler(debug_handler)
            logger.addHandler(error_handler)
            logger.addHandler(info_handler)
            cls._logger = logger

        return cls._instance

    @property
    def log(self):
        return self._logger
