"""
Bridge module to import steps from Shopify-specific step files.
This avoids duplication in step definitions while maintaining compatibility with BrowserStack SDK.
"""
import sys
import os
import logging

logger = logging.getLogger('behave')
logger.info("Loading product_steps.py module")
logger.info(f"Python path: {sys.path}")

# Import step definitions from Shopify-specific modules WITHOUT registering them again
# This avoids the "step already defined" error while maintaining proper imports
from features.steps.Shopify.product_steps import *

# The following code was causing issues with newer versions of behave
# Commenting it out and replacing with a simpler approach

# # Remove duplicated step registrations
# # This is a hack to prevent BrowserStack from finding duplicate step registrations
# import behave.matchers
# import re
# import inspect

# # Store original register_type function to restore it later
# original_register = behave.matchers.registry.register_type

# # Replace register_type with a function that prevents duplicate registrations
# def prevent_duplicate_registrations():
#     steps_already_registered = {}
    
#     # Get the original registry's step patterns
#     for step_type in behave.matchers.registry.step_types:
#         for pattern in behave.matchers.registry.steps[step_type]:
#             steps_already_registered[f"{step_type}:{pattern}"] = True
    
#     # Override the registration function
#     def safe_register(step_type, pattern, func):
#         step_id = f"{step_type}:{pattern}"
#         if step_id in steps_already_registered:
#             logger.info(f"Skipping duplicate step registration: {step_type} {pattern}")
#             return func
#         steps_already_registered[step_id] = True
#         return original_register(step_type, pattern, func)
    
#     behave.matchers.registry.register_type = safe_register

# # Apply the prevention of duplicate registrations
# prevent_duplicate_registrations()

# Simpler approach: Just log that we've loaded the steps
logger.info("Successfully loaded product_steps bridge module")
