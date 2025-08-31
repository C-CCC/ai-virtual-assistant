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

"""
Baes class to store the user conversation in database permanently
"""

from typing import List, Optional
from datetime import datetime

from src.common.utils import get_config
from src.agent.datastore.postgres_client import PostgresClient
# from src.agent.datastore.redis_client import RedisClient


class Datastore:
    def __init__(self):
        db_name = get_config().database.name
        if db_name == "postgres":
            print("Using postgres to store conversation history")
            self.database = PostgresClient()
        elif db_name == "none":
            print("Using mock database for testing (no persistence)")
            self.database = MockDatabaseClient()
        # elif db_name == "redis":
        #     print("Using Redis to store conversation history")
        #     self.database = RedisClient()
        else:
            raise ValueError(f"{db_name} database in not supported. Supported types: postgres, none")

    def store_conversation(self, session_id: str, user_id: Optional[str], conversation_history: list, last_conversation_time: str, start_conversation_time: str):
        """store conversation for given details"""
        self.database.store_conversation(session_id, user_id, conversation_history, last_conversation_time, start_conversation_time)

    def fetch_conversation(self, session_id: str):
        """fetch conversation for given session id"""
        self.database.fetch_conversation(session_id)

    def delete_conversation(self, session_id: str):
        """delete conversation for given session id"""
        self.database.delete_conversation(session_id)

    def is_session(self, session_id: str) -> bool:
        """check if session exists"""
        return self.database.is_session(session_id)


class MockDatabaseClient:
    """Mock database client for testing without external dependencies"""
    
    def __init__(self):
        self.conversations = {}
        print("Mock database initialized - no persistence")
    
    def store_conversation(self, session_id: str, user_id: Optional[str], conversation_history: list, last_conversation_time: str, start_conversation_time: str):
        """Mock store conversation"""
        self.conversations[session_id] = {
            "user_id": user_id,
            "conversation_history": conversation_history,
            "last_conversation_time": last_conversation_time,
            "start_conversation_time": start_conversation_time
        }
        print(f"Mock: Stored conversation for session {session_id}")
    
    def fetch_conversation(self, session_id: str):
        """Mock fetch conversation"""
        return self.conversations.get(session_id, None)
    
    def delete_conversation(self, session_id: str):
        """Mock delete conversation"""
        if session_id in self.conversations:
            del self.conversations[session_id]
            print(f"Mock: Deleted conversation for session {session_id}")
    
    def is_session(self, session_id: str) -> bool:
        """Mock check if session exists"""
        return session_id in self.conversations