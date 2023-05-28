FROM tensorflow/tensorflow:latest

EXPOSE 22

RUN echo "root:toor" | chpasswd

RUN apt update && apt install -y openssh-server openssh-client \
    && mkdir -p /root/.ssh \
    && chmod 0700 /root/.ssh \
    && ssh-keygen -A \
    && echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config \
    && echo "PermitRootLogin yes" >> /etc/ssh/sshd_config \
    && service ssh restart \

ENTRYPOINT ["/bin/sh","-c","sleep infinity"]