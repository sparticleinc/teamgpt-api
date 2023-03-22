FROM python:3.10-slim-buster

LABEL maintainer="leo.chen@sparticle.com"

ENV TZ=Asia/Tokyo
ENV DEBUG=0

RUN apt-get update && \
    apt-get -y install gcc libpq-dev tzdata

COPY . /backend
WORKDIR /backend

# Use system pip
RUN pip install  --isolated  -r requirements.txt

EXPOSE 8000

RUN chmod +x ./startup.sh
CMD ["/bin/sh", "-c", "./startup.sh"]