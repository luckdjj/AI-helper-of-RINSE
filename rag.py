
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from Vector_stores import VectorStoreService
from langchain_community.embeddings import DashScopeEmbeddings
import config_data as config
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables import RunnableWithMessageHistory
import file_history_store as get_history

def prompt_print(prompt):
    print("="*20)
    print("prompt:",prompt)
    return prompt

class RagService(object):
    def __init__(self):
        try:
            self.vector_store = VectorStoreService(
                embedding=DashScopeEmbeddings(model=config.embedding_model_name)
            )
            self.prompt_template = ChatPromptTemplate.from_messages([
                ("system", "你是一个专业的尺码建议助手，以我提供的已知参考资料为主，"
                 "简洁和专业的回答用户问题。参考资料：{context}"),
                ("system", "以下是用户对话的历史纪录："),
                MessagesPlaceholder(variable_name="history"),
                ("human", "请回答用户提问：{input}"),
            ])
            self.chat_model = ChatTongyi(model_name=config.chat_model_name)
            self.chain = self._get_chain()
        except Exception as e:
            print(f"RagService 初始化失败：{str(e)}")
            raise

    def _get_chain(self):
        retriever = self.vector_store.get_retriever()
        
        def format_documents(docs: list[Document]):
            if not docs: 
                return "无相关参考资料"
            formatted_str = ""
            for doc in docs:
                formatted_str += f"文段片段：{doc.page_content}\n文档元数据：{doc.metadata}\n\n"
            return formatted_str
        
        def format_for_retriever(value: dict) -> str:
            return value["input"]
        
        def format_for_prompt_template(value: dict) -> dict:
            new_value = {}
            new_value["input"] = value["input"]["input"]
            new_value["context"] = value["context"]
            new_value["history"] = value["input"]["history"]
            return new_value
        
        try:
            chain = (
                {
                    "input": RunnablePassthrough(),
                    "context": RunnableLambda(format_for_retriever) | retriever | format_documents
                } 
                | RunnableLambda(format_for_prompt_template) 
                | self.prompt_template 
                | prompt_print 
                | self.chat_model 
                | StrOutputParser()
            )
            
            conversation_chain = RunnableWithMessageHistory(
                chain,
                get_history.get_history,
                input_messages_key="input",
                history_messages_key="history",
            )
            return conversation_chain
        except Exception as e:
            print(f"构建 chain 失败：{str(e)}")
            raise

# if __name__ == "__main__":
#     try:
#         # 使用配置文件中的 session_config，避免硬编码
#         res = RagService().chain.invoke(
#             {"input": "请给出一个体重 70kg 的尺寸建议"},
#             config.session_config
#         )
#         print(res)
#     except Exception as e:
#         print(f"调用失败：{str(e)}")