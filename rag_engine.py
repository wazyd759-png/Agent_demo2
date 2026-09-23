from __future__ import annotations

import os
import shutil
from typing import Any, Dict, List, Optional

from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.llms import Tongyi
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import CrossEncoder

PROMPT = """你是一个专业的问答助手。请根据以下提供的上下文信息，回答用户的问题。
如果上下文不包含答案，请如实告知。

上下文：
{context}

用户问题：
{question}

请给出简洁、准确的回答：
"""


class RAGEngine:
    def __init__(
        self,
        data_path: str = r"D:\demo1\data\产品1.txt",
        persist_dir: str = "./chroma_db1",
        collection_name: str = "demo",
        rebuild: bool = False,
        retrieve_k: int = 7,
        rerank_top_k: int = 3,
        embedding_model: str = "text-embedding-v2",
        rerank_model: str = "BAAI/bge-reranker-base",
        llm_model: str = "qwen-turbo",
    ) -> None:
        self.data_path = data_path
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.retrieve_k = retrieve_k
        self.rerank_top_k = rerank_top_k

        self.embeddings = DashScopeEmbeddings(
            model=embedding_model,
            dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
        )
    if rebuild and os.path.isdir(persist_dir):
    # 兼容挂载点：只删里面的内容，不删目录本身
        for name in os.listdir(persist_dir):
            path = os.path.join(persist_dir, name)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
        print(f"[RAG] 已清空旧向量库内容: {persist_dir}")

        self.db = self._build_or_load()

        self.retriever = self.db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": self.retrieve_k},
        )

        print("[RAG] 正在加载重排模型 ...")
        self.reranker = CrossEncoder(rerank_model)

        print("[RAG] 正在加载 LLM ...")
        self.llm = Tongyi(model=llm_model)

        self.prompt_template = ChatPromptTemplate.from_messages([("human", PROMPT)])
        print("[RAG] 引擎就绪 ✅")

    # ---------- 建库 / 加载 ----------
    def _build_or_load(self) -> Chroma:
        if os.path.isdir(self.persist_dir) and os.listdir(self.persist_dir):
            print(f"[RAG] 加载已有向量库: {self.persist_dir}")
            return Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_dir,
            )

        print(f"[RAG] 构建向量库，数据源: {self.data_path}")
        docs = TextLoader(file_path=self.data_path, encoding="utf-8").load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "。", "？", "！", "；", "，", "、", "\n", " ", ""],
        )
        documents = splitter.split_documents(docs)
        print(f"[RAG] 切分后共 {len(documents)} 个块")

        return Chroma.from_documents(
            collection_name=self.collection_name,
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_dir,
            collection_metadata={"hnsw:space": "cosine"},
        )

    # ---------- 问答 ----------
    def ask(self, question: str, top_k: Optional[int] = None) -> Dict[str, Any]:
        question = (question or "").strip()
        if not question:
            raise ValueError("问题不能为空")

        # 1) 向量召回
        retrieved_docs = self.retriever.invoke(question)
        if not retrieved_docs:
            return {"answer": "抱歉，知识库中没有检索到相关内容。", "sources": []}

        # 2) 重排
        pairs = [[question, d.page_content] for d in retrieved_docs]
        scores = self.reranker.predict(pairs)
        ranked = sorted(
            zip(retrieved_docs, scores), key=lambda x: float(x[1]), reverse=True
        )
        k = top_k or self.rerank_top_k
        top = ranked[:k]

        # 3) 只把重排后的 top-k 拼进上下文（原代码这里是 bug）
        context_text = "\n\n---\n\n".join(d.page_content for d, _ in top)

        formatted_prompt = self.prompt_template.format(
            question=question, context=context_text
        )
        answer = self.llm.invoke(formatted_prompt)

        # 4) 组装 sources
        sources: List[Dict[str, Any]] = [
            {
                "index": i + 1,
                "content": doc.page_content,
                "score": round(float(score), 4),
                "metadata": dict(doc.metadata or {}),
            }
            for i, (doc, score) in enumerate(top)
        ]

        return {"answer": answer, "sources": sources}