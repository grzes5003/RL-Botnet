import platform
import re
import docker
from docker import DockerClient

from supervisor import signals
from supervisor.vectors import Vecs

client = docker.from_env()

machine_name = 'worm-docker-m1-1' if platform.system() != 'Windows' else 'mgr-m1-1'
proc_name = 'python /worm/agent.py'


def get_container(clinet: DockerClient = docker.from_env(), name: str = machine_name):
    containers = [cont for cont in clinet.containers.list() if cont.name == name]
    match containers:
        case [container]:
            return container
        case _:
            raise ConnectionError("Cannot find container")


def tape(cont, is_ubuntu: bool = False) -> str:
    output = cont.exec_run(cmd='ps aux').output.decode('utf-8')
    lines = [line for line in output.splitlines() if proc_name in line and 'sleep' not in line]
    print(lines)
    match lines:
        case [line]:
            if is_ubuntu:
                return line.strip().split()[1]
            return line.strip().split()[0]
        case other:
            raise ConnectionError(f"cannot find pid in {other}")


def send_sig(cont, pid, sig: signals.Signals):
    print(f"send {sig} to {pid} '{sig.cmd(pid)}'")
    cont.exec_run(cmd=sig.cmd(pid))


if __name__ == '__main__':
    cont = get_container(client)
    stats = cont.stats(stream=True, decode=True)
    print(stats)
    c = Vecs.from_read(stats)
    ...
