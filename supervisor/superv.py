import docker
from docker import DockerClient

from supervisor import signals
from supervisor.vectors import Vecs

client = docker.from_env()

machine_name = 'mgr-m1-1'
proc_name = 'python'


def get_container(clinet: DockerClient = docker.from_env(), name: str = 'worm-docker-m1-1'):
    containers = [cont for cont in clinet.containers.list() if cont.name == name]
    match containers:
        case [container]:
            return container
        case _:
            raise "Cannot find container"


def tape(cont) -> str:
    pids = [proc for proc in cont.top() if proc_name in proc[-1]]
    match pids:
        case [pid]:
            return pid
        case other:
            raise f"cannot find pid in {other}"


def send_sig(cont, pid, sig: signals.Signals):
    cont.exec_run(cmd=sig.cmd(pid))


if __name__ == '__main__':
    cont = get_container(client)
    stats = cont.stats(stream=True, decode=True)
    print(stats)
    c = Vecs.from_read(stats)
    ...
