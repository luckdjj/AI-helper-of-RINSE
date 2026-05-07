#知识库
import os
import config_data as config
import hashlib
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime
def check_md5(md5_str: str):
    #检查文件的md5值是否一致
    if not os.path.exists(config.md5_file):
        #if进入表示文件不存在，返回False
        open(config.md5_file, 'w',encoding='utf-8').close()
        return False#返回False，表示文件不存在
    else:
        for line in open(config.md5_file, 'r', encoding='utf-8'):
            line = line.strip()
            if line == md5_str:
                return True
        return False
        
def save_md5(md5_str: str):
    #保存文件的md5值
    with open(config.md5_file, 'a', encoding='utf-8') as f:
        f.write(md5_str)
    #保存文件的md5值
    pass

def get_string_md5(input_str: str,encoding='utf-8'):
    #将传入字符串转换为md5字符串
    str_md5 = input_str.encode(encoding=encoding)
    md5_obj = hashlib.md5()
    md5_obj.update(str_md5)
    md5hex = md5_obj.hexdigest()
    return md5hex
    
    
    
class knowledgeBaseService():
    def __init__(self):
        os.makedirs(config.persist_directory, exist_ok=True)    
        
        self.chroma = Chroma(
            collection_name=config.collection_name,
            embedding_function=DashScopeEmbeddings(model=config.embedding_model_name),
            persist_directory=config.persist_directory
        )
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=config.separators,
            length_function=len
        )

    def upload_file(self, data, filename ):
        # 将传入的字符串，进行向量化，存入向量数据库中
        #先得到传入字符串中的md5值
        md5hex = get_string_md5(data)
        if check_md5(md5hex):
            return "文件已存在"
        if len(data)>config.max_split_char_number:
            knowledge_chunks = self.spliter.split_text(data)
        else:
            knowledge_chunks = [data]
        metadata = {"filename": filename,
                    "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "operator": "djj"
                    }
        #将知识库中的文本和元数据添加到向量数据库中
        self.chroma.add_texts(
            knowledge_chunks,
            metadatas=[metadata for _ in knowledge_chunks],
        )
        save_md5(md5hex)

        return "文件上传成功"
