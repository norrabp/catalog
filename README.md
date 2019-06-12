# Catalog
Backend of a Web Catalog. Made from python, Flask, SQLAlchemy, and Marshmallow

## Install

Install [Python2.7](https://www.python.org/download/releases/2.7/) and [MySQL8.0.16.0](https://dev.mysql.com/downloads/)

Clone this project

```
$ git clone https://github.com/norrabp/catalog.git platform
```

Install project dependencies:

```
cd platform
pip install -r requirements.txt
```

Install the python environment if needed

```
pip install virtualenv
```

cd into whichever directory the python `env` directory is and activate with
```
source env/bin/activate
```

## Setup

You will need to connect with whichever instance of a mysql database you will need to use

##### MySQL setup:
- Go into the config folder
- Edit each config.py.example file with the following
- set SQLALCHEMY_DATABASE_URI equal to the mysql database URI that you are going to be using

##### 

## Environments
If testing run the following command (may differ between systems)

```
export FLASK_CONFIG=testing
```

If developing run the following command (If you need to check that authentication works don't use this environment)

```
export FLASK_CONFIG=development
```

If deploying to production run the following

```
export FLASK_CONFIG=development
```

## Project Structure

The repository should look like this:
.
├── README.md
├── catalog
│   ├── app
│   │   ├── __init__.py
│   │   ├── api_v1
│   │   │   ├── __init__.py
│   │   │   ├── categories.py
│   │   │   ├── errors.py
│   │   │   └── items.py
│   │   ├── auth.py
│   │   ├── exceptions.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── config
│   │   ├── development.py
│   │   ├── production.py
│   │   ├── testing.py
│   ├── run.py
│   ├── test.py
│   └── tests
│       ├── __init__.py
│       ├── catalog.json
│       ├── test_client.py
│       ├── tests.py
└── requirements.txt

The website is designed around Categories, which are containers for Items

`models.py` contains the SQLAlchemy database models and 
`schemas.py` contain the Marshmallow schemas for Categories and Items

`auth.py` contains the authentication APIs (except for `get-auth-token`)

`/config` contains the configuration files as explained earlier

`/tests` contains `tests.py`, which contains the test cases and `test_client.py` which is the mechanism by which `tests.py` communicates with the website APIs

`/api_v1` contains the APIs for Categories, Items, and Errors respectively

`exceptions.py` contains a custom exception used

`/catalog/app/__init__.py` will create the Flask application, set the configuration based on the environment variable, link with the SQLAlchemy db and Marshmallow, import the api blueprint and set up the token generation API. It is from this file that `db` and `app` will be imported\created from

## Running the Application

To run the application normally, type in 

```
python run.py
```

`run.py` will configure a user `GotIt` with password `GotItAI` from which you can obtain your token from

To run the tests, run
```
python tests.py
```

## APIs

Run the following commands in your terminal (separate from the one running the instance of the website)

##### Get Token
To obtain a JSON object with your token 

```
http --auth GotIt:GotItAI http://localhost:5000/get-auth-token
```

You should receive a response like this
```
{
    "token": "eyJhbGciOiJIUzI1NiIsImV4cCI6MTU2MDMwODc0NiwiaWF0IjoxNTYwMzA1MTQ2fQ.eyJpZCI6MX0.T9fycT3Lg6AXjua57_3cc8VwEpn3nHHhcTYXsiChiYU"
}
```
When making any `POST`, `PUT`, or `DELETE` requests begin them with the following

```
http --auth <YOUR TOKEN HERE> <Method> http://localhost:5000/<rest of URL> <headers>
```

### Category

##### Getters

- Get a list of all categories
    - Command: `http GET http://localhost:5000/api/v1/categories`
    - Returns:
        - Status Code: `200`
        - Data: {
                    "categories": [
                        {
                            "id": <id>,
                            "name": <category name>
                            "items": [
                                <item id>
                            ]
                        }
                    ]
                }

- Get a specific category
    - Command: `http GET http://localhost:5000/api/v1/categories/<id>`
    - Returns:
        - Status Code: `200`
        - Data: {
                    "id": <id>,
                    "name": <category name>
                    "items": [
                        {
                            <item id>
                        }
                    ]
                }

##### Create

- Create a new category
    - Command: `http --auth <your token>: POST http://localhost:5000/api/v1/categories name=<category name>`
    - Returns:
        - Status Code: `201`
        - Data: {
                    "id: <id>
                    "name": <category name>
                    "items": []
                }

##### Edit

- Edit a category
    - Command: `http --auth <your token>: PUT http://localhost:5000/api/v1/categories/<id> name=<new category name>`
    - Returns:
        - Status Code: `200`
        - Data: {
                    "id": <id>,
                    "items": [
                        <item id>
                    ],
                    "name": <category name>
                }

##### Delete

- Delete a category
    - Command: `http --auth <your token>: DELETE http://localhost:5000/api/v1/categories/<id>`
    - Returns:
        - Status Code: `204`

### Items

##### Getters

 - Get all Items in a category
    - Command: `http GET http://localhost:5000/api/v1/categories/<id>/items`
    - Returns:
        - Status Code: `200`
        - Data: {
                    "<category name> items": [
                        {
                            "id": <item id>
                            "title": <item title>
                            "description": <item description>
                            "category": <category id>
                        }
                    ]
                }

- Get all Items
    - Command: `http GET http://localhost:5000/api/v1/items`
    - Returns:
        - Status Code: `200`
        - Data: {
                    "Items": [
                        {
                            "id": <item id>
                            "title": <item title>
                            "description": <item description>
                            "category": <category id> 
                        }
                    ]
                }

- Get a specific Item
    - Command: `http GET http://localhost:5000/api/v1/items/<id>`
    - Returns:
        - Status Code: `200`
        - Data: {
                    "id": <item id>
                    "title": <item title>
                    "description": <item description>
                    "category": <category id>
                }

##### Create

- Create a new Item
    - Command: `http --auth <your token>: POST http://localhost:5000/api/v1/categories/<category id>/items title=<item title> description=<item description>`
    - Returns:
        - Status Code: `201`
        - Data: {
                    "id": <item id>
                    "title": <item title>
                    "description": <item description>
                    "category": <category id>
                }

##### Edit

NOTE: This api is designed so that you are allowed to edit between 0 and 3 attributes. You can edit simply the title and the description and category remain the same. You can also edit the category of the item if you want to put it in a new category

- Edit an Item
    - Command: `http --auth <your token>: PUT http://localhost:5000/api/v1/items/<id> title=<new title> description=<new description> category=<new category id>`
    - Returns:
        - Status Code: `200`
        - Data: {
                    "id": <item id>
                    "title": <item title>
                    "category": <category id>
                    "description": <item description>
                }

##### Delete
- Delete an Item
    - Command: `http --auth <your token>: DELETE http://localhost:5000/api/v1/items/<id>`
    - Returns:
        - Status Code: `204`


