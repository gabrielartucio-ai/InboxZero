import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


class LoggingService:
    """
    Configura el sistema de logging de la aplicación.
    Los componentes de Inbox Zero no deben configurar logging por separado.
    Cada componente solamente debe obtener su logger mediante:
        logger = logging.getLogger(__name__)
    """

    _configured = False

    @classmethod
    def configure(
        cls,
        level: int = logging.INFO,
        log_directory: str = "logs",
        log_filename: str = "inbox_zero.log"
    ) -> None:
        """
        Configura la salida de logs hacia:
        1. La consola.
        2. Un archivo rotativo.
        La configuración se ejecuta una sola vez aunque el método sea
        invocado más de una vez.
        """

        if cls._configured:
            return

        log_path = Path(log_directory)
        log_path.mkdir(parents=True, exist_ok=True)

        log_file = log_path / log_filename

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)

        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)

        root_logger = logging.getLogger()
        root_logger.setLevel(level)

        root_logger.handlers.clear()
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)

        logging.getLogger("exchangelib").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

        cls._configured = True

        logger = logging.getLogger(__name__)
        logger.info(
            "Sistema de logging configurado. Archivo=%s",
            log_file.resolve()
        )