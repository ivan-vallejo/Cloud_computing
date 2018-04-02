# Automation of AWS ec2 instance launch and remote configuration of data science toolkit
## Ivan Vallejo Vall, March 2018

This repository contains some Python (2.7.9) code to automate the launch and configuration of AWS ec2 instances. The Python script calls two bash scripts which need to be placed in the same folder.

The by default instance launched is based on the "Amazon Linux 2 LTS Candidate AMI 2017.12.0". Changing it to a Ubuntu-based image may require some minor changes in the code (e.g. replacing 'ec2-user' by 'ubuntu' as the user name for the image).

The script allows for changes in the type of instance (by default: t2.micro), the storage space (by default: 8 GB, the minimum required for the selected image) and security group. 

The Python script requires a number of packages (e.g. boto3 to interact with AWS). The script should prompt an error message if any of the packages are missing and indicate them. You can install them in your machine using pip, conda, etc.

Concerning the setup of the remote machine, the script installs Anaconda, emacs (I find it personally useful) and configures Jupyter notebook with a by default password "open_Internet". Further additions in the programs installed/configured are easy to incorporate by modifying the file 'setup_python.sh'.

You can change the password (strongly recommended) by generating a new one with the corresponding hash code and replacing the hash code in line 15 of 'setup_python.sh'. For some guidance on how to generate a password for Jupyter notebook, see [https://jupyter-notebook.readthedocs.io/en/stable/public_server.html](https://jupyter-notebook.readthedocs.io/en/stable/public_server.html).   

The other bash script ('tunnel_localhost.sh') starts a Jupyter notebook on the instance and connects to it using ssh so that it can be accessed from a local browser. Once that is done, the code you enter in your browser is run in the remote instance. 

The script 'tunnel_localhost.sh' **requires the command 'screen'** to be installed on your shell. It will prompt an error if it is not installed. You can easily add it by using 'apt-get install screen' or 'yum install screen' depending on your linux distribution. 