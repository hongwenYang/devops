import json
import paramiko
import psutil
import subprocess
import socket
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


class ServerInspector:
    def __init__(self, config_file):
        self.configs = self.load_config(config_file)
        self.report_data = []

    def load_config(self, file_path):
        """加载JSON配置文件"""
        with open(file_path, 'r',encoding='utf-8') as f:
            configs = json.load(f)

        # 配置验证和默认值设置
        required_fields = ['instance_id', 'username', 'password']
        for conf in configs:
            for field in required_fields:
                if field not in conf:
                    raise ValueError(f"Missing required field: {field}")

            conf.setdefault('port', conf['public_port'])
            conf.setdefault('protocol', 'ssh')
            conf.setdefault('services', [])

        return configs

    def remote_command(self, conf, command):
        """执行远程命令"""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # 优先使用公网地址
            target_ip = conf.get('public_ip') or conf.get('private_ip')
            client.connect(target_ip,
                           port=conf['port'],
                           username=conf['username'],
                           password=conf['password'],
                           timeout=10)

            stdin, stdout, stderr = client.exec_command(command)
            return stdout.read().decode().strip()
        except Exception as e:
            print(f"Connection failed to {conf['instance_id']}: {str(e)}")
            return None
        finally:
            client.close()

    def check_service(self, conf, service):
        """检查指定服务状态"""
        if conf['protocol'] == 'ssh':
            status = self.remote_command(conf, f"systemctl is-active {service}")
            return status if status else 'inactive'
        # 可扩展其他协议检查
        return 'Unsupported protocol'

    def inspect_server(self, conf):
        """执行单个服务器巡检"""
        server_info = {
            'instance_id': conf['instance_id'],
            'server_ip': conf['public_ip'],
            'inspection_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'engineer': "杨洪文"  # 可从配置中读取
        }

        # CPU使用率（远程）
        cpu_usage = self.remote_command(conf,"top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\$[0-9.]*\$%* id.*/\\1/' | awk '{print 100 - $1}'")
        server_info['cpu_usage'] = f"{float(cpu_usage or 0):.1f}%" if cpu_usage else 'N/A'

        # 内存使用率
        mem_info = self.remote_command(conf, "free -m | awk '/Mem/{printf \"%.1f%%\", $3/$2 * 100}'")
        server_info['memory_usage'] = mem_info or 'N/A'

        # 磁盘使用率
        disk_usage = self.remote_command(conf, "df -h / | awk 'NR==2{print $5}'")
        server_info['disk_usage'] = disk_usage or 'N/A'

        # 服务状态检查
        service_status = {}
        for service in conf.get('services', []):
            status = self.check_service(conf, service)
            service_status[service] = status if status else 'unknown'
        server_info['services'] = json.dumps(service_status, ensure_ascii=False)

        # 安全扫描（示例）
        server_info['security_scan'] = self.remote_command(conf, "sudo lynis audit system --quick") or 'N/A'

        return server_info

    def generate_report(self):
        """生成巡检报告"""
        # 使用线程池并行检查
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = executor.map(self.inspect_server, self.configs)

        self.report_data = [result for result in results if result]

        # 生成Excel报告
        df = pd.DataFrame(self.report_data)
        output_file = f"multi_server_report_{datetime.now().strftime('%Y%m%d')}.xlsx"
        df.to_excel(output_file, index=False)
        print(f"生成巡检报告: {output_file}")


if __name__ == "__main__":
    inspector = ServerInspector('infos.json')
    inspector.generate_report()
