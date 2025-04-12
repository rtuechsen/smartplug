
# Instructions

Install Ubuntu 24.04 as virtual machine or WSL.  
Set a user name and a password.  

Configure git:  
Install git using `sudo apt -y install git`.  
`git config --global user.name "YOUR_NAME"`  
`git config --global user.email "YOUR_EMAIL"`  
To store your git password (AS PLAINTEXT - DO NOT USE A PASSWORD YOU ARE USING SOMEWHERE ELSE !!!):  
`git config --global credential.helper store`  
`git config --global user.password YOUR_PASSWORD`  
Note that there are no Quotes around the password in contrast to user name or email.  

Clone this repo using: `git clone https://gitlab.com/proi3/shelly-dirigent.git`  

Enter project folder with `cd shelly-dirigent`.  
Run `bash install.sh` to install the project.  
VSCode should find the python virtual environment automatically ONCE you have opened a python file. For existing terminals VSCode will ask you to reload them.  
Run `bash develop_backend.sh` and `bash develop_frontend.sh` (in separate terminals) to run without deployment.  
When using breakpoints in VSCode, instead of simply opening the browser, go to the debug tab and launch `Frontend Debug (Chrome)`.  
For Debugging React Components in a browser the [React Developer Tools](https://react.dev/learn/react-developer-tools) might be helpful.  
Run `bash deploy.sh` to deploy using nginx. Currently one has to open http://localhost:80 (note the lack of https).  


## WSL

WSL can installed either from the Microsoft Store or via `wsl --install -d Ubuntu-24.04`.  
When installing via command line it can be removed using `wsl --unregister Ubuntu-24.04`.  

When using WSL the machine can be reset instead of reinstalled via Windows Settings > Apps > Installed apps > search for "Ubuntu" > "..." > Advanced options > Reset (only works if installed from the Microsoft Store).  


## Nginx

You can verify the syntax of `nginx.conf` by calling `sudo nginx -t` __AFTER__ deploying the configuration file to its proper location.  


## Backend



## Frontend

Requires the extension `ESLint` for in-code-linting in VSCode.  


