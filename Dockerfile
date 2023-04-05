FROM alpine:latest AS base

EXPOSE 22

RUN echo "root:toor" | chpasswd

#  build-base
RUN apk add --no-cache openrc openssh python3 musl-dev libc-dev \
    gcc py3-pip python3-dev linux-headers nmap nmap-scripts \
    && mkdir -p /root/.ssh \
    && chmod 0700 /root/.ssh \
    && ssh-keygen -A \
    && echo -e "PasswordAuthentication yes" >> /etc/ssh/sshd_config \
    && echo -e "PermitRootLogin yes" >> /etc/ssh/sshd_config \
    && mkdir -p /run/openrc \
    && touch /run/openrc/softlevel

ADD machines/basic_IoT /iot

FROM base AS image-infected
ADD worm /worm
RUN pip install -r worm/requirements.txt
ENTRYPOINT ["/bin/sh","-c","rc-status; rc-service sshd start; sleep 10; python /worm/script.py; sleep infinity"]


FROM base AS image-clean
ENTRYPOINT ["/bin/sh","-c","rc-status; rc-service sshd start; sleep 2; python /iot/main.py; sleep infinity"]