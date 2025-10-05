"""
Graceful Shutdown Handler

T121: Handle crashes and interrupts gracefully.

Features:
- Signal handler for SIGINT, SIGTERM
- Save agent state on shutdown
- Cleanup resources (close windows, connections, files)
- Log shutdown reason
"""

import signal
import sys
import atexit
from typing import Optional, Callable, List
from pathlib import Path

from src.lib.logging_config import get_logger

logger = get_logger(__name__)


class ShutdownHandler:
    """
    Manages graceful shutdown of the agent.
    
    Registers signal handlers and cleanup callbacks to ensure proper
    resource cleanup on exit or interruption.
    """
    
    def __init__(self):
        """Initialize shutdown handler."""
        self.shutdown_callbacks: List[Callable[[], None]] = []
        self.is_shutting_down = False
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Register atexit handler
        atexit.register(self._cleanup)
        
        logger.info("shutdown_handler_initialized")
    
    def register_callback(self, callback: Callable[[], None]) -> None:
        """
        Register a cleanup callback.
        
        Args:
            callback: Function to call on shutdown
        """
        self.shutdown_callbacks.append(callback)
        logger.debug(
            "shutdown_callback_registered",
            callback_count=len(self.shutdown_callbacks)
        )
    
    def _signal_handler(self, signum: int, frame) -> None:
        """
        Handle shutdown signals.
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        signal_name = signal.Signals(signum).name
        logger.info(
            "shutdown_signal_received",
            signal=signal_name,
            signal_num=signum
        )
        
        self._shutdown(f"signal_{signal_name}")
    
    def _cleanup(self) -> None:
        """Cleanup handler called on normal exit."""
        if not self.is_shutting_down:
            self._shutdown("normal_exit")
    
    def _shutdown(self, reason: str) -> None:
        """
        Execute shutdown sequence.
        
        Args:
            reason: Reason for shutdown
        """
        if self.is_shutting_down:
            logger.warning("shutdown_already_in_progress")
            return
        
        self.is_shutting_down = True
        
        logger.info("shutdown_started", reason=reason)
        
        # Execute all registered callbacks
        for i, callback in enumerate(self.shutdown_callbacks):
            try:
                logger.debug(
                    "executing_shutdown_callback",
                    callback_index=i,
                    total_callbacks=len(self.shutdown_callbacks)
                )
                callback()
            except Exception as e:
                logger.error(
                    "shutdown_callback_failed",
                    callback_index=i,
                    error=str(e)
                )
        
        logger.info("shutdown_complete", reason=reason)
        
        # Exit if triggered by signal
        if reason.startswith("signal_"):
            sys.exit(0)
    
    def trigger_shutdown(self, reason: str = "manual") -> None:
        """
        Manually trigger shutdown.
        
        Args:
            reason: Reason for shutdown
        """
        self._shutdown(reason)


# Global shutdown handler instance
_shutdown_handler: Optional[ShutdownHandler] = None


def get_shutdown_handler() -> ShutdownHandler:
    """
    Get or create the global shutdown handler.
    
    Returns:
        ShutdownHandler instance
    """
    global _shutdown_handler
    
    if _shutdown_handler is None:
        _shutdown_handler = ShutdownHandler()
    
    return _shutdown_handler


def register_shutdown_callback(callback: Callable[[], None]) -> None:
    """
    Register a cleanup callback for shutdown.
    
    Args:
        callback: Function to call on shutdown
    """
    handler = get_shutdown_handler()
    handler.register_callback(callback)


def trigger_shutdown(reason: str = "manual") -> None:
    """
    Trigger graceful shutdown.
    
    Args:
        reason: Reason for shutdown
    """
    handler = get_shutdown_handler()
    handler.trigger_shutdown(reason)
