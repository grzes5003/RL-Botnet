FROM alpine:latest

EXPOSE 22

RUN echo "root:toor" | chpasswd

#  build-base
RUN apk add --no-cache openrc openssh python3 py3-pip \
    && mkdir -p /root/.ssh \
    && chmod 0700 /root/.ssh \
    && ssh-keygen -A \
    && echo -e "PasswordAuthentication yes" >> /etc/ssh/sshd_config \
    && echo -e "PermitRootLogin yes" >> /etc/ssh/sshd_config \
    && mkdir -p /run/openrc \
    && touch /run/openrc/softlevel

ADD machines/honeypot /honeypot


ENTRYPOINT ["/bin/sh","-c","rc-status; rc-service sshd start; sleep 2; ifconfig eth0 10.0.0.25 netmask 255.255.255.0; ifconfig eth1 10.0.0.50 netmask 255.255.255.0; ifconfig eth2 10.0.0.100 netmask 255.255.255.0; python /honeypot/main.py; sleep infinity"]