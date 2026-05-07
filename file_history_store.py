import os, json
import re
from typing import Sequence
from pathlib import Path

from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import message_to_dict, messages_from_dict, BaseMessage
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory


def _validate_session_id(session_id: str) -> bool:
    """验证 session_id 是否合法，防止路径遍历攻击和特殊字符问题"""
    if not session_id or not isinstance(session_id, str):
        return False
    # 只允许字母、数字、下划线、短横线
    if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
        return False
    # 防止路径遍历
    if '..' in session_id or '/' in session_id or '\\' in session_id:
        return False
    return True


def get_history(session_id):
    return FileChatMessageHistory(session_id, "./chat_history")


class FileChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id, storage_path):
        # 验证 session_id 合法性
        if not _validate_session_id(session_id):
            raise ValueError(f"无效的 session_id: {session_id}")
        
        self.session_id = session_id
        self.storage_path = storage_path
        
        # 使用 Path 对象安全地构建文件路径
        storage_path_obj = Path(storage_path).resolve()
        self.file_path = str(storage_path_obj / session_id)

        # 确保文件夹是存在的
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        try:
            all_messages = list(self.messages)
            all_messages.extend(messages)

            new_messages = [message_to_dict(message) for message in all_messages]
            
            # 写入时先写临时文件再重命名，减少并发冲突风险
            temp_file = self.file_path + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(new_messages, f, ensure_ascii=False)
            
            # 原子操作替换文件
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
            os.rename(temp_file, self.file_path)
        except Exception as e:
            print(f"保存消息失败：{str(e)}")
            if os.path.exists(temp_file):
                os.remove(temp_file)
            raise

    @property       # @property装饰器将messages方法变成成员属性用
    def messages(self) -> list[BaseMessage]:
        try:
            if not os.path.exists(self.file_path):
                return []
            with open(self.file_path, "r", encoding="utf-8") as f:
                messages_data = json.load(f)
                return messages_from_dict(messages_data)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError as e:
            print(f"读取历史消息 JSON 解析失败：{str(e)}")
            return []
        except Exception as e:
            print(f"读取历史消息失败：{str(e)}")
            return []

    def clear(self) -> None:
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False)
        except Exception as e:
            print(f"清空历史记录失败：{str(e)}")
            raise



