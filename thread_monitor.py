#!/usr/bin/env python
"""
Thread Monitor for BrowserStack Tests

This script monitors thread activity during BrowserStack test execution,
helping to diagnose and fix the "RuntimeError: can't create new thread at interpreter shutdown" error.

Usage:
    python thread_monitor.py

Author: Cascade AI Assistant
Date: 2025-03-23
"""

import os
import sys
import time
import json
import logging
import threading
import atexit
import signal
import gc
import traceback
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Set up logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = log_dir / f"thread_monitor_{timestamp}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)s:%(thread)d] [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger()

# Load environment variables
load_dotenv()

# Global variables for thread tracking
_ACTIVE_THREADS = set()
_THREAD_HISTORY = []
_CLEANUP_REGISTERED = False

def track_threads():
    """Track and record all active threads"""
    global _ACTIVE_THREADS, _THREAD_HISTORY
    
    current_threads = set(threading.enumerate())
    new_threads = current_threads - _ACTIVE_THREADS
    ended_threads = _ACTIVE_THREADS - current_threads
    
    if new_threads:
        logger.info(f"New threads detected: {len(new_threads)}")
        for thread in new_threads:
            logger.info(f"New thread: {thread.name} (ID: {thread.ident}, Daemon: {thread.daemon})")
    
    if ended_threads:
        logger.info(f"Threads ended: {len(ended_threads)}")
        for thread in ended_threads:
            logger.info(f"Thread ended: {thread.name} (ID: {thread.ident}, Daemon: {thread.daemon})")
    
    # Record thread state history
    thread_state = {
        "timestamp": datetime.now().isoformat(),
        "total_threads": len(current_threads),
        "threads": [
            {
                "name": t.name,
                "id": t.ident,
                "daemon": t.daemon,
                "alive": t.is_alive()
            }
            for t in current_threads
        ]
    }
    _THREAD_HISTORY.append(thread_state)
    
    _ACTIVE_THREADS = current_threads
    return current_threads

def dump_thread_info(prefix="threads"):
    """Dump thread information to a JSON file for analysis"""
    thread_info = []
    for thread in threading.enumerate():
        thread_info.append({
            "name": thread.name,
            "id": thread.ident,
            "daemon": thread.daemon,
            "alive": thread.is_alive()
        })
    
    # Save to JSON file
    thread_file = log_dir / f"{prefix}_{timestamp}.json"
    with open(thread_file, "w") as f:
        json.dump(thread_info, f, indent=2)
    
    logger.info(f"Thread information saved to {thread_file}")
    return thread_info

def save_thread_history():
    """Save the thread history to a JSON file"""
    history_file = log_dir / f"thread_history_{timestamp}.json"
    with open(history_file, "w") as f:
        json.dump(_THREAD_HISTORY, f, indent=2)
    
    logger.info(f"Thread history saved to {history_file}")

def cleanup_threads():
    """Clean up threads before interpreter shutdown"""
    logger.info("Cleaning up threads before interpreter shutdown")
    
    # Try to clean up non-daemon threads
    for thread in threading.enumerate():
        if thread != threading.current_thread() and not thread.daemon and thread.is_alive():
            logger.info(f"Attempting to join thread: {thread.name}")
            try:
                thread.join(timeout=1.0)
            except Exception as e:
                logger.error(f"Error joining thread {thread.name}: {str(e)}")
    
    # Save thread history
    save_thread_history()
    
    # Force garbage collection
    logger.info("Running garbage collection")
    gc.collect()

def signal_handler(signum, frame):
    """Handle signals to ensure proper cleanup"""
    logger.info(f"Signal {signum} received, initiating cleanup")
    cleanup_threads()
    sys.exit(1)

def register_cleanup():
    """Register cleanup handlers"""
    global _CLEANUP_REGISTERED
    if not _CLEANUP_REGISTERED:
        # Register cleanup function to run at interpreter shutdown
        atexit.register(cleanup_threads)
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        _CLEANUP_REGISTERED = True
        logger.info("Cleanup handlers registered")

def monitor_threads(interval=1.0, duration=60.0):
    """Monitor threads for a specified duration"""
    logger.info(f"Starting thread monitoring for {duration} seconds")
    
    # Register cleanup handlers
    register_cleanup()
    
    # Track initial threads
    logger.info("Initial thread state:")
    initial_threads = track_threads()
    dump_thread_info("initial_threads")
    
    # Monitor threads at regular intervals
    start_time = time.time()
    while time.time() - start_time < duration:
        time.sleep(interval)
        current_threads = track_threads()
        
        # Log thread count
        logger.info(f"Current thread count: {len(current_threads)}")
        
        # Dump thread info every 10 seconds
        if int((time.time() - start_time) / 10) == (time.time() - start_time) / 10:
            dump_thread_info(f"threads_{int(time.time() - start_time)}")
    
    # Final thread state
    logger.info("Final thread state:")
    final_threads = track_threads()
    dump_thread_info("final_threads")
    
    # Save thread history
    save_thread_history()
    
    # Log summary
    logger.info(f"Thread monitoring completed")
    logger.info(f"Initial thread count: {len(initial_threads)}")
    logger.info(f"Final thread count: {len(final_threads)}")
    
    # List non-daemon threads
    non_daemon_threads = [t for t in final_threads if not t.daemon]
    logger.info(f"Non-daemon threads: {len(non_daemon_threads)}")
    for thread in non_daemon_threads:
        logger.info(f"Non-daemon thread: {thread.name} (ID: {thread.ident})")

def analyze_thread_leaks():
    """Analyze thread leaks from thread history"""
    if not _THREAD_HISTORY:
        logger.error("No thread history available for analysis")
        return
    
    logger.info("Analyzing thread leaks")
    
    # Get initial and final thread states
    initial_state = _THREAD_HISTORY[0]
    final_state = _THREAD_HISTORY[-1]
    
    # Find threads that were created during monitoring and still alive at the end
    initial_thread_ids = {t["id"] for t in initial_state["threads"]}
    final_threads = final_state["threads"]
    
    leaked_threads = [
        t for t in final_threads 
        if t["id"] not in initial_thread_ids and t["alive"] and not t["daemon"]
    ]
    
    if leaked_threads:
        logger.info(f"Found {len(leaked_threads)} potential thread leaks:")
        for thread in leaked_threads:
            logger.info(f"Leaked thread: {thread['name']} (ID: {thread['id']}, Daemon: {thread['daemon']})")
    else:
        logger.info("No thread leaks detected")
    
    # Analyze thread count over time
    thread_counts = [(state["timestamp"], state["total_threads"]) for state in _THREAD_HISTORY]
    logger.info("Thread count over time:")
    for timestamp, count in thread_counts:
        logger.info(f"{timestamp}: {count} threads")

def main():
    """Main function to run the thread monitor"""
    logger.info("Starting thread monitor")
    
    # Monitor threads for 60 seconds
    monitor_threads(interval=1.0, duration=60.0)
    
    # Analyze thread leaks
    analyze_thread_leaks()
    
    # Final cleanup
    logger.info("Thread monitoring completed")

if __name__ == "__main__":
    main()
