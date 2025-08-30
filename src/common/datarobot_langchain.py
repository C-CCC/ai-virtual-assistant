# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""LangChain-compatible DataRobot clients for AI Virtual Assistant."""
import logging
from typing import Any, Iterator, List, Optional, Dict
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.embeddings import Embeddings
from langchain_core.documents.compressor import BaseDocumentCompressor
from langchain_core.documents import Document

from .datarobot_client import DataRobotConfig, DataRobotLLMClient, DataRobotEmbeddingsClient, DataRobotRerankClient

logger = logging.getLogger(__name__)

class DataRobotChatModel(BaseChatModel):
    """LangChain-compatible DataRobot chat model."""
    
    def __init__(self, config: DataRobotConfig, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self._client = DataRobotLLMClient(config)
    
    @property
    def _llm_type(self) -> str:
        return "datarobot"
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate chat response."""
        try:
            # Convert LangChain messages to DataRobot format
            dr_messages = []
            for message in messages:
                if isinstance(message, SystemMessage):
                    dr_messages.append({"role": "system", "content": message.content})
                elif isinstance(message, HumanMessage):
                    dr_messages.append({"role": "user", "content": message.content})
                elif isinstance(message, AIMessage):
                    dr_messages.append({"role": "assistant", "content": message.content})
                else:
                    # Handle other message types as user messages
                    dr_messages.append({"role": "user", "content": str(message.content)})
            
            # Get response from DataRobot
            response = self._client.chat(dr_messages, **kwargs)
            
            # Create AIMessage from response
            ai_message = AIMessage(content=response)
            
            # Return ChatResult
            return ChatResult(
                generations=[ChatGeneration(message=ai_message)]
            )
            
        except Exception as e:
            logger.error(f"DataRobot chat generation failed: {e}")
            raise
    
    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> Iterator[ChatResult]:
        """Stream chat response (not supported by DataRobot, so we return single response)."""
        # DataRobot doesn't support streaming, so we return the full response
        result = self._generate(messages, stop, run_manager, **kwargs)
        yield result

class DataRobotEmbeddings(Embeddings):
    """LangChain-compatible DataRobot embeddings."""
    
    def __init__(self, config: DataRobotConfig):
        self.config = config
        self._client = DataRobotEmbeddingsClient(config)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        return self._client.embed_documents(texts)
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query."""
        return self._client.embed_query(text)

class DataRobotRerank(BaseDocumentCompressor):
    """LangChain-compatible DataRobot reranker."""
    
    def __init__(self, config: DataRobotConfig, top_n: int = 10):
        self.config = config
        self.top_n = top_n
        self._client = DataRobotRerankClient(config)
    
    def compress_documents(
        self,
        documents: List[Document],
        query: str,
    ) -> List[Document]:
        """Rerank and compress documents based on query relevance."""
        try:
            # Extract text content from documents
            texts = [doc.page_content for doc in documents]
            
            # Get reranked results from DataRobot
            reranked_results = self._client.rerank(query, texts, top_k=self.top_n)
            
            # Create new documents with reranked order
            reranked_docs = []
            for result in reranked_results:
                doc_index = result["index"]
                original_doc = documents[doc_index]
                
                # Create new document with metadata including rerank score
                new_doc = Document(
                    page_content=original_doc.page_content,
                    metadata={
                        **original_doc.metadata,
                        "rerank_score": result["score"],
                        "rerank_rank": len(reranked_docs) + 1
                    }
                )
                reranked_docs.append(new_doc)
            
            return reranked_docs
            
        except Exception as e:
            logger.error(f"DataRobot reranking failed: {e}")
            # Return original documents if reranking fails
            return documents[:self.top_n]
