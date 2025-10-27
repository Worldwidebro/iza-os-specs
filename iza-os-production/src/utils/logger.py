"""
IZA OS Logging System
Simplified logging configuration for development
"""

import logging
import logging.handlers
import sys
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from functools import wraps
from datetime import datetime
from rich.logging import RichHandler
from rich.console import Console
import structlog
from loguru import logger as loguru_logger

console = Console()


class IZAFormatter(logging.Formatter):
    """
    Custom formatter for IZA OS with emoji indicators and mobile-friendly output
    """
    
    # Emoji indicators for different log levels
    LEVEL_EMOJI = {
        'DEBUG': '🔍',
        'INFO': '📘',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🚨'
    }
    
    def __init__(self, format_type: str = "detailed"):
        self.format_type = format_type
        
        if format_type == "mobile":
            # Compact format for mobile development
            fmt = "{emoji} {levelname:<8} | {name:<20} | {message}"
        elif format_type == "json":
            # JSON format for structured logging
            fmt = None  # Will use custom JSON formatting
        else:
            # Detailed format for development
            fmt = "{emoji} {asctime} | {levelname:<8} | {name:<30} | {funcName}:{lineno:<4} | {message}"
        
        super().__init__(fmt, style='{')
    
    def format(self, record):
        # Add emoji to record
        record.emoji = self.LEVEL_EMOJI.get(record.levelname, '📝')
        
        if self.format_type == "json":
            # Custom JSON formatting
            log_data = {
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'function': record.funcName,
                'line': record.lineno,
                'message': record.getMessage(),
                'module': record.module,
                'thread': record.thread,
                'process': record.process
            }
            
            # Add exception info if present
            if record.exc_info:
                log_data['exception'] = self.formatException(record.exc_info)
            
            # Add extra fields if present
            if hasattr(record, 'extra'):
                log_data['extra'] = record.extra
            
            return json.dumps(log_data, ensure_ascii=False)
        else:
            return super().format(record)


class IZALoggerAdapter(logging.LoggerAdapter):
    """
    Custom logger adapter that adds IZA OS context to log messages
    """
    
    def __init__(self, logger, extra=None):
        super().__init__(logger, extra or {})
    
    def process(self, msg, kwargs):
        # Add IZA OS context
        extra = kwargs.get('extra', {})
        extra.update(self.extra)
        
        # Add system context
        extra['iza_os_version'] = '1.0.0'
        extra['component'] = self.extra.get('component', 'core')
        
        kwargs['extra'] = extra
        return msg, kwargs


def setup_logger(
    name: str,
    level: str = "INFO",
    format_type: str = "detailed",
    file_logging: bool = True,
    rich_logging: bool = True,
    component: str = "core"
) -> logging.Logger:
    """
    Set up a comprehensive logger for IZA OS components
    
    Args:
        name: Logger name (usually __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Format type (detailed, mobile, json)
        file_logging: Enable file logging
        rich_logging: Enable rich terminal output
        component: IZA OS component name
    
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Console handler with rich formatting
    if rich_logging and not os.getenv('NO_RICH_LOGGING'):
        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=True,
            markup=True,
            rich_tracebacks=True,
            tracebacks_show_locals=True
        )
        console_handler.setLevel(getattr(logging, level.upper()))
        logger.addHandler(console_handler)
    else:
        # Standard console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(IZAFormatter(format_type))
        console_handler.setLevel(getattr(logging, level.upper()))
        logger.addHandler(console_handler)
    
    # File handler for persistent logging
    if file_logging:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Main log file with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "iza-os.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(IZAFormatter("json"))
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        
        # Component-specific log file
        if component != "core":
            component_handler = logging.handlers.RotatingFileHandler(
                log_dir / f"iza-os-{component}.log",
                maxBytes=5 * 1024 * 1024,  # 5MB
                backupCount=3,
                encoding='utf-8'
            )
            component_handler.setFormatter(IZAFormatter("json"))
            component_handler.setLevel(logging.DEBUG)
            logger.addHandler(component_handler)
    
    # Error file handler for errors and above
    if file_logging:
        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / "iza-os-errors.log",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=10,
            encoding='utf-8'
        )
        error_handler.setFormatter(IZAFormatter("json"))
        error_handler.setLevel(logging.ERROR)
        logger.addHandler(error_handler)
    
    # Wrap with adapter to add context
    adapter = IZALoggerAdapter(logger, {'component': component})
    
    return adapter


def setup_structlog():
    """
    Configure structlog for structured logging across IZA OS
    """
    
    timestamper = structlog.processors.TimeStamper(fmt="ISO")
    
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ]
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True
    )


def log_execution_time(logger: logging.Logger):
    """
    Decorator to log function execution time - useful for performance monitoring
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = datetime.now()
            try:
                result = await func(*args, **kwargs)
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.info(
                    f"⚡ {func.__name__} completed",
                    extra={
                        'execution_time': execution_time,
                        'function': func.__name__,
                        'module': func.__module__
                    }
                )
                return result
            except Exception as e:
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.error(
                    f"❌ {func.__name__} failed after {execution_time:.2f}s",
                    extra={
                        'execution_time': execution_time,
                        'function': func.__name__,
                        'module': func.__module__,
                        'error': str(e)
                    },
                    exc_info=True
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = datetime.now()
            try:
                result = func(*args, **kwargs)
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.info(
                    f"⚡ {func.__name__} completed",
                    extra={
                        'execution_time': execution_time,
                        'function': func.__name__,
                        'module': func.__module__
                    }
                )
                return result
            except Exception as e:
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.error(
                    f"❌ {func.__name__} failed after {execution_time:.2f}s",
                    extra={
                        'execution_time': execution_time,
                        'function': func.__name__,
                        'module': func.__module__,
                        'error': str(e)
                    },
                    exc_info=True
                )
                raise
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def log_api_call(logger: logging.Logger):
    """
    Decorator to log API calls with request/response details
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request_id = kwargs.get('request_id', 'unknown')
            
            logger.info(
                f"🌐 API call started: {func.__name__}",
                extra={
                    'request_id': request_id,
                    'function': func.__name__,
                    'args_count': len(args),
                    'kwargs_keys': list(kwargs.keys())
                }
            )
            
            try:
                result = await func(*args, **kwargs)
                logger.info(
                    f"✅ API call completed: {func.__name__}",
                    extra={
                        'request_id': request_id,
                        'function': func.__name__,
                        'success': True
                    }
                )
                return result
            except Exception as e:
                logger.error(
                    f"❌ API call failed: {func.__name__}",
                    extra={
                        'request_id': request_id,
                        'function': func.__name__,
                        'error': str(e),
                        'success': False
                    },
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


def log_venture_operation(logger: logging.Logger):
    """
    Decorator specifically for venture operations
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            venture_id = kwargs.get('venture_id', args[0] if args else 'unknown')
            
            logger.info(
                f"🏭 Venture operation: {func.__name__}",
                extra={
                    'venture_id': venture_id,
                    'operation': func.__name__,
                    'component': 'venture_factory'
                }
            )
            
            try:
                result = await func(*args, **kwargs)
                logger.info(
                    f"✅ Venture operation completed: {func.__name__}",
                    extra={
                        'venture_id': venture_id,
                        'operation': func.__name__,
                        'success': True
                    }
                )
                return result
            except Exception as e:
                logger.error(
                    f"❌ Venture operation failed: {func.__name__}",
                    extra={
                        'venture_id': venture_id,
                        'operation': func.__name__,
                        'error': str(e),
                        'success': False
                    },
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


class PerformanceMonitor:
    """
    Performance monitoring utility for IZA OS components
    """
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.metrics = {}
    
    def start_timer(self, operation: str):
        """Start timing an operation"""
        self.metrics[operation] = {
            'start_time': datetime.now(),
            'status': 'running'
        }
    
    def end_timer(self, operation: str, success: bool = True, metadata: Dict[str, Any] = None):
        """End timing an operation"""
        if operation not in self.metrics:
            self.logger.warning(f"⚠️  Timer not found for operation: {operation}")
            return
        
        start_time = self.metrics[operation]['start_time']
        duration = (datetime.now() - start_time).total_seconds()
        
        self.metrics[operation].update({
            'end_time': datetime.now(),
            'duration': duration,
            'status': 'completed' if success else 'failed',
            'metadata': metadata or {}
        })
        
        # Log performance metric
        emoji = "⚡" if success else "⏱️"
        status = "completed" if success else "failed"
        
        self.logger.info(
            f"{emoji} Operation {operation} {status} in {duration:.3f}s",
            extra={
                'operation': operation,
                'duration': duration,
                'success': success,
                'metadata': metadata or {}
            }
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics"""
        return self.metrics.copy()


# Configure loguru for additional features
def setup_loguru():
    """
    Configure loguru logger for enhanced logging features
    """
    
    # Remove default handler
    loguru_logger.remove()
    
    # Add custom handler with rotation and retention
    loguru_logger.add(
        "logs/iza-os-loguru.log",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} | {message}",
        level="INFO"
    )
    
    # Add colored console output
    loguru_logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
        level="DEBUG"
    )


# Global performance monitor instance
_global_perf_monitor = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _global_perf_monitor
    if _global_perf_monitor is None:
        logger = setup_logger(__name__, component="performance")
        _global_perf_monitor = PerformanceMonitor(logger)
    return _global_perf_monitor


# Initialize logging system
if __name__ == "__main__":
    # Test the logging system
    test_logger = setup_logger(__name__, level="DEBUG", component="test")
    
    test_logger.info("🧠 IZA OS logging system initialized")
    test_logger.debug("🔍 Debug message test")
    test_logger.warning("⚠️  Warning message test")
    test_logger.error("❌ Error message test")
    
    # Test performance monitoring
    perf = get_performance_monitor()
    perf.start_timer("test_operation")
    import time
    time.sleep(0.1)
    perf.end_timer("test_operation", success=True, metadata={"test": "data"})
    
    print("✅ Logging system test completed")
else:
    # Auto-configure on import
    setup_structlog()
    setup_loguru()


import asyncio  # Import asyncio for decorator function type checking
