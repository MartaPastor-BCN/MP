#!/usr/bin/env pwsh

Write-Host "Installing Deal ID Audit Tool dependencies..." -ForegroundColor Green
Write-Host ""

Write-Host "Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

Write-Host ""
Write-Host "Installing Streamlit, Pandas, and NumPy..." -ForegroundColor Cyan
python -m pip install streamlit pandas numpy

Write-Host ""
Write-Host "===================================="  -ForegroundColor Green
Write-Host "Installation complete!"  -ForegroundColor Green
Write-Host "===================================="  -ForegroundColor Green
Write-Host ""
Write-Host "To run the app, execute:" -ForegroundColor Yellow
Write-Host "   streamlit run app.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "The app will open at: http://localhost:8501" -ForegroundColor Yellow
Write-Host ""
