@echo off
title Pure Python Server (Zero Excel / Zero Windows Required)
color 0A
cd /d "%~dp0"

echo =====================================================================
echo           PURE PYTHON MARKET REPORT SERVER (LINUX NATIVE)
echo              No Windows COM - No Microsoft Excel Required
echo =====================================================================
echo.
echo Starting local test server on http://localhost:8080 ...
echo Open your browser to: http://localhost:8080
echo.
python server.py
pause
