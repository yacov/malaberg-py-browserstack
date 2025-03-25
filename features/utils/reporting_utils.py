"""
Reporting utilities for test execution.
Provides common functionality for logging, report generation, and test result tracking.
"""
import os
import logging
import json
import sys
from datetime import datetime
from pathlib import Path

class ReportingUtils:
    """
    Centralized reporting functionality for both local and BrowserStack test execution.
    """
    
    @staticmethod
    def setup_logging(log_file="test_execution.log", logger_name="test_runner"):
        """
        Set up standardized logging configuration.
        
        Args:
            log_file: Name of the log file
            logger_name: Name of the logger
            
        Returns:
            Configured logger instance
        """
        # Create necessary directories
        os.makedirs("reports", exist_ok=True)
        os.makedirs("screenshots", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(name)s][%(levelname)s] - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        return logging.getLogger(logger_name)
    
    @staticmethod
    def get_behave_command(feature_path, tags=None, is_browserstack=False, scenario_line=None):
        """
        Generate a standardized behave command with appropriate arguments.
        
        Args:
            feature_path: Path to feature file or directory
            tags: Tags to filter tests
            is_browserstack: Whether to run on BrowserStack
            scenario_line: Specific scenario line number
            
        Returns:
            List of command arguments
        """
        # Base command
        if is_browserstack:
            cmd = ["browserstack-sdk", "behave"]
        else:
            cmd = ["behave"]
        
        # Add feature path
        feature_spec = feature_path
        if scenario_line:
            feature_spec = f"{feature_path}:{scenario_line}"
        cmd.append(feature_spec)
        
        # Add tags if specified
        if tags:
            cmd.extend(["--tags", tags])
        
        # Add common arguments
        cmd.extend(["-v", "--no-capture", "--no-skipped"])
        
        # Add format for better reporting
        report_file = "browserstack-report.json" if is_browserstack else "local-report.json"
        
        # Use different format options based on whether we're using BrowserStack or not
        if is_browserstack:
            # BrowserStack SDK only supports simple formats
            cmd.extend([
                "--format=pretty"
            ])
        else:
            # For local runs, we can use more advanced formats
            cmd.extend([
                "--format=pretty", 
                f"--format=json:reports/{report_file}"
            ])
        
        return cmd
    
    @staticmethod
    def setup_environment(is_browserstack=False):
        """
        Set up environment variables for test execution.
        
        Args:
            is_browserstack: Whether running on BrowserStack
            
        Returns:
            Tuple of (success, error_message)
        """
        # Set BUILD_NUMBER for consistent builds
        if not os.environ.get('BUILD_NUMBER'):
            build_number = datetime.now().strftime("%Y%m%d%H%M%S")
            os.environ['BUILD_NUMBER'] = build_number
        
        # Set MAX_RETRIES for flaky tests if not already set
        if not os.environ.get('MAX_RETRIES'):
            os.environ['MAX_RETRIES'] = '3'
        
        # Set PYTHONPATH for consistent imports
        os.environ['PYTHONPATH'] = os.getcwd()
        
        # Add current directory to Python path
        if os.getcwd() not in sys.path:
            sys.path.insert(0, os.getcwd())
        
        # Explicitly disable BrowserStack local testing
        if is_browserstack:
            os.environ['BROWSERSTACK_LOCAL'] = 'false'
            
            # Check BrowserStack credentials
            required_vars = ['BROWSERSTACK_USERNAME', 'BROWSERSTACK_ACCESS_KEY']
            missing = [var for var in required_vars if not os.environ.get(var)]
            
            if missing:
                return False, f"Missing required environment variables: {', '.join(missing)}"
        
        return True, None
    
    @staticmethod
    def parse_session_id(output):
        """
        Parse BrowserStack session ID from command output.
        
        Args:
            output: Command output string
            
        Returns:
            List of session IDs found
        """
        session_ids = []
        for line in output.split('\n'):
            if "SDK run started with id:" in line:
                try:
                    session_id = line.split("SDK run started with id:")[1].split(",")[0].strip()
                    session_ids.append(session_id)
                except:
                    pass
        return session_ids
    
    @staticmethod
    def get_dashboard_url(session_id):
        """
        Get BrowserStack dashboard URL for a session.
        
        Args:
            session_id: BrowserStack session ID
            
        Returns:
            Dashboard URL
        """
        return f"https://automate.browserstack.com/builds/sessions/{session_id}"
    
    @staticmethod
    def collect_browserstack_artifacts(session_id, scenario_name, context=None):
        """
        Collect BrowserStack artifacts for a session.
        
        Args:
            session_id: BrowserStack session ID
            scenario_name: Name of the scenario
            context: Optional behave context object
            
        Returns:
            True if artifacts were collected successfully, False otherwise
        """
        try:
            from features.utils.browserstack_logger import BrowserStackLogger
            logger = BrowserStackLogger(context)
            return logger.download_session_artifacts(session_id, scenario_name)
        except Exception as e:
            logging.getLogger('reporting_utils').error(f"Failed to collect BrowserStack artifacts: {str(e)}")
            return False
    
    @staticmethod
    def generate_test_summary(results_file="reports/browserstack-report.json", output_file="reports/summary.html"):
        """
        Generate a HTML summary report from JSON test results.
        
        Args:
            results_file: Path to JSON results file
            output_file: Path to output HTML file
            
        Returns:
            True if summary was generated successfully, False otherwise
        """
        try:
            # Check if results file exists
            if not os.path.exists(results_file):
                return False
                
            # Read JSON results
            with open(results_file, 'r') as f:
                results = json.load(f)
                
            # Extract statistics
            stats = {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'duration': 0
            }
            
            scenarios = []
            
            # Process features
            for feature in results:
                for element in feature.get('elements', []):
                    if element.get('type') == 'scenario':
                        stats['total'] += 1
                        
                        # Determine scenario status
                        status = 'passed'
                        for step in element.get('steps', []):
                            if step.get('result', {}).get('status') == 'failed':
                                status = 'failed'
                                break
                            elif step.get('result', {}).get('status') == 'skipped':
                                status = 'skipped'
                        
                        # Update stats
                        stats[status] += 1
                        
                        # Calculate duration
                        duration = 0
                        for step in element.get('steps', []):
                            duration += step.get('result', {}).get('duration', 0)
                        stats['duration'] += duration
                        
                        # Add scenario details
                        scenarios.append({
                            'name': element.get('name', 'Unnamed Scenario'),
                            'feature': feature.get('name', 'Unnamed Feature'),
                            'status': status,
                            'duration': duration / 1000000000  # Convert nanoseconds to seconds
                        })
            
            # Generate HTML report
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Test Execution Summary</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1, h2 {{ color: #333; }}
                    .summary {{ display: flex; margin-bottom: 20px; }}
                    .stat {{ margin-right: 20px; padding: 10px; border-radius: 5px; }}
                    .total {{ background-color: #f0f0f0; }}
                    .passed {{ background-color: #dff0d8; }}
                    .failed {{ background-color: #f2dede; }}
                    .skipped {{ background-color: #fcf8e3; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    tr.passed {{ background-color: #dff0d8; }}
                    tr.failed {{ background-color: #f2dede; }}
                    tr.skipped {{ background-color: #fcf8e3; }}
                </style>
            </head>
            <body>
                <h1>Test Execution Summary</h1>
                <div class="summary">
                    <div class="stat total">Total: {stats['total']}</div>
                    <div class="stat passed">Passed: {stats['passed']}</div>
                    <div class="stat failed">Failed: {stats['failed']}</div>
                    <div class="stat skipped">Skipped: {stats['skipped']}</div>
                    <div class="stat total">Duration: {stats['duration'] / 1000000000:.2f}s</div>
                </div>
                
                <h2>Scenario Details</h2>
                <table>
                    <tr>
                        <th>Feature</th>
                        <th>Scenario</th>
                        <th>Status</th>
                        <th>Duration (s)</th>
                    </tr>
            """
            
            # Add scenario rows
            for scenario in scenarios:
                html += f"""
                    <tr class="{scenario['status']}">
                        <td>{scenario['feature']}</td>
                        <td>{scenario['name']}</td>
                        <td>{scenario['status'].upper()}</td>
                        <td>{scenario['duration']:.2f}</td>
                    </tr>
                """
                
            html += """
                </table>
                
                <h2>Execution Information</h2>
                <p>Generated on: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
            </body>
            </html>
            """
            
            # Write HTML report
            with open(output_file, 'w') as f:
                f.write(html)
                
            return True
        except Exception as e:
            logging.getLogger('reporting_utils').error(f"Failed to generate test summary: {str(e)}")
            return False
