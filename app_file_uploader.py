
"""
    基于streamlit完成web网页上传服务
    pip install streamlit
    streamlit run f:/AI_study/team/app_file_uploader.py
    当web页面发生变化后，则整个代码会重跑一遍，会丢失数据
"""
import streamlit as st
import time
from knowedge_base import knowledgeBaseService

st.title("知识库更新服务")

uploaded_file = st.file_uploader(
    "请上传文件", 
    type=["txt", "pdf", "docx"],
    accept_multiple_files=False
)

# 使用 session_state 确保 service 对象只创建一次，避免重复初始化
if "service" not in st.session_state:
    st.session_state["service"] = knowledgeBaseService()

if uploaded_file is not None:
    file_name = uploaded_file.name
    file_content = uploaded_file.type
    file_size = uploaded_file.size / 1024
    st.write(f"文件名：{file_name}", f"文件类型：{file_content}", f"文件大小：{file_size:.2f}KB")
    st.success(f"文件上传成功，文件大小：{file_size:.2f}KB")
    
    try:
        # 读取文件内容并解码
        text_content = uploaded_file.read().decode("utf-8")
        
        with st.spinner("文件处理中..."):
            time.sleep(1)
            result = st.session_state["service"].upload_file(text_content, file_name)
            st.write(result)
    except UnicodeDecodeError as e:
        st.error(f"文件解码失败：文件可能不是 UTF-8 编码。错误详情：{str(e)}")
    except Exception as e:
        st.error(f"文件处理失败：{str(e)}")