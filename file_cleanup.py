import os
import time
from datetime import datetime
import threading
import logging
import atexit

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileCleanupManager:
    def __init__(self, cleanup_interval=10):  # 10 seconds check interval
        self.cleanup_interval = cleanup_interval
        self.file_timestamps = {}
        self.lock = threading.Lock()
        self.cleanup_thread = None
        self.running = False
        
    def start(self):
        """Start the cleanup manager"""
        if self.running:
            return
            
        try:
            self.running = True
            self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
            self.cleanup_thread.start()
            logger.info("File cleanup manager started")
        except Exception as e:
            logger.error(f"Error starting cleanup manager: {e}")
            self.running = False
    
    def stop(self):
        """Stop the cleanup manager"""
        if not self.running:
            return
            
        try:
            self.running = False
            if self.cleanup_thread and self.cleanup_thread.is_alive():
                self.cleanup_thread.join(timeout=5)  # Wait up to 5 seconds
                logger.info("File cleanup manager stopped")
        except Exception as e:
            logger.error(f"Error stopping cleanup manager: {e}")
    
    def track_file(self, filepath, expiry_seconds=10):  # 10 seconds default
        """Add a file to be tracked for cleanup"""
        try:
            with self.lock:
                self.file_timestamps[filepath] = {
                    'created_at': time.time(),
                    'expiry_seconds': expiry_seconds
                }
                logger.info(f"Tracking new file: {filepath} (will expire in {expiry_seconds} seconds)")
        except Exception as e:
            logger.error(f"Error tracking file {filepath}: {e}")
    
    def _cleanup_loop(self):
        """Main cleanup loop"""
        while self.running:
            try:
                self._perform_cleanup()
                time.sleep(self.cleanup_interval)
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                time.sleep(1)  # Prevent rapid error loops
    
    def _perform_cleanup(self):
        """Perform the actual cleanup of expired files"""
        current_time = time.time()
        files_to_remove = []
        
        try:
            # Identify expired files
            with self.lock:
                for filepath, info in self.file_timestamps.items():
                    if current_time - info['created_at'] >= info['expiry_seconds']:
                        files_to_remove.append(filepath)
                    else:
                        # Log remaining time for each file
                        remaining = info['expiry_seconds'] - (current_time - info['created_at'])
                        logger.info(f"File {filepath} will expire in {remaining:.1f} seconds")
            
            # Remove expired files
            for filepath in files_to_remove:
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        logger.info(f"Deleted expired file: {filepath}")
                    with self.lock:
                        self.file_timestamps.pop(filepath, None)
                except Exception as e:
                    logger.error(f"Error deleting file {filepath}: {e}")
        except Exception as e:
            logger.error(f"Error in cleanup process: {e}")
    
    def cleanup_all(self):
        """Immediately cleanup all tracked files"""
        try:
            with self.lock:
                for filepath in list(self.file_timestamps.keys()):
                    try:
                        if os.path.exists(filepath):
                            os.remove(filepath)
                            logger.info(f"Deleted file during cleanup_all: {filepath}")
                    except Exception as e:
                        logger.error(f"Error deleting file {filepath}: {e}")
                self.file_timestamps.clear()
        except Exception as e:
            logger.error(f"Error in cleanup_all: {e}")

# Create a global instance
cleanup_manager = FileCleanupManager() 