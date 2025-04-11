
# Instructions

Install Ubuntu 24.04 as virtual machine or WSL.  
Set a user name and a password.  

Configure git:  
`git config --global user.name "YOUR_NAME"`  
`git config --global user.email "YOUR_EMAIL"`  
To store your git password (AS PLAINTEXT):  
`git config --global credential.helper store`  
`git config --global user.password YOUR_PASSWORD`  
Note that there are no Quotes around the password in contrast to user name or email.  

Clone this repo using: `git clone https://gitlab.com/proi3/shelly-dirigent.git`  

Enter project folder with `cd shelly-dirigent`.  
Run `bash install.sh` to install the project.  
Run `bash develop_backend.sh` and `bash develop_frontend.sh` (in separate terminals) to run without deployment. Then go to the debug tab in VSCode and launch `Frontend Debug (Chrome)` (instead of simply opening the browser).  
Run `bash deploy.sh` to deploy using nginx. Currently one has to open http://localhost:80 (note the lack of https).  


## WSL

WSL can installed either from the Microsoft Store or via `wsl --install -d Ubuntu-24.04`.  

When using WSL the machine can be reset instead of reinstalled via Windows Settings > Apps > Installed apps > search for "Ubuntu" > "..." > Advanced options > Reset (only works if installed from the Microsoft Store).  


## Nginx

You can verify the syntax of `nginx.conf` by calling `sudo nginx -t` __AFTER__ deploying the configuration file to its proper location.  


## Backend



## Frontend

Requires the extension `ESLint` for in-code-linting in VSCode.  


