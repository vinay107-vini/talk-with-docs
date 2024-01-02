FROM ubuntu:20.04

WORKDIR /explore_docs
COPY ./requirements.txt /explore_docs/requirements.txt
RUN apt-get update && \
    apt-get install -y python3.8 python3-pip python3.8-dev build-essential
RUN python3.8 -m pip install -U pip
RUN pip install -r /explore_docs/requirements.txt \
    && rm -rf /root/.cache/pip
RUN apt-get install -y antiword
COPY . /explore_docs




