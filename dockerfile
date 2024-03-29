
FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y sagemath
RUN pip3 install pandas

WORKDIR /media
CMD ./dockerrun
