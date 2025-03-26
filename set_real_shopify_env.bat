@echo off
REM Set environment variables for real Shopify API testing
SET USE_MOCK_MCP=false
SET SHOPIFY_MCP_SERVER=http://localhost:3000
SET SHOPIFY_API_KEY=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
SET SHOPIFY_DOMAIN=pre-production-dss.myshopify.com

REM Set the same variables for PowerShell in the same session
powershell -Command "$env:USE_MOCK_MCP='false'; $env:SHOPIFY_MCP_SERVER='http://localhost:3000'; $env:SHOPIFY_API_KEY='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'; $env:SHOPIFY_DOMAIN='pre-production-dss.myshopify.com';"

echo Environment variables set for real Shopify API testing.
echo USE_MOCK_MCP=%USE_MOCK_MCP%
echo SHOPIFY_MCP_SERVER=%SHOPIFY_MCP_SERVER%
echo Remember to replace the placeholder API key with your actual key.
