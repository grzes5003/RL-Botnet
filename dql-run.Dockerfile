FROM tensorflow/tensorflow:latest

EXPOSE 22

RUN echo "root:toor" | chpasswd

RUN apt update && apt install -y openssh-server openssh-client iputils-ping \
    && service ssh start \
    && sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && service ssh restart

ADD machines/basic_IoT /iot
ADD worm/worm_deep_rl_2 /worm
ADD supervisor/resources/results/worm-dql/models/worm-dql-a-03.h5 /worm.h5
RUN pip install -r worm/requirements.txt
ENTRYPOINT ["/bin/sh","-c", "sleep 2; python /iot/main.py & python /worm/agent.py -r -f /worm.h5; sleep infinity"]