"""
Queue Manager for Batch Downloads
"""

import queue
from threading import Thread, Lock
from typing import List, Callable, Optional, Dict
from ..utils.logger import get_logger
from .downloader import Downloader

logger = get_logger(__name__)


class QueueManager:
    """Manage download queue"""
    
    def __init__(self):
        self._queue = queue.Queue()
        self._is_processing = False
        self._lock = Lock()
        self._current_item: Optional[str] = None
        self._downloader = Downloader()
    
    def add(self, url: str) -> None:
        """Add URL to queue"""
        self._queue.put(url)
        logger.info(f"Added to queue: {url}")
    
    def add_multiple(self, urls: List[str]) -> int:
        """
        Add multiple URLs to queue
        
        Returns:
            Number of URLs added
        """
        count = 0
        for url in urls:
            if url.strip():
                self.add(url.strip())
                count += 1
        return count
    
    def remove(self, url: str) -> bool:
        """Remove URL from queue (if not started)"""
        # This is tricky with queue.Queue, would need custom implementation
        # For now, we'll keep it simple
        logger.warning("Remove from queue not yet implemented")
        return False
    
    def clear(self) -> int:
        """
        Clear all items from queue
        
        Returns:
            Number of items cleared
        """
        with self._lock:
            count = self._queue.qsize()
            while not self._queue.empty():
                try:
                    self._queue.get_nowait()
                except queue.Empty:
                    break
            logger.info(f"Cleared {count} items from queue")
            return count
    
    def get_size(self) -> int:
        """Get queue size"""
        return self._queue.qsize()
    
    def is_processing(self) -> bool:
        """Check if queue is being processed"""
        return self._is_processing
    
    def start_processing(self, output_dir: str, settings: Dict,
                        progress_callback: Optional[Callable] = None,
                        log_callback: Optional[Callable] = None,
                        complete_callback: Optional[Callable] = None) -> None:
        """
        Start processing queue
        
        Args:
            output_dir: Output directory
            settings: Download settings
            progress_callback: Progress callback
            log_callback: Log callback
            complete_callback: Callback when queue is complete
        """
        if self._is_processing:
            logger.warning("Queue is already being processed")
            return
        
        thread = Thread(
            target=self._process_queue,
            args=(output_dir, settings, progress_callback, log_callback, complete_callback),
            daemon=True
        )
        thread.start()
    
    def _process_queue(self, output_dir: str, settings: Dict,
                      progress_callback: Optional[Callable],
                      log_callback: Optional[Callable],
                      complete_callback: Optional[Callable]) -> None:
        """Process queue in background thread"""
        with self._lock:
            if self._is_processing:
                return
            self._is_processing = True
        
        total = self._queue.qsize()
        processed = 0
        successful = 0
        failed = 0
        
        if log_callback:
            log_callback(f"Starting queue processing: {total} items")
        
        logger.info(f"Processing queue: {total} items")
        
        while not self._queue.empty():
            try:
                url = self._queue.get_nowait()
                self._current_item = url
                processed += 1
                
                if log_callback:
                    log_callback(f"[{processed}/{total}] Processing: {url}")
                
                # Download
                success = self._downloader.download(
                    url, output_dir, settings,
                    progress_callback, log_callback
                )
                
                if success:
                    successful += 1
                else:
                    failed += 1
                
                self._queue.task_done()
                
            except queue.Empty:
                break
            except Exception as e:
                logger.error(f"Error processing queue item: {e}")
                failed += 1
        
        self._current_item = None
        self._is_processing = False
        
        # Summary
        summary = f"Queue complete: {successful} successful, {failed} failed"
        if log_callback:
            log_callback(summary)
        logger.info(summary)
        
        # Callback
        if complete_callback:
            complete_callback(successful, failed)
    
    def stop_processing(self) -> None:
        """Stop queue processing"""
        self._downloader.stop()
        self.clear()
        self._is_processing = False
        logger.info("Queue processing stopped")
    
    def get_all_items(self) -> List[str]:
        """Get list of all queued items (without removing them)"""
        # This creates a copy of the queue
        with self._lock:
            items = list(self._queue.queue)
        return items


# Global instance
queue_manager = QueueManager()
