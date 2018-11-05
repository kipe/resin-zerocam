FROM resin/rpi-raspbian:stretch-20181024

RUN apt-get update && \
    apt-get install libraspberrypi-bin wget

RUN wget -O /tmp/motion.deb https://github.com/Motion-Project/motion/releases/download/release-4.2/pi_stretch_motion_4.2-1_armhf.deb && \
    dpkg -i /tmp/motion.deb ; \
    apt-get -fy install && \
    rm /tmp/motion.deb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY /etc /etc

CMD ["sleep", "99999999"]
