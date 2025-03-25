"""
Test setup script to run Shopify tests with BrowserStack or locally
"""
import os
import sys
import argparse
import subprocess
from datetime import datetime
from features.utils.reporting_utils import ReportingUtils

def setup_environment(is_browserstack):
    """Set up environment variables for test execution"""
    logger = ReportingUtils.setup_logging("test_execution.log", "test_setup")
    
    success, error_message = ReportingUtils.setup_environment(is_browserstack)
    
    if not success and error_message:
        logger.error(error_message)
        logger.info("Please set BROWSERSTACK_USERNAME and BROWSERSTACK_ACCESS_KEY as environment variables.")
        return False, logger
    
    logger.info(f"Set BUILD_NUMBER to {os.environ.get('BUILD_NUMBER')}")
    logger.info(f"Set MAX_RETRIES to {os.environ.get('MAX_RETRIES')} for automatic test retries")
    if is_browserstack:
        logger.info("BrowserStack local testing disabled")
    
    return True, logger

def run_tests(feature_path, tags, is_browserstack, retries=3, logger=None):
    """Run tests either locally or on BrowserStack"""
    if logger is None:
        logger = ReportingUtils.setup_logging("test_execution.log", "test_setup")
    
    # Set MAX_RETRIES from parameter
    os.environ['MAX_RETRIES'] = str(retries)
    logger.info(f"Set MAX_RETRIES to {retries} for automatic test retries")
    
    # Get standardized behave command
    cmd = ReportingUtils.get_behave_command(
        feature_path, 
        tags=tags, 
        is_browserstack=is_browserstack
    )
    
    logger.info(f"Running command: {' '.join(cmd)}")
    
    # Execute the command with real-time output
    process = subprocess.Popen(
        cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Capture output in real-time
    for line in iter(process.stdout.readline, ''):
        if line:
            logger.info(line.strip())
    
    # Get any remaining output
    stdout, stderr = process.communicate()
    
    if stderr:
        for line in stderr.strip().split('\n'):
            if line:
                logger.error(line)
    
    # Parse session IDs if running on BrowserStack
    if is_browserstack:
        session_ids = ReportingUtils.parse_session_id(stdout)
        if session_ids:
            logger.info("BrowserStack session IDs:")
            for session_id in session_ids:
                logger.info(f"  - {session_id}")
                dashboard_url = ReportingUtils.get_dashboard_url(session_id)
                logger.info(f"  - Dashboard URL: {dashboard_url}")
    
    return process.returncode

def main():
    """Main function to run tests"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run Shopify tests locally or on BrowserStack")
    parser.add_argument("--feature", default="features/ShopifyTest", 
                        help="Path to feature file or directory to test")
    parser.add_argument("--tags", default="@shopify", 
                        help="Tags to filter tests (e.g. @shopify)")
    parser.add_argument("--browserstack", action="store_true", 
                        help="Run tests on BrowserStack instead of locally")
    parser.add_argument("--retries", type=int, default=3, 
                        help="Number of retries for flaky tests")
    args = parser.parse_args()
    
    # Check if we're running on BrowserStack
    is_browserstack = args.browserstack or (
        os.environ.get('BROWSERSTACK_USERNAME') and 
        os.environ.get('BROWSERSTACK_ACCESS_KEY')
    )
    
    # Set up environment
    success, logger = setup_environment(is_browserstack)
    if not success:
        return 1
    
    logger.info("-----------------------------------")
    logger.info("Starting test execution")
    logger.info("-----------------------------------")
    
    # Run tests
    return_code = run_tests(args.feature, args.tags, is_browserstack, args.retries, logger)
    
    logger.info("-----------------------------------")
    logger.info(f"Test execution completed with return code: {return_code}")
    logger.info("-----------------------------------")
    
    return return_code

if __name__ == "__main__":
    sys.exit(main())
