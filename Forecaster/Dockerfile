FROM python:3.7
MAINTAINER ademory@gatech.edu
USER root
WORKDIR /sample
ADD . /sample
RUN apt update && apt install --no-install-recommends -y python3-dev  gcc build-essential
RUN pip install --trusted-host pypi.python.org -r requirements.txt
EXPOSE 8080
ENTRYPOINT ["python", "sample.py"]
