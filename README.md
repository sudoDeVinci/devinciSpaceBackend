![Linting](https://github.com/sudoDeVinci/devinci.cloud/actions/workflows/linting.yml/badge.svg?branch=main)
![Type Check](https://github.com/sudoDeVinci/devinci.cloud/actions/workflows/typecheck.yml/badge.svg?branch=main)

# Devinci.cloud
![Current Visual](/public/images/screenshot.png)

This is the server and database component of my personal portfolio website, devinci.cloud. The site is modeled after a Windows 98 desktop, complete with a start menu, taskbar, and desktop icons. The is a minimal Flask server with sqlite as the database.

Styling for the windows components is done using the [98.css](https://jdan.github.io/98.css/) package for consistency. 

The frontend component of the site is a custom window manager bundled using Vite. That's available [here](https://github.com/sudoDeVinci/devinci.cloud-frontend).


## Flask Server

A minimal Flask and SQLite  app providing database and routing functionality.

### Structure
```
.
├── main.py
├── requirements.txt
├── logs/
│   └── db.log
│
├── static/
│   ├── assets/
│   ├── icons/
│   ├── images/
│   └── favicon.ico
│
└── server/ 
    ├── __init__.py
    ├── routes.py
    ├── stubs/
    └── db/
        ├── __init__.py
        ├── entities.py 
        ├── manager.py
        ├── services.py
        └── schema.py
```

## Window Components

Windows are vanilla ES6 modules, and are bundled using Vite. The components are styled using 98.css for consistency. The framework I created for this is designed to be easily extensible, and can be used to create new windows with minimal effort. 

The desktop environment and window are served first, with each window calling the server for its content independently. 

## TODO
- [ ] Add more custom window types
- [ ] Add music window
- [ ] Add project window
- [ ] Add contact window 
- [ ] Add more icons
- [ ] Make clock realtime