FROM resin/raspberry-pi-python:3.6.1-slim
ENV READTHEDOCS=True
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt
COPY src /usr/local/src/app
CMD ["python3", "/usr/local/src/app/http_server.py"]
