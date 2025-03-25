"""
BrowserStack Test Runner for Shopify Tests
This script manages test execution on BrowserStack with improved reporting.
"""
import os
import sys
import argparse
import subprocess
import json
from datetime import datetime
from features.utils.reporting_utils import ReportingUtils

# Set up logging
logger = ReportingUtils.setup_logging("browserstack_tests.log", "browserstack_runner")

def setup_environment():
    """Ensure environment is properly configured for BrowserStack tests"""
    success, error_message = ReportingUtils.setup_environment(is_browserstack=True)
    
    if not success:
        logger.error(error_message)
        logger.info("Please set BROWSERSTACK_USERNAME and BROWSERSTACK_ACCESS_KEY as environment variables.")
        return False
    
    logger.info(f"Set BUILD_NUMBER to {os.environ.get('BUILD_NUMBER')}")
    logger.info(f"Set MAX_RETRIES to {os.environ.get('MAX_RETRIES')} for automatic test retries")
    
    return True

def run_test(feature_path, scenario_line=None, tags=None):
    """Run a specific test on BrowserStack"""
    # Get standardized behave command
    cmd = ReportingUtils.get_behave_command(
        feature_path, 
        tags=tags, 
        is_browserstack=True, 
        scenario_line=scenario_line
    )
    
    # Add additional debugging options
    cmd.extend(["--logging-level=DEBUG"])
    
    logger.info(f"Running command: {' '.join(cmd)}")
    
    try:
        # Execute the command
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Capture output in real-time
        stdout_lines = []
        stderr_lines = []
        
        while True:
            stdout_line = process.stdout.readline()
            stderr_line = process.stderr.readline()
            
            if not stdout_line and not stderr_line and process.poll() is not None:
                break
                
            if stdout_line:
                line = stdout_line.strip()
                logger.info(line)
                stdout_lines.append(line)
                
            if stderr_line:
                line = stderr_line.strip()
                logger.error(line)
                stderr_lines.append(line)
        
        # Get final output
        stdout_remainder, stderr_remainder = process.communicate()
        if stdout_remainder:
            for line in stdout_remainder.strip().split('\n'):
                if line:
                    logger.info(line)
                    stdout_lines.append(line)
                    
        if stderr_remainder:
            for line in stderr_remainder.strip().split('\n'):
                if line:
                    logger.error(line)
                    stderr_lines.append(line)
        
        stdout = '\n'.join(stdout_lines)
        stderr = '\n'.join(stderr_lines)
        
        # Handle threading errors commonly seen during shutdown
        if "can't create new thread at interpreter shutdown" in stderr:
            logger.warning("Detected threading error during shutdown - this is expected and can be ignored")
        
        if process.returncode != 0:
            logger.warning(f"Test execution completed with non-zero exit code: {process.returncode}")
        else:
            logger.info("Test execution completed successfully")
        
        # Parse session IDs from output
        session_ids = ReportingUtils.parse_session_id(stdout)
                    
        return {
            "success": process.returncode == 0,
            "stdout": stdout,
            "stderr": stderr,
            "session_ids": session_ids
        }
    
    except Exception as e:
        logger.error(f"Error running test: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """Main function to run BrowserStack tests"""
    parser = argparse.ArgumentParser(description="Run Shopify tests on BrowserStack")
    parser.add_argument("--feature", default="features/ShopifyTest", 
                        help="Path to feature file or directory to test")
    parser.add_argument("--scenario", type=int, help="Specific scenario line number to test")
    parser.add_argument("--tags", default="@shopify", help="Tags to filter tests (e.g. @shopify)")
    parser.add_argument("--retries", type=int, default=3, help="Number of retries for flaky tests")
    args = parser.parse_args()
    
    logger.info("-----------------------------------")
    logger.info("Starting BrowserStack test execution")
    logger.info("-----------------------------------")
    
    if not setup_environment():
        return 1
    
    # Set MAX_RETRIES from command line argument
    os.environ['MAX_RETRIES'] = str(args.retries)
    logger.info(f"Set MAX_RETRIES to {args.retries} for automatic test retries")
    
    # Run test
    result = run_test(args.feature, args.scenario, args.tags)
    
    if not result.get("success", False):
        logger.error("Test execution failed. Check logs for details.")
        return 1
    
    logger.info("-----------------------------------")
    logger.info("Test execution completed")
    logger.info("-----------------------------------")
    
    # Print session IDs for easy access to BrowserStack dashboard
    if result.get("session_ids"):
        logger.info("BrowserStack session IDs:")
        for session_id in result["session_ids"]:
            logger.info(f"  - {session_id}")
            dashboard_url = ReportingUtils.get_dashboard_url(session_id)
            logger.info(f"  - Dashboard URL: {dashboard_url}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
