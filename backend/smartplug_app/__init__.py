## \mainpage
##
## # High level documentation
##
## This document contains the high level documentation for the general project as well as the backend.
## The frontend has a separate high level documenation under [./frontend/docs/documents/high_level_documentation.html](../../../frontend/docs/documents/high_level_documentation.html).
## For instructions on how to setup the project for development take a look at [README.md](../../../README.md).
##
## ## General
##
## The goal of this software is to allow a number of deployed smartplugs to be controlled remotely via a web interface.
## The system expects an Active Directory to be present for authenticating users.
##
## ### Architecture
##
## The system is delivered as an ubuntu system with a web server and a mosquitto server installed. The web server serves both frontend and backend.
## Once the system is properly setup and configured, a user can open the configured address of the frontend in a web browser.
## Interactions with the frontend will trigger requests to the backend, like switching a smartplug on.
## The backend itself contains the main logic of the system. It reaches out to other components, e.g. to the Active Directory to authenticate users or to the mosquitto server to communicate with the smartplugs.
##
## ### Files and places
##
## The projects files used for development are located in a folder `smartplug-dirigent` in the ubuntu systems user folder. This folder is managed via git for development.
## Inside this folder there are two main folders, one for the backend and one for the frontend. Additionally a `.vscode` folder is present to unify vscode editor settings for developers working on this project.
## There are also different files present at the root of the project:
## - README.md: contains instructions on how to setup the project for development after cloning from a git repository.
## - LICENSE.txt: the license used for this project
## - a number of configuration files:
##   - config.json: describes the smartplugs present in the network and the groups displayed in the UI
##   - mosquitto.conf: configurations for the mosquitto server
##   - nginx.conf: configuration for the nginx web server
##   - openapi.yaml: documents the REST API of the backend
##   - smartplug_app: configuration file for the logrotate tool on ubuntu
## - a number of scripts:
##   - deploy_production.sh: the script used to start the system for production
##   - develop_backend.sh / develeop_frontend.sh: the scripts to start the backend / frontend for development
##   - format.sh: used for formatting (parts of) the project
##   - install.sh: used to install the project with the necessary dependencies
##   - update_dependencies.sh: used to update the dependencies without installing the whole project again
##   - generate_documentation.sh: used to generate the HTML documentation for the backend and frontend
##
## ## Backend
##
## Please note: due to bugs in doxygen some variables like instance variables with type hints do not show up in the generated docs. This might be fixed in recent versions of doxygen, but those are not distributed to linux yet.
## Also type hints that start with a namespace are not picked up correctly, e.g. `my_var: namepsace.my_type = 1` might be picked up as being of type `namespace`.
##
## ### Architecture
##
## While Django is intended as a full-stack framework, combining frontend and backend, we are using it as a pure REST framework.
## It responds to requests from the frontend and communicates with the Active Directory and the smartplugs (via the mosquitto server).
## The REST API is defined in `urls.py` and `views.py` as expected by Django. The incoming requests are then forwarded to the RequestManager.
## The RequestManager then calls the necessary components of the backend to fulfil the request. This can be the SessionManager to decide if a user has the necessary permissions to perform the request.
## Or this can be the SmartplugApp (used nearly all other tasks).
## The SmartplugApp holds the device tree, which is a representation of the structure and the state of the smartplugs.
## It can receive updates from the MQTTClient if the state of devices change and can itself call MQTTClient to switch smartplugs on or off.
## For authentication Djangos build-in mechanisms are used. This requires defining a AuthenticationBackend to validate given credentials. The SessionManager can then use this funcionality.
##
## In development the django development server is used, for production a combination of nginx with gunicorn is used.
##
## ### Files and places
##
## The backend folder contains the the folder smartplug_app, which holds most of the source code. It also contains a `Doxyfile` used as configuration for the doxygen generator, a `manage.py` required by Django and `requirements.txt` which holds the python dependencies for the backend used by pip.
## Inside the folder `smartplug_app` there is another folder `settings`. This is the place expected by Django to define all Django-related settings. It is split in a `settings_base.py` which holds the settings used both in production and development, as well as dedicated files for both production and development.
## The rest of the files in `smartplug_app` are the python source files for the backend as well a database. Django stores implementation related information here as well as e.g. information about users. This project only actively uses the database in connection with Djangos build-in user management.
## The file `admin_settings.py` is intended for settings an admin might want to tweak without touching the overall implementation.
##
## When running the script `deploy_production.sh` various files of this project are copied to the required places, e.g. to folders known to nginx or to locations used by the ubuntu system.
##
## ### Additional notes
##
## Some identifiers do not conform to the snake case naming convention, e.g. `deviceId`. This is because those names are used consistently across the project, also the frontend. So identifiers with the same meaning at different places of the project will be written exactly the same way.
##
## When using doxygen with python some things are worth to mention:
## - Instance attributes need to use a different syntax using `##` than the ususal python docstring in order to show up in the generated documentation. This means that the linters of IDEs do not recognize these docstrings.
## - A `\` symbol is needed after a period in those docstrings if more than one sentence is used.
## - Everything after the first period in a module docstring will not show up in the documentation.
