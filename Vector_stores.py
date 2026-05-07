
from langchain_chroma import Chroma
import config_data as config


class VectorStoreService(object):  
    def __init__(self, embedding):
        try:
            self.embedding = embedding
            self.vector_store = Chroma(
                collection_name=config.collection_name,
                embedding_function=self.embedding,
                persist_directory=config.persist_directory,
            )
        except Exception as e:
            print(f"初始化向量存储失败：{str(e)}")
            raise
    
    def get_retriever(self):
        try:
            # 返回向量检索器，方便加入 chain 中
            return self.vector_store.as_retriever(
                search_kwargs={"k": config.similarity_threshold},
            )
        except Exception as e:
            print(f"获取检索器失败：{str(e)}")
            raise

if __name__ == "__main__":
    from langchain_community.embeddings import DashScopeEmbeddings

    try:
        embedding = DashScopeEmbeddings(model=config.embedding_model_name)
        service = VectorStoreService(embedding)
        retriever = service.get_retriever()
        result = retriever.invoke("我的身高是 1.8 米，我体重是 70kg，建议尺码是？")
        print(result)
    except Exception as e:
        print(f"测试失败：{str(e)}")