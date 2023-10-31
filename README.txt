DESCRIPTION
-- Describe the package in a few paragraphs
The application is fully hosted in AWS and can be ascessed at the following address: http://44.203.89.214, without any additional installation. The individual packages required are listed in requirements.txt and the information for the file used by the docker is in Dockerfile. However, these files are mentioned because they can be used to continue work on the underlying code, and are not necessary if you only wish to use the application.

INSTALLATION
--How to install and setup your code
Nothing needs to be installed to access the application. The application files were containerized using Docker, where the container contains all the packages needed to be downloaded for the application to run properly. Then, the container was imported to a free-tier EC2 instance on AWS, which hosts our application, so it can be accessible publicly.

If users prefer to access the application locally, they will need to install python (at least 3.7) along with all the packages listed in the requirements.txt file located in the CODE folder. To ease the process, we recommend using Anaconda as it assists in installing all the required packages along with their dependencies. To do that, open Anaconda Navigator, click on the Environment tab and install all the packages listed in the requirements.txt file. 

EXECUTION
-- How to run a demo on your code
To access the public site, open up a browser and type in the address http://44.203.89.214

To access it locally, open the terminal, browse to the CODE folder, and run the sample.py python script. If packages were installed using Anaconda, open Anaconda Navigator and open the terminal with your current environment. On the terminal, browse to the CODE folder and run the sample.py python script.
