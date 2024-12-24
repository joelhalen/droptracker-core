from models.log import Log
from models.base import session
import traceback
import time
from typing import Optional

class Logger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance
    
    def log(self, level: str, source: str, message: str, details: Optional[str] = None) -> None:
        """
        Log a message to the database
        
        Args:
            level: Log level (INFO, WARNING, ERROR, DEBUG)
            source: Source of the log (which part of the application)
            message: Main log message
            details: Optional additional details or stack trace
        """
        try:
            log_entry = Log(
                level=level.upper(),
                source=source,
                message=message,
                details=details,
                timestamp=int(time.time())
            )
            session.add(log_entry)
            print(f"[{level}] {source}: {message}")
            session.commit()
        except Exception as e:
            print(f"Failed to write log to database: {e}")
            session.rollback()
    
    def info(self, source: str, message: str) -> None:
        self.log("INFO", source, message)
    
    def warning(self, source: str, message: str, details: Optional[str] = None) -> None:
        self.log("WARNING", source, message, details)
    
    def error(self, source: str, message: str, error: Optional[Exception] = None) -> None:
        details = traceback.format_exc() if error else None
        self.log("ERROR", source, message, details)
    
    def debug(self, source: str, message: str) -> None:
        self.log("DEBUG", source, message)
