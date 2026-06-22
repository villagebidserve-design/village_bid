@echo off
title VillageBid Migration Reset

echo ==========================================
echo VILLAGEBID DATABASE RESET
echo ==========================================
echo.

cd /d D:\village_bid_approval

call venv\Scripts\activate

echo.
echo Deleting SQLite database...

if exist db.sqlite3 (
    del /f /q db.sqlite3
    echo db.sqlite3 deleted
) else (
    echo db.sqlite3 not found
)

echo.
echo Removing migration files...

for %%d in (
accounts
core
categories
products
auctions
bids
dashboard
messages_app
notifications
payments
reviews
favorites
reports
adminpanel
) do (

    if exist %%d\migrations (

        del /f /q %%d\migrations\0*.py 2>nul
        del /f /q %%d\migrations\1*.py 2>nul
        del /f /q %%d\migrations\2*.py 2>nul
        del /f /q %%d\migrations\3*.py 2>nul
        del /f /q %%d\migrations\4*.py 2>nul
        del /f /q %%d\migrations\5*.py 2>nul
        del /f /q %%d\migrations\6*.py 2>nul
        del /f /q %%d\migrations\7*.py 2>nul
        del /f /q %%d\migrations\8*.py 2>nul
        del /f /q %%d\migrations\9*.py 2>nul

        echo Cleaned %%d migrations
    )
)

echo.
echo Creating fresh migrations...

python manage.py makemigrations accounts

if errorlevel 1 (
    echo.
    echo ==========================================
    echo ERROR DURING MAKEMIGRATIONS
    echo ==========================================
    pause
    exit /b
)

echo.
echo Running migrate...

python manage.py migrate

if errorlevel 1 (
    echo.
    echo ==========================================
    echo ERROR DURING MIGRATE
    echo ==========================================
    pause
    exit /b
)

echo.
echo ==========================================
echo SUCCESS
echo ==========================================
echo.
echo Next command:
echo.
echo python manage.py createsuperuser
echo.
pause