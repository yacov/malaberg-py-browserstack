"""
Utility functions for BrowserStack integration.
Provides helper methods for session management, test status reporting, and debugging.
"""
import os
import json
import requests
from urllib.parse import urljoin
from features.utils.reporting_utils import ReportingUtils

class BrowserStackUtils:
    """
    Helper class for BrowserStack-specific functionality.
    Provides methods for session management and test status reporting.
    """
    
    def __init__(self, context):
        """
        Initialize BrowserStackUtils with a behave context.
        
        Args:
            context: Behave context object
        """
        self.context = context
        self.username = os.environ.get('BROWSERSTACK_USERNAME')
        self.access_key = os.environ.get('BROWSERSTACK_ACCESS_KEY')
        self.session_id = None
        
        # Extract session ID if driver is available
        if hasattr(context, 'driver'):
            try:
                self.session_id = context.driver.session_id
            except:
                pass
        elif hasattr(context, 'browser'):
            try:
                self.session_id = context.browser.session_id
            except:
                pass
    
    def mark_test_status(self, status, reason=None):
        """
        Mark the test status in BrowserStack.
        
        Args:
            status: 'passed' or 'failed'
            reason: Reason for failure (optional)
            
        Returns:
            True if status was updated successfully, False otherwise
        """
        if not self.session_id or not self.username or not self.access_key:
            return False
        
        url = f"https://api.browserstack.com/automate/sessions/{self.session_id}.json"
        
        data = {'status': status}
        if reason:
            data['reason'] = reason
        
        try:
            response = requests.put(
                url,
                data=json.dumps(data),
                auth=(self.username, self.access_key),
                headers={'Content-Type': 'application/json'}
            )
            return response.status_code == 200
        except Exception as e:
            if hasattr(self.context, 'logger'):
                self.context.logger.error(f"Failed to update BrowserStack status: {str(e)}")
            return False
    
    def get_session_url(self):
        """
        Get the BrowserStack session URL for debugging.
        
        Returns:
            BrowserStack session URL or None if not available
        """
        if not self.session_id or not self.username or not self.access_key:
            return None
        
        return ReportingUtils.get_dashboard_url(self.session_id)
    
    def get_session_video_url(self):
        """
        Get the BrowserStack session video URL.
        
        Returns:
            BrowserStack session video URL or None if not available
        """
        if not self.session_id or not self.username or not self.access_key:
            return None
        
        url = f"https://api.browserstack.com/automate/sessions/{self.session_id}.json"
        
        try:
            response = requests.get(
                url,
                auth=(self.username, self.access_key)
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('automation_session', {}).get('video_url')
            return None
        except Exception as e:
            if hasattr(self.context, 'logger'):
                self.context.logger.error(f"Failed to get BrowserStack video URL: {str(e)}")
            return None
    
    def set_session_name(self, name):
        """
        Set the name of the BrowserStack session.
        
        Args:
            name: Name to set for the session
            
        Returns:
            True if name was set successfully, False otherwise
        """
        if not self.session_id or not self.username or not self.access_key:
            return False
        
        url = f"https://api.browserstack.com/automate/sessions/{self.session_id}.json"
        
        try:
            response = requests.put(
                url,
                data=json.dumps({'name': name}),
                auth=(self.username, self.access_key),
                headers={'Content-Type': 'application/json'}
            )
            return response.status_code == 200
        except Exception as e:
            if hasattr(self.context, 'logger'):
                self.context.logger.error(f"Failed to set BrowserStack session name: {str(e)}")
            return False
    
    def add_session_annotation(self, annotation):
        """
        Add an annotation to the BrowserStack session for debugging.
        
        Args:
            annotation: Text annotation to add
            
        Returns:
            True if annotation was added successfully, False otherwise
        """
        if not self.session_id or not self.username or not self.access_key:
            return False
        
        url = f"https://api.browserstack.com/automate/sessions/{self.session_id}/annotations"
        
        try:
            response = requests.post(
                url,
                data=json.dumps({'text': annotation}),
                auth=(self.username, self.access_key),
                headers={'Content-Type': 'application/json'}
            )
            return response.status_code == 200
        except Exception as e:
            if hasattr(self.context, 'logger'):
                self.context.logger.error(f"Failed to add BrowserStack annotation: {str(e)}")
            return False
            
    def update_test_status_from_scenario(self, scenario):
        """
        Update BrowserStack test status based on scenario result.
        
        Args:
            scenario: Behave scenario object
            
        Returns:
            True if status was updated successfully, False otherwise
        """
        status = 'passed' if scenario.status == 'passed' else 'failed'
        reason = None
        
        if status == 'failed':
            # Extract failure reason from steps
            for step in scenario.steps:
                if step.status == 'failed':
                    reason = f"Step failed: {step.name}"
                    if step.exception:
                        reason += f" - {str(step.exception)}"
                    break
        
        return self.mark_test_status(status, reason)
    
    @staticmethod
    def is_browserstack_enabled():
        """
        Check if BrowserStack is enabled based on environment variables.
        
        Returns:
            True if BrowserStack is enabled, False otherwise
        """
        return bool(os.environ.get('BROWSERSTACK_USERNAME') and os.environ.get('BROWSERSTACK_ACCESS_KEY'))
    
    def get_session_logs(self):
        """
        Get the BrowserStack session logs.
        
        Returns:
            Dictionary with log URLs or None if not available
        """
        if not self.session_id or not self.username or not self.access_key:
            return None
        
        url = f"https://api.browserstack.com/automate/sessions/{self.session_id}.json"
        
        try:
            response = requests.get(
                url,
                auth=(self.username, self.access_key)
            )
            
            if response.status_code == 200:
                data = response.json()
                automation_session = data.get('automation_session', {})
                
                return {
                    'text_logs': automation_session.get('logs'),
                    'console_logs': automation_session.get('browser_console_logs_url'),
                    'network_logs': automation_session.get('har_logs_url'),
                    'selenium_logs': automation_session.get('selenium_logs_url'),
                    'video_url': automation_session.get('video_url'),
                    'dashboard_url': self.get_session_url()
                }
            return None
        except Exception as e:
            if hasattr(self.context, 'logger'):
                self.context.logger.error(f"Failed to get BrowserStack logs: {str(e)}")
            return None
