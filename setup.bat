@echo off
echo Installing Deal ID Audit Tool dependencies...
echo.

python -m pip install --upgrade pip
echo.
echo Installing Streamlit, Pandas, and NumPy...
python -m pip install streamlit pandas numpy

echo.
echo.
echo ====================================
echo Installation complete!
echo ====================================
echo.
echo To run the app, execute:
echo   streamlit run app.py
echo.
echo The app will open at: http://localhost:8501
echo.
pause
