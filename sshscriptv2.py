import paramiko
import time
import getpass
import os
import re
from config_file import host_conf
from paramiko import transport

#UN = raw_input("Username : ")
#UN = input("Username: ")
#PW = getpass.getpass("Password : ")
UN = "username"
PW = "password"

final = dict()
f = open('sshlogfile0001.txt', 'w')
network_devices = open('network_devices', 'r')

for ip in network_devices:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ip = ip.strip()
    try:
        ssh.connect(ip, port=22, username=UN, password=PW,allow_agent=False,look_for_keys=False)
    except:
        print("Can't connect to %s" % str(ip))
        continue
    remote = ssh.invoke_shell()
    remote.send('term len 0\n')
    time.sleep(1)
    #This for loop allows you to specify number of commands  you want to enter
    #Dependent on the output of the commands you may want to tweak sleep time.
    f = open('sshlogfile0001.txt', 'a')
    serial = []
    for command in host_conf:
        remote.send(' %s \n' % command)
        time.sleep(2)
        buf = remote.recv(65000)
        for i in buf.splitlines():
            i = str(i)

            ## SERIAL
            if ( re.search('System serial number  ', i) or re.search('System Serial Number  ', i) or re.search('Processor Board ID', i) or re.search('Processor board ID', i) ) and ( re.split(' ',i)[-1] not in serial ):
                serial.append(re.split(' ',i)[-1])

            ## OS VERSION
            if re.search('RELEASE SOFTWARE', i) and re.search('Software', i):
                version = (re.split('Version', i))[1]
            if re.search('System version: ', i):
                version = (re.split(' ', i))[4]
            
            ## DEVICE NAME
            if re.search(' uptime is ', i) and not re.search('Kernel', i):
                hostname = (re.split(' ', i))[0]
            if  re.search('Device name: ', i):
                hostname = (re.split(' ', i))[4]
            
            ## MODEL NUMBER
            if re.search('Model number ', i) or re.search('Model Number ', i):
                model = (re.split(':', i))[1]
            if re.search('chassis', i):
                model = (re.split(' ',i))[3] + ' ' + (re.split(' ',i))[4]
            if ( re.search('processor with ', i) and re.search('bytes of memory.', i) ):
                model = (re.split(' ',i))[1]
        
        list = "{0};{1};{2};{3};{4}\n".format( ip, str(hostname), serial, str(version), str(model) )
    print(list)
    f.write(list)
    final[ip] = [str(hostname), serial, str(version), str(model)]
    f.close()
    ssh.close()
print("\n#", final)
