@echo off
echo Activating virtual environment...
call .\web-scraper-venv\Scripts\activate
echo Running Python script...
python scrape_kenpom.py
echo Script finished running.
pause
