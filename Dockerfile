FROM resin/raspberry-pi-alpine:3.6
RUN apk add --no-cache python3
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt
COPY src /usr/local/src/app
CMD ["python3", "/usr/local/src/app/http_server.py"]
