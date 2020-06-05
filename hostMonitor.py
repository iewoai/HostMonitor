import os
import sys
import re
import logging
import paramiko
import time
logging.basicConfig(
    filename='log/hostUse_{}.log'.format(time.strftime('%Y-%m-%d', time.localtime(time.time()))),
    format='%(message)s',
    filemode='w',
    level=logging.INFO
)

class SSHClient():
    def __init__(self, hostname, port, username, pkey):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.pkey = paramiko.RSAKey.from_private_key_file(pkey)
        self.ssh = ''

    def connect(self):
        self.transport = paramiko.Transport((self.hostname, self.port))
        self.transport.connect(username=self.username, pkey=self.pkey)

    def command(self, cmd):
        try:
            stdin,stdout,stderr = self.ssh.exec_command(cmd)
            readlines = stdout.readlines()
            return ''.join(readlines)
        except Exception as err:
            print(err)
            return err

    def put(self, local_path, remote_path):
        try:
            sftp = paramiko.SFTPClient.from_transport(self.transport)
            sftp.put(local_path, remote_path)
        except Exception as err:
            print(err)

    def close(self):
        self.transport.close()

    # 获得内存占用
    def get_Ram_Use(self):
        str_out = self.command('cat /proc/meminfo')
        str_total = re.search(r'MemTotal:.*?\n', str_out).group()
        totalmem = re.search(r'\d+',str_total).group()
        str_free = re.search(r'MemFree:.*?\n', str_out).group()
        freemem = re.search(r'\d+',str_free).group()
        use = round(float(freemem)/float(totalmem), 2)
        logging.info('      当前内存使用率为：%s'%str(use) + '%')

    # 获得cpu占用，CPU利用率= 1-(CPU空闲时间2 - CPU空闲时间1) / (CPU总时间2 - CPU总时间1)
    def get_CPU_Use(self):
        str_out = self.command('cat /proc/stat | grep "cpu "')
        cpu_time_list = re.findall(r'\d+', str_out)
        cpu_idle1 = cpu_time_list[3]
        total_cpu_time1 = 0
        for t in cpu_time_list:
            total_cpu_time1 = total_cpu_time1 + int(t)
        time.sleep(2)
        str_out = self.command('cat /proc/stat | grep "cpu "')
        cpu_time_list = re.findall(r'\d+', str_out)
        cpu_idle2 = cpu_time_list[3]
        total_cpu_time2 = 0
        for t in cpu_time_list:
            total_cpu_time2 = total_cpu_time2 + int(t)
        cpu_usage = round(1 - (float(cpu_idle2) - float(cpu_idle1)) / (total_cpu_time2 - total_cpu_time1), 2)
        logging.info('      当前CPU使用率为：%s'%str(cpu_usage) + '%')

    # 获得磁盘占用
    def get_Disk_Use(self):
        str_out = self.command('df -m')
        disk_list = str_out.split('\n')
        all_disk = 0
        all_disk_used = 0
        for disk in disk_list[1:]:
            disk_split = disk.split()
            if len(disk_split) > 1:
                # print(disk.split()[1], disk.split()[2])
                all_disk += float(disk.split()[1])
                all_disk_used += float(disk.split()[2])
        disk_usage = round(all_disk_used/all_disk ,2)
        logging.info('      当前磁盘占用率为：%s'%disk_usage + '%')

    def get_Use(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=self.hostname, port=self.port, username=self.username, pkey=self.pkey)
        logging.info('##### 服务器：%s'%self.hostname)
        self.get_Ram_Use()
        self.get_CPU_Use()
        self.get_Disk_Use()

if __name__ == '__main__':
    ip_list = [
    '47.244.202.68',
    '47.52.31.22',
    '47.244.5.195',
    '47.244.45.179',
    '47.244.133.17',
    '47.240.226.198',
    '47.56.222.172',
    '47.56.241.135',
    '47.57.28.64',
    '47.75.4.100',
    '47.56.199.24',
    '47.52.20.36',
    '47.52.99.123',
    '47.244.144.197',
    '47.56.193.71',
    '47.56.91.103',
    '47.52.227.14',
    '47.52.253.226',
    '47.56.205.186',
    '47.90.50.213',
    '47.57.21.145',
    '47.57.24.93',
    '47.57.24.74',
    '47.56.219.93',
    '47.57.22.8',
    '47.57.20.26',
    '47.244.38.203',
    '47.57.24.157',
    '47.57.24.191',
    '47.89.13.160'
    ]
    logging.info('\n\n###########检测开始时间{}，本次检测共有{}个服务器##########'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), len(ip_list)))
    for ip in ip_list:
        logging.info('#########################{}####################'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
        client = SSHClient(hostname=ip, port=22, username='root', pkey='id_rsa')
        client.get_Use()

