# Cardless-Transaction-In-Banking-System-Project

This is an academic project based on Django Web Framework.

# To Generate (and view) a graphviz graph of app models:

$ python manage.py graph_models -a -o myapp_models.png


# Project Title

## ecommerce

The website project of KS Friends chemical ltd.

## Demo link:

Access The site at [ecommerce.com](https://ecommerce.com/)

## Table of Content:

- [About The App](#about-the-app)
- [Technologies](#technologies)
- [Setup](#setup)
- [Approach](#approach)
- [Status](#status)
- [Credits](#credits)
- [License](#license)

## About The App

This project is using Django 4.1 and python 3.9.

### Main features

# Getting Started

## Setup

First clone the repository from Github and switch to the new directory:

    $ git clone https://github.com/ahsaan-habib/Cardless-Transaction-In-Banking-System-Project.git
    $ cd Cardless-Transaction-In-Banking-System-Project

Activate the virtualenv for your project.(linux)

    $ python -m venv venv
    $ source env/bin/activate

Or, Activate the virtualenv for your project.(Windows git bash)

    $ python -m venv venv
    $ source env/Scripts/activate

Install project dependencies:

    $ pip install -r requirements.txt

Then simply apply the migrations:
(sometimes take a look in database configuration)

    $ python manage.py makemigrations
    $ python manage.py migrate


it will start tailwind in watch mode.

Finally, run the Django development server:

    $ python manage.py runserver

That's it. You can now access

    the site at http://localhost:8000/
    admin panel: http://localhost:8000/admin

Enjoy Django Developing! :)

