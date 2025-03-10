from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

# 连接到源和目标ES集群，需要账号密码认证
source_es = Elasticsearch(
    "http://es-cn-7mz2ujwmf001h3x54.public.elasticsearch.aliyuncs.com:9200",
    http_auth=("elastic", "u*VfKe!dWySuLh!L2^gTV0zw")
)

target_es = Elasticsearch(
    "http://120.26.112.81:9200",
    http_auth=("elastic", "jc123456")
)


def get_mapping(index_name):
    """获取源ES索引的mapping"""
    try:
        mapping = source_es.indices.get_mapping(index=index_name)
        return mapping
    except NotFoundError:
        print(f"Index {index_name} not found in source ES.")
        return None


def create_index_with_mapping(index_name, mapping):
    """在目标ES中创建新索引并应用mapping"""
    if mapping:
        # settings = mapping[index_name + '-bak']
        settings = mapping[index_name]
        print(f"Creating index {index_name} with settings: {settings}")
        try:
            if not target_es.indices.exists(index=index_name):
                target_es.indices.create(index=index_name, body=settings)
                print(f"Index {index_name} created successfully.")
            else:
                print(f"Index {index_name} already exists in target ES.")
        except Exception as e:
            print(f"Error creating index: {e}")
    else:
        print("No mapping found to create the index.")


def sync_es_index(source_index, target_index):
    """同步源ES索引到目标ES"""
    mapping = get_mapping(source_index)
    create_index_with_mapping(target_index, mapping)


def remove_bak_suffix(index_name):
    """去掉'-bak'后缀"""
    if index_name.endswith('-bak'):
        return index_name[:-4]
    return index_name


if __name__ == "__main__":
    # 索引列表，源索引带 '-bak' 后缀
    index_list = [
        'jc_user'
    ]

    # 遍历索引列表，逐个同步
    for index in index_list:
        # 使用带 '-bak' 后缀的源索引，去掉 '-bak' 后缀作为目标索引
        target_index_name = remove_bak_suffix(index)
        sync_es_index(index, target_index_name)
