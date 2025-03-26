@echo off
REM Set environment variables for real Shopify API testing
SET USE_MOCK_MCP=false
SET SHOPIFY_MCP_SERVER=http://localhost:3000

REM Get API key and domain from .env file
FOR /F "tokens=1,* delims==" %%A IN ('type .env ^| findstr "SHOPIFY_API_KEY"') DO SET SHOPIFY_API_KEY=%%B
FOR /F "tokens=1,* delims==" %%A IN ('type .env ^| findstr "SHOPIFY_DOMAIN"') DO SET SHOPIFY_DOMAIN=%%B

REM Set the same variables for PowerShell in the same session
powershell -Command "$env:USE_MOCK_MCP='false'; $env:SHOPIFY_MCP_SERVER='http://localhost:3000'; $env:SHOPIFY_API_KEY='%SHOPIFY_API_KEY%'; $env:SHOPIFY_DOMAIN='%SHOPIFY_DOMAIN%';"

echo Environment variables set for real Shopify API testing.
echo USE_MOCK_MCP=%USE_MOCK_MCP%
echo SHOPIFY_MCP_SERVER=%SHOPIFY_MCP_SERVER%
echo SHOPIFY_API_KEY=%SHOPIFY_API_KEY%
echo SHOPIFY_DOMAIN=%SHOPIFY_DOMAIN%
