# ShoppingList API

[![Build Status](https://travis-ci.org/flacode/shopping_list.png)](https://travis-ci.org/flacode/shopping_list)     [![Coverage Status](https://coveralls.io/repos/github/flacode/shopping_list/badge.svg)](https://coveralls.io/github/flacode/shopping_list)
[![Test Coverage](https://api.codeclimate.com/v1/badges/08889291e991002973ae/test_coverage)](https://codeclimate.com/github/flacode/shopping_list/test_coverage)
[![Maintainability](https://api.codeclimate.com/v1/badges/08889291e991002973ae/maintainability)](https://codeclimate.com/github/flacode/shopping_list/maintainability)

> ShoppingList is a simple API that allows users to record, share and keep track of their shopping lists.

## Features
- Users can create accounts.
- Users can log in.
- Users can create, view, update and delete shopping lists. 
- Users can add, update, view or delete items in a shopping list

## API documentation

Documentation for the API can be found at https://shoppinglist12.docs.apiary.io/#

## Tools
Tools used for development of this API are;
- Documentation : [Apiary](https://apiary.io/)
- Database: [Postgresql](https://www.postgresql.org)
- Microframework: [Flask](http://flask.pocoo.org/)
- Editor: [Vs code](https://code.visualstudio.com)
- Programming language: [Python 3.x.x](https://docs.python.org/3/)
- API development environment: [Postman](https://www.getpostman.com)

## Running the tests

From the project's repository, to run tests, use
```sh
   python -m pytest tests/ 
 ``` 

## Getting Started
### Prerequisites
1. Install requirements, run 
```sh
     pip install -r requirements.txt
```
2. Database configuration.
   - Download and install postgres from [here](https://www.postgresql.org/download/)
   - Create database in terminal
   ```sh
      psql postgres;
      CREATE DATABASE database_name;
   ```
   - Connect the application to the database by changing the ``` POSTGRES ``` variable in shopping_list/app/__init__.py.
   ```
      POSTGRES = {
            'user': 'database user',
            'pw': 'user password',
            'db': 'database name',
            'host': 'localhost',
            'port': '5432',
            }
   ```
3. To create database tables, from the project's repository run 
```sh 
    $ python manage.py db init
    $ python manage.py db migrate
    $ python manage.py db upgrade
    $ python run.py runserver
 ```
### Base URL for the API
URL: https://deployment-shopping-list-api.herokuapp.com/api

## End points
### Endpoints to create a user account and login into the application
HTTP Method|End point | Public Access|Action
-----------|----------|--------------|------
POST | /auth/register | True | Create an account
POST | /auth/login | True | Login a user
POST | /auth/logout | False | Logout a user
POST | /auth/reset-password | False | Reset a user password
GET | /auth/users | True | View all registered user accounts
GET | /auth/user/<user_id> | True | View details of a registered account
DELETE | /auth/user/<user_id> | True | Delete user account

### Endpoints to create, update, view and delete a shopping list
HTTP Method|End point | Public Access|Action
-----------|----------|--------------|------
POST | /shoppinglists/ | False | Create a shopping list
GET | /shoppinglists/ | False | View all shopping lists
GET | /shoppinglists/<list_id> | False | View details of a shopping list
PUT | /shoppinglists/<list_id> | False | Updates a shopping list with a given id
DELETE | /shoppinglists/<list_id> | False | Deletes a shopping list with a given id

### Endpoints to create, update, view and delete a shopping list item
HTTP Method|End point | Public Access|Action
-----------|----------|--------------|------
POST | /shoppinglists/<list_id>/items/ | False | Add an Item to a shopping list
PUT | /shoppinglists/<list_id>/items/<item_id> | False | Update a shopping list item on a given list
GET | /shoppinglists/<list_id>/items/ | False | View items in a particular shopping list
DELETE | /shoppinglists/<list_id>/items/<item_id> | False | Delete an item from a given shopping list


