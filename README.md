
Install Ubuntu 24.04 as virtual machine or WSL.  
Set a user name and a password.  

Configure git:  
`git config --global user.name "YOUR_NAME"`  
`git config --global user.email "YOUR_EMAIL"`  
To store your git password (AS PLAINTEXT):  
`git config --global credential.helper store`  
`git config --global user.password YOUR_PASSWORD`  
Note that there are no Quotes around the password in contrast to user name or email.  

Clone this repo using `git clone `.  

Run `sudo bash install.sh` to install the project.  
Run `sudo bash develop.sh` to run without deployment.  
Run `sudo bash deploy.sh` to deploy using nginx.  

## Backend



## Frontend

Requires the extension `ESLint` for in-code-linting in VSCode.  


