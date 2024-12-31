![Linting](https://github.com/sudoDeVinci/devinci.cloud-backend/actions/workflows/python-app.yml/badge.svg?branch=main)

# Devinci.cloud Backend Application

A web application built with Flask and SQLite providing database and routing functionality for the website `devinci.cloud`.

## Project Structure

```json
.
├── main.py
├── README.md
├── requirements.txt
├── logs/
│   └── db.log
|
└── utils/ 
    │ 
    ├── __init__.py
    ├── routes.py
    └── db/
        │ 
        ├── Entities.py 
        ├── Manager.py
        └── schema.py
```