"""
BrowserStack Logger for downloading and saving test artifacts.
This module is focused on artifact collection and storage, not general reporting.
"""
import os
import json
import requests
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path
from features.utils.browserstack_utils import BrowserStackUtils
from features.utils.reporting_utils import ReportingUtils

class BrowserStackLogger:
    """
    Handles downloading and storing BrowserStack test artifacts.
    Focused on collecting logs, videos, and other artifacts for later analysis.
    """
    
    def __init__(self, context=None):
        """
        Initialize BrowserStackLogger.
        
        Args:
            context: Optional behave context object
        """
        self.username = os.getenv('BROWSERSTACK_USERNAME')
        self.access_key = os.getenv('BROWSERSTACK_ACCESS_KEY')
        self.base_url = 'https://api.browserstack.com/automate/sessions'
        self.log_dir = Path(os.getcwd()) / 'logs' / 'browserstack'
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Get existing logger or create a new one
        self.logger = logging.getLogger('BrowserStackLogger')
        self.context = context
        
        # Initialize BrowserStackUtils if context is provided
        self.bs_utils = None
        if context:
            self.bs_utils = BrowserStackUtils(context)

    def download_session_artifacts(self, session_id: str, scenario_name: str) -> bool:
        """
        Download all artifacts for a BrowserStack session.
        
        Args:
            session_id: BrowserStack session ID
            scenario_name: Name of the scenario
            
        Returns:
            True if artifacts were downloaded successfully, False otherwise
        """
        if not self.username or not self.access_key:
            self.logger.error("BrowserStack credentials not found")
            return False
            
        # Create directory for this session
        scenario_dir = self.log_dir / scenario_name.replace(' ', '_')
        scenario_dir.mkdir(parents=True, exist_ok=True)
        
        # Get session details
        session_logs = None
        if self.bs_utils:
            session_logs = self.bs_utils.get_session_logs()
        else:
            # Create temporary BrowserStackUtils
            from features.utils.browserstack_utils import BrowserStackUtils
            temp_utils = BrowserStackUtils(self.context)
            temp_utils.session_id = session_id
            session_logs = temp_utils.get_session_logs()
            
        if not session_logs:
            self.logger.error(f"Failed to get session logs for {session_id}")
            return False
            
        # Download each log type
        success = True
        for log_type, log_url in session_logs.items():
            if not log_url or log_type == 'dashboard_url':
                continue
                
            try:
                response = requests.get(
                    log_url,
                    auth=(self.username, self.access_key)
                )
                response.raise_for_status()
                
                # Determine file extension based on log type
                extension = '.txt'
                if log_type == 'video_url':
                    extension = '.mp4'
                elif log_type == 'network_logs':
                    extension = '.har'
                
                # Save the log
                log_path = scenario_dir / f"{log_type}{extension}"
                mode = 'wb' if log_type == 'video_url' else 'w'
                
                with open(log_path, mode) as f:
                    if mode == 'wb':
                        f.write(response.content)
                    else:
                        f.write(response.text)
                        
                self.logger.info(f"Downloaded {log_type} to {log_path}")
            except Exception as e:
                self.logger.error(f"Failed to download {log_type}: {str(e)}")
                success = False
                
        # Create summary file
        try:
            dashboard_url = session_logs.get('dashboard_url', '')
            summary_path = scenario_dir / 'session_summary.json'
            summary = {
                'session_id': session_id,
                'scenario_name': scenario_name,
                'timestamp': datetime.now().isoformat(),
                'dashboard_url': dashboard_url,
                'artifacts': [k for k, v in session_logs.items() if v and k != 'dashboard_url']
            }
            
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2)
                
            self.logger.info(f"Created session summary at {summary_path}")
        except Exception as e:
            self.logger.error(f"Failed to create summary file: {str(e)}")
            success = False
            
        return success