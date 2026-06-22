@echo off
echo Fixing VillageBid Database...
echo.
echo Step 1: Closing any running Python/Django servers...
taskkill /F /IM python.exe 2>nul

echo.
echo Step 2: Waiting for processes to release locks...
timeout /t 2 /nobreak

echo.
echo Step 3: Deleting old database...
del db.sqlite3 2>nul

echo.
echo Step 4: Running migrations...
call .\venv\Scripts\python manage.py makemigrations
call .\venv\Scripts\python manage.py migrate

echo.
echo Step 5: Creating superuser...
echo To create a superuser, the script will open an interactive prompt.
echo Enter: username, email, password when prompted.
call .\venv\Scripts\python manage.py createsuperuser

echo.
echo Done! Your database is now fixed.
echo You can now run: python manage.py runserver
pause
