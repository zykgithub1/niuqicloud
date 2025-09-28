import os
import requests
from dotenv import load_dotenv

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from sentence_transformers import SentenceTransformer

from realtime_ai_character.logger import get_logger


load_dotenv()
logger = get_logger(__name__)


class SiliconFlowBGEEmbeddings:
    def __init__(self, api_key, model_name="BAAI/bge-large-zh-v1.5"):
        self.api_key = api_key
        self.model_name = model_name
        self.url = "https://api.siliconflow.cn/v1/embeddings"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def embed_documents(self, texts):
        """批量嵌入文档"""
        embeddings = []
        for text in texts:
            embedding = self._get_embedding(text)
            embeddings.append(embedding)
        return embeddings
    
    def embed_query(self, text):
        """嵌入单个查询"""
        return self._get_embedding(text)
    
    def _get_embedding(self, text):
        """获取单个文本的嵌入向量"""
        payload = {
            "model": self.model_name,
            "input": text
        }
        
        try:
            response = requests.post(self.url, json=payload, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            return result['data'][0]['embedding']
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            raise

class LocalBGEEmbeddings:
    def __init__(self, model_name="BAAI/bge-large-zh-v1.5"):
        self.model = SentenceTransformer(model_name)
    
    def embed_documents(self, texts):
        return self.model.encode(texts).tolist()
    
    def embed_query(self, text):
        return self.model.encode([text])[0].tolist()

def get_chroma(embedding: bool = True):
    if embedding:
        embedding_type = os.getenv("EMBEDDING_TYPE", "siliconflow_bge")
        
        if embedding_type == "siliconflow_bge":
            # 使用硅基流动的 BGE API
            siliconflow_api_key = os.getenv("SILICONFLOW_API_KEY")
            if not siliconflow_api_key:
                raise Exception("SILICONFLOW_API_KEY is required for SiliconFlow BGE embeddings")
            logger.info("Using SiliconFlow BGE embeddings")
            embedding_function = SiliconFlowBGEEmbeddings(siliconflow_api_key)
        elif embedding_type == "local_bge":
            # 使用本地 BGE 模型
            logger.info("Using local BGE embeddings")
            embedding_function = LocalBGEEmbeddings()
        else:
            # 使用 OpenAI 嵌入
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise Exception("OPENAI_API_KEY is required to generate embeddings")
            if os.getenv("OPENAI_API_TYPE") == "azure":
                embedding_function = OpenAIEmbeddings(
                    openai_api_key=openai_api_key,
                    deployment=os.getenv(
                        "OPENAI_API_EMBEDDING_DEPLOYMENT_NAME", "text-embedding-ada-002"
                    ),
                    chunk_size=1,
                )
            else:
                embedding_function = OpenAIEmbeddings(openai_api_key=openai_api_key)
    else:
        embedding_function = None

    chroma = Chroma(
        collection_name="llm",
        embedding_function=embedding_function,
        persist_directory="./chroma.db",
    )
    return chroma
