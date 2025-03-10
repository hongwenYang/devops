import requests
import datetime
import json
import hmac
import hashlib
import base64


def generate_signature(secret, string_to_sign):
    """
    生成 HMAC-SHA256 签名
    :param secret: 密钥
    :param string_to_sign: 待签名的字符串
    :return: 签名后的字符串
    """
    h = hmac.new(secret.encode('utf-8'), string_to_sign.encode('utf-8'), hashlib.sha256)
    return base64.b64encode(h.digest()).decode('utf-8')


def get_auth_header(key_id, secret, method, path, headers):
    """
    生成签名认证头部
    :param key_id: 访问密钥 ID
    :param secret: 访问密钥
    :param method: 请求方法
    :param path: 请求路径
    :param headers: 请求头部
    :return: 包含签名的认证头部
    """
    # 定义需要签名的头部
    signature_headers = ['(request-target)', 'accept', 'date']
    # 构建待签名的字符串
    request_target = f"{method.lower()} {path}"
    string_to_sign = f"(request-target): {request_target}\n"
    for header in signature_headers[1:]:
        string_to_sign += f"{header}: {headers[header]}\n"
    string_to_sign = string_to_sign.rstrip()
    # 生成签名
    signature = generate_signature(secret, string_to_sign)
    # 构建认证头部
    auth_header = f'Signature keyId="{key_id}",algorithm="hmac-sha256",headers="{" ".join(signature_headers)}",signature="{signature}"'
    return auth_header


def get_user_info(jms_url, key_id, secret):
    """
    获取用户信息
    :param jms_url: Jumpserver 的 URL
    :param key_id: 访问密钥 ID
    :param secret: 访问密钥
    """
    url = jms_url + '/api/v1/assets/hosts/'
    path = url.replace(jms_url, '')
    gmt_form = '%a, %d %b %Y %H:%M:%S GMT'
    headers = {
        'accept': 'application/json',
        'X-JMS-ORG': '00000000-0000-0000-0000-000000000002',
        'date': datetime.datetime.utcnow().strftime(gmt_form),
        'Content-Type': 'application/json'
    }
    # 生成认证头部
    auth_header = get_auth_header(key_id, secret, 'POST', path, headers)
    headers['Authorization'] = auth_header
    asset_data = {
        "name": "Test Asset4",  # 资产名称
        "address": "192.168.1.122",  # 资产 IP 或主机名
        'platform': {
            'id': 33,
            'name': '文件传输'
        },
        'protocols': [{'name': 'ssh', 'port': 21469}, {'name': 'sftp', 'port': 21469}],
        'nodes': [{'id': '5ec8b715-457c-4601-ba53-c42274dcf68c', 'name': 'Default'}],
        "username": "root",  # 登录用户名
        "password": "$!j2VIbMXZpYKNXCBm7i",  # 登录密码
        "description": "这是一个测试资产",  # 资产描述
        "tags": [""],  # 资产标签（可选）
    }
    # 发送请求
    response = requests.post(url, headers=headers, verify=False, data=json.dumps(asset_data))
    try:
        if response.status_code == 201:
            print(asset_data['address'] + '创建成功')
    except json.JSONDecodeError:
        print(f"Failed to decode JSON response: {response.text}")


if __name__ == '__main__':
    jms_url = 'http://192.168.8.211'
    KeyID = 'e3b7d25a-4be9-401a-959a-b643bc83b1f3'
    SecretID = 'f1Ow2WvcimoaR7FQYoDuB2ieag0WAZT2ASq9'
    get_user_info(jms_url, KeyID, SecretID)
