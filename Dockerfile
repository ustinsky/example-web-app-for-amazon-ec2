FROM amazonlinux

RUN yum update -y && \
    yum install -y python3-pip python3-dev

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

## The wait tool to force Compose to wait for launching DB first and only then the app
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait


CMD /wait && python3 app.py