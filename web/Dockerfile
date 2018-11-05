FROM resin/rpi-raspbian:stretch-20181024

ENV INITSYSTEM on
ENV READTHEDOCS True

RUN apt-get update && \
    apt-get install python3 python3-pip libraspberrypi-bin && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

COPY src /usr/local/src/app

CMD ["/usr/local/src/app/start.sh"]
