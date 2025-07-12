
# Instructions

Install Ubuntu 24.04 as virtual machine or WSL.  
Set the username of your Ubunutu device to `default` and set a password for this user.  

Install git using `sudo apt -y install git`.  

Clone this repo using: `git clone https://gitlab.com/proi3/smartplug-dirigent.git`  

Enter project folder with `cd smartplug-dirigent`.  
Run `bash install.sh` to install the project.
During the installation script, you will be asked to enter a password. This password must be set on all smart plugs and stored in a JSON file located at /etc/mosquitto/mosquitto_passwd.json. The file must have the following format:
```{
    "mqtt_username": "mqttuser",
    "mqtt_password": "Password"
}```
VSCode should find the python virtual environment automatically ONCE you have opened a python file. For existing terminals VSCode will ask you to reload them. In terminals outside of vscode use `source backend/django-env/bin/activate` to activate the virtual environment for python before running other scripts. If a script fails with `no module found named django` the cause is often that the virtual environment was not activated. If the error still shows up after activating the virtual environment try running `bash update_dependencies.sh`.  
Run `bash develop_backend.sh` and `bash develop_frontend.sh` (in separate terminals) to run without deployment.  
When using breakpoints in VSCode for the __frontend__, instead of simply opening the browser, go to the debug tab in VSCode (on the left) and launch `Frontend Debug (Chrome)`.  
When using breakpoints in VSCode for the __backend__, instead of running `develop_backend.sh`, go to the debug tab in VSCode (on the left) and launch `Backend Debug (Django ASGI Uvicorn)`.  
For Debugging React Components in a browser the [React Developer Tools](https://react.dev/learn/react-developer-tools) might be helpful.  
Run `bash deploy_production.sh` to deploy using nginx. Currently one has to open [](https://localhost:80).  
The scripts for starting the server in development or production mode can be stopped using `Ctrl+C`. If clients are still connected (i.e. SSE is connected), aborting might not happen immediately.  
In production the webserver is run as systemctl under the name `gunicorn`. If any conflicts occur during debugging, you can check the status using `sudo systemctl status gunicorn` and stop the service using `sudo systemctl stop gunicorn`.


## WSL

WSL can installed either from the Microsoft Store or via `wsl --install -d Ubuntu-24.04`.  
When installing via command line it can be removed using `wsl --unregister Ubuntu-24.04`.  

When using WSL the machine can be reset instead of reinstalled via Windows Settings > Apps > Installed apps > search for "Ubuntu" > "..." > Advanced options > Reset (only works if installed from the Microsoft Store).  


## Nginx

You can verify the syntax of `nginx.conf` by calling `sudo nginx -t` __AFTER__ deploying the configuration file to its proper location.  


## Backend

After adding dependencies to the backend via pip, one has to manually add them to `/backend/requirements.txt` to include them in future installations. The dependency should allow patches (`>=`) but not switch to higher feature versions (`,<`).  
Requires the extension `Black Formatter` for formatting in VSCode.  


## Frontend

Requires the extension `ESLint` for in-code-linting in VSCode.  


## Documentation

After building the documentation using `bash generate_documentation.sh` the docs can be found at:

- backend: [./backend/docs/html/index.html](./backend/docs/html/index.html)
- frontend: [./frontend/docs/documents/high_level_documentation.html](./frontend/docs/documents/high_level_documentation.html)

The API is not documented using html but as an OpenAPI document in YAML format:
- API: [./openapi.yaml](./openapi.yaml)

## Active Directory

You can follow this tutorial to setup your own Active Directory Server: [tutorial](https://activedirectorypro.com/create-active-directory-test-environment/)  
The first lessons inluding lesson 3 are the only ones needed. Afterwards users can be added using the program 'Active Directory Users and Computers'.  
To make the server reachable from other devices in the same network:
- choose bridged adapter in VMs network settings, choose your network driver (e.g. 'Intel ...'), check 'cable connected'
- a Host-only adapter in Virtualbox settings is not needed
- change the IP inside the windows server: access ethernet settings via control panel, change adapter settings, Properties, IPv4, e.g.:
	- IP: 192.168.178.50
	- mask: 255.255.255.0
	- default gateway: 192.168.178.1
	- preferred DNS: 192.168.178.1


