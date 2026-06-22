@echo off
title VillageBid Django Setup

echo ==========================================
echo VILLAGEBID DJANGO PROJECT SETUP
echo ==========================================
echo.

cd /d D:\village_bid_approval

echo Creating Virtual Environment...
python -m venv venv

echo.
echo Activating Virtual Environment...
call venv\Scripts\activate

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing Required Packages...

pip install django
pip install djangorestframework
pip install djangorestframework-simplejwt
pip install psycopg2-binary
pip install pillow
pip install python-dotenv
pip install django-crispy-forms
pip install crispy-bootstrap5

echo.
echo Saving requirements.txt...
pip freeze > requirements.txt

echo.
echo Creating Django Project...
django-admin startproject config .

echo.
echo Creating Applications...

python manage.py startapp accounts
python manage.py startapp core
python manage.py startapp categories
python manage.py startapp products
python manage.py startapp auctions
python manage.py startapp bids
python manage.py startapp dashboard
python manage.py startapp messages_app
python manage.py startapp notifications
python manage.py startapp payments
python manage.py startapp reviews
python manage.py startapp favorites
python manage.py startapp reports
python manage.py startapp adminpanel

echo.
echo Creating Directories...

mkdir templates
mkdir static
mkdir media

mkdir templates\base
mkdir templates\core
mkdir templates\accounts
mkdir templates\products
mkdir templates\auctions
mkdir templates\dashboard

mkdir static\css
mkdir static\js
mkdir static\images

echo.
echo Running Initial Migration...

python manage.py migrate

echo.
echo ==========================================
echo SETUP COMPLETED SUCCESSFULLY
echo ==========================================
echo.
echo To start server:
echo.
echo call venv\Scripts\activate
echo python manage.py runserver
echo.
pause