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

"""DataRobot client adapter for AI Virtual Assistant."""
import os
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

try:
    import datarobot as dr
    from datarobot import PredictionServer
    from datarobot.models import Deployment
except ImportError:
    dr = None
    logging.warning("DataRobot SDK not installed. Install with: pip install datarobot")

logger = logging.getLogger(__name__)

@dataclass
class DataRobotConfig:
    """Configuration for DataRobot endpoints."""
    api_token: str
    endpoint: str
    deployment_id: str
    model_name: str
    max_retries: int = 3
    timeout: int = 300

class DataRobotLLMClient:
    """DataRobot client for LLM inference."""
    
    def __init__(self, config: DataRobotConfig):
        self.config = config
        self._client = None
        self._deployment = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize DataRobot client."""
        try:
            dr.Client(token=self.config.api_token, endpoint=self.config.endpoint)
            self._deployment = Deployment.get(self.config.deployment_id)
            logger.info(f"Initialized DataRobot client for deployment: {self.config.deployment_id}")
        except Exception as e:
            logger.error(f"Failed to initialize DataRobot client: {e}")
            raise
    
    def predict(self, prompt: str, **kwargs) -> str:
        """Generate text prediction from prompt."""
        try:
            # Prepare prediction data
            prediction_data = dr.Dataset.from_dataframe(
                pd.DataFrame([{"prompt": prompt}])
            )
            
            # Make prediction
            predictions = self._deployment.predict(prediction_data)
            
            if predictions and len(predictions) > 0:
                return str(predictions[0])
            else:
                raise ValueError("No prediction returned from DataRobot")
                
        except Exception as e:
            logger.error(f"DataRobot prediction failed: {e}")
            raise
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate chat response from messages."""
        # Convert messages to a single prompt
        prompt = self._format_messages_to_prompt(messages)
        return self.predict(prompt, **kwargs)
    
    def _format_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Format chat messages into a single prompt string."""
        formatted_prompt = ""
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            if role == "system":
                formatted_prompt += f"System: {content}\n"
            elif role == "user":
                formatted_prompt += f"User: {content}\n"
            elif role == "assistant":
                formatted_prompt += f"Assistant: {content}\n"
        
        formatted_prompt += "Assistant:"
        return formatted_prompt

class DataRobotEmbeddingsClient:
    """DataRobot client for embeddings."""
    
    def __init__(self, config: DataRobotConfig):
        self.config = config
        self._client = None
        self._deployment = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize DataRobot client."""
        try:
            dr.Client(token=self.config.api_token, endpoint=self.config.endpoint)
            self._deployment = Deployment.get(self.config.deployment_id)
            logger.info(f"Initialized DataRobot embeddings client for deployment: {self.config.deployment_id}")
        except Exception as e:
            logger.error(f"Failed to initialize DataRobot embeddings client: {e}")
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of documents."""
        try:
            embeddings = []
            for text in texts:
                # Prepare prediction data
                prediction_data = dr.Dataset.from_dataframe(
                    pd.DataFrame([{"text": text}])
                )
                
                # Make prediction
                prediction = self._deployment.predict(prediction_data)
                
                if prediction and len(prediction) > 0:
                    # Assuming the prediction returns a list of floats
                    embedding = prediction[0]
                    if isinstance(embedding, str):
                        # Parse string representation if needed
                        embedding = eval(embedding)
                    embeddings.append(embedding)
                else:
                    raise ValueError(f"No embedding returned for text: {text[:100]}...")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"DataRobot embeddings failed: {e}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query."""
        embeddings = self.embed_documents([text])
        return embeddings[0] if embeddings else []

class DataRobotRerankClient:
    """DataRobot client for reranking."""
    
    def __init__(self, config: DataRobotConfig):
        self.config = config
        self._client = None
        self._deployment = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize DataRobot client."""
        try:
            dr.Client(token=self.config.api_token, endpoint=self.config.endpoint)
            self._deployment = Deployment.get(self.config.deployment_id)
            logger.info(f"Initialized DataRobot rerank client for deployment: {self.config.deployment_id}")
        except Exception as e:
            logger.error(f"Failed to initialize DataRobot rerank client: {e}")
            raise
    
    def rerank(self, query: str, documents: List[str], top_k: int = None) -> List[Dict[str, Any]]:
        """Rerank documents based on query relevance."""
        try:
            results = []
            
            for i, doc in enumerate(documents):
                # Prepare prediction data with query and document
                prediction_data = dr.Dataset.from_dataframe(
                    pd.DataFrame([{
                        "query": query,
                        "document": doc,
                        "document_index": i
                    }])
                )
                
                # Make prediction
                prediction = self._deployment.predict(prediction_data)
                
                if prediction and len(prediction) > 0:
                    score = float(prediction[0])
                    results.append({
                        "document": doc,
                        "score": score,
                        "index": i
                    })
                else:
                    logger.warning(f"No rerank score returned for document {i}")
            
            # Sort by score (higher is better)
            results.sort(key=lambda x: x["score"], reverse=True)
            
            # Apply top_k if specified
            if top_k is not None:
                results = results[:top_k]
            
            return results
            
        except Exception as e:
            logger.error(f"DataRobot reranking failed: {e}")
            raise

# Import pandas for DataFrame operations
try:
    import pandas as pd
except ImportError:
    pd = None
    logging.warning("pandas not installed. Install with: pip install pandas")
