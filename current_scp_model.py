from io import StringIO
import warnings
from paramiko import AutoAddPolicy, RSAKey, SSHClient
warnings.filterwarnings("ignore")

import requests
import tempfile
import os
import json
import subprocess
from pathlib import Path
import argparse
from rich.console import Console
from scp import SCPClient, SCPException


console = Console()
args = None
 

def get_home_directory():
    return str(Path.home())

home_dir = get_home_directory() + "/"


def printer(msg, fail=False):
    if not args:
        disable_color = True
    else:
        disable_color = False
    if not disable_color:
        if not fail:
            console.print(msg, style = "green")
        else:
            console.print(msg, style = "red")
    else:
        print(msg)

def get_ssh_client(ip_address,ssh_port,username,ssh_key_path,passphrase,timeout=10):
    try:
        ssh_client = SSHClient()
        ssh_client.set_missing_host_key_policy(AutoAddPolicy())

        ssh_client.connect(
            hostname=ip_address,
            username=username,
            pkey=RSAKey.from_private_key_file(ssh_key_path,password=passphrase),
            port=ssh_port,
            passphrase=passphrase,
            look_for_keys=False,
            timeout=timeout
        )

        printer("SSH Connection Established",False)
        return ssh_client
    except Exception as ex:
        printer("SSH Connection Failed",True)
        printer(str(ex),True)
        return None

def scp_get_data(ssh_client, remote_path, local_path, recursive=False, timeout=1):
    try:
        scp_client = SCPClient(ssh_client.get_transport(), socket_timeout=timeout)
        scp_client.get(remote_path, local_path, recursive)
        printer("Files downloaded from remote path {} to local path {}".format(remote_path, local_path),False)
        return True
    except SCPException as ex:
        printer("Failed to download files from remote path {} to local path {}".format(remote_path, local_path),True)
        return False

    finally:
        if scp_client:
            scp_client.close()

if __name__ == "__main__":

    global SSH_KEY_PATH
    global USERNAME
    global PASSPHRASE
    global IP_ADDRESS
    global PORT
    global REMOTE_PATH
    global LOCAL_PATH

    parser = argparse.ArgumentParser(description='Current SCP Model')
    parser.add_argument('-d','--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('-v', '--verbose', help='Verbose output', action='store_true',default=True)
    parser.add_argument("-ssh_key_path", help="SSH Key Path", default=False,action="store",required=True)
    parser.add_argument("-username", help="Username", default=False,action="store",required=True)
    parser.add_argument("-passphrase", help="Passphrase", default=False,action="store",required=False)
    parser.add_argument("-ip_address", help="IP Address", default=False,action="store",required=True)
    parser.add_argument("-port", help="Port", default=False,action="store",required=True)
    parser.add_argument("-remote_path", help="Remote Path", default=False,action="store",required=True)
    parser.add_argument("-local_path", help="Local Path", default=False,action="store",required=True)


    args = parser.parse_args()

    SSH_KEY_PATH = args.ssh_key_path
    USERNAME = args.username
    PASSPHRASE = args.passphrase
    IP_ADDRESS = args.ip_address
    PORT = args.port
    REMOTE_PATH = args.remote_path
    LOCAL_PATH = args.local_path
    

    ssh_client = get_ssh_client(IP_ADDRESS,PORT,USERNAME,SSH_KEY_PATH,PASSPHRASE)
    if ssh_client:
        sucess = scp_get_data(ssh_client,REMOTE_PATH,LOCAL_PATH,recursive=True,timeout=1)
        print("----------------------------------------")
    else:
        sucess = False
        print("----------------------------------------")
    if sucess :
        printer(msg="Task Completed",fail=False)
        print("----------------------------------------")
    else:
        printer("Task failed",True)
        print("----------------------------------------")
        
