"""
Azure-Powered MCP Collaboration Tools for DeepSeek R1 Multi-Agent System
Enables intelligent inter-agent communication using Azure services
"""

import json
import uuid
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import asyncio
from azure.storage.blob import BlobServiceClient
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.cosmos import CosmosClient, PartitionKey
import os

class CollaborationMessageType(Enum):
    """Types of collaboration messages between agents"""
    TASK_REQUEST = "task_request"
    KNOWLEDGE_SHARE = "knowledge_share"
    PEER_REVIEW = "peer_review"
    CONSENSUS_BUILDING = "consensus_building"
    CONFLICT_RESOLUTION = "conflict_resolution"
    STATUS_UPDATE = "status_update"
    URGENT_CONSULTATION = "urgent_consultation"
    CROSS_VALIDATION = "cross_validation"

@dataclass
class CollaborationTask:
    """Structure for collaborative tasks between agents"""
    task_id: str
    requester: str
    assignee: str
    task_type: CollaborationMessageType
    description: str
    context: Dict[str, Any]
    priority: int  # 1-5, 5 being highest
    deadline: Optional[datetime]
    status: str  # "pending", "in_progress", "completed", "blocked"
    created_at: datetime
    updated_at: datetime
    dependencies: List[str]  # Other task IDs this depends on
    artifacts: List[str]  # URLs to shared artifacts

@dataclass
class SharedArtifact:
    """Shared artifacts between agents (stored in Azure Blob)"""
    artifact_id: str
    name: str
    type: str  # "document", "analysis", "budget", "research"
    creator: str
    content: str
    metadata: Dict[str, Any]
    blob_url: str
    created_at: datetime
    access_permissions: List[str]  # Which agents can access

class AzureMCPCollaborationTools:
    """MCP Collaboration Tools powered by Azure services"""
    
    def __init__(self):
        # Azure service configuration (using your credits)
        self.storage_account_name = os.getenv('AZURE_STORAGE_ACCOUNT', 'grantstorage')
        self.storage_account_key = os.getenv('AZURE_STORAGE_KEY', '')
        self.servicebus_connection_string = os.getenv('AZURE_SERVICEBUS_CONNECTION', '')
        self.cosmos_endpoint = os.getenv('AZURE_COSMOS_ENDPOINT', '')
        self.cosmos_key = os.getenv('AZURE_COSMOS_KEY', '')
        
        # Initialize Azure clients
        self.blob_service_client = None
        self.servicebus_client = None
        self.cosmos_client = None
        self.tasks_container = None
        self.artifacts_container = None
        
        self._initialize_azure_services()
    
    def _initialize_azure_services(self):
        """Initialize Azure services for collaboration"""
        try:
            # Azure Blob Storage for shared artifacts (covered by credits)
            if self.storage_account_key:
                self.blob_service_client = BlobServiceClient(
                    account_url=f"https://{self.storage_account_name}.blob.core.windows.net",
                    credential=self.storage_account_key
                )
                print("✅ Azure Blob Storage initialized for shared artifacts")
            
            # Azure Service Bus for real-time messaging (covered by credits)
            if self.servicebus_connection_string:
                self.servicebus_client = ServiceBusClient.from_connection_string(
                    self.servicebus_connection_string
                )
                print("✅ Azure Service Bus initialized for real-time messaging")
            
            # Azure Cosmos DB for task management (covered by credits)
            if self.cosmos_endpoint and self.cosmos_key:
                self.cosmos_client = CosmosClient(self.cosmos_endpoint, self.cosmos_key)
                database = self.cosmos_client.create_database_if_not_exists("GrantCollaboration")
                
                # Create containers for tasks and artifacts
                self.tasks_container = database.create_container_if_not_exists(
                    id="CollaborationTasks",
                    partition_key=PartitionKey(path="/requester"),
                    offer_throughput=400
                )
                
                self.artifacts_container = database.create_container_if_not_exists(
                    id="SharedArtifacts", 
                    partition_key=PartitionKey(path="/creator"),
                    offer_throughput=400
                )
                print("✅ Azure Cosmos DB initialized for task management")
                
        except Exception as e:
            print(f"⚠️ Warning: Some Azure collaboration services not available: {e}")
    
    def create_collaboration_task(self, requester: str, assignee: str, 
                                task_type: CollaborationMessageType, description: str,
                                context: Dict = None, priority: int = 3, 
                                deadline: datetime = None) -> str:
        """
        MCP Tool: Create Collaboration Task
        Uses Azure Cosmos DB (covered by your credits)
        """
        task_id = f"task_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
        
        task = CollaborationTask(
            task_id=task_id,
            requester=requester,
            assignee=assignee, 
            task_type=task_type,
            description=description,
            context=context or {},
            priority=priority,
            deadline=deadline,
            status="pending",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            dependencies=[],
            artifacts=[]
        )
        
        try:
            if self.tasks_container:
                # Store in Azure Cosmos DB (using your credits)
                self.tasks_container.create_item(body=self._task_to_dict(task))
                
                # Send real-time notification via Azure Service Bus
                self._send_task_notification(task)
                
                print(f"🤝 Collaboration task created: {requester} → {assignee} ({task_type.value})")
                return task_id
            else:
                # Fallback storage
                return self._store_task_fallback(task)
                
        except Exception as e:
            print(f"❌ Error creating collaboration task: {e}")
            return self._store_task_fallback(task)
    
    def get_assigned_tasks(self, agent_name: str, status_filter: str = None) -> List[CollaborationTask]:
        """
        MCP Tool: Get Tasks Assigned to Agent
        Uses Azure Cosmos DB query (covered by your credits)
        """
        try:
            if self.tasks_container:
                # Query Azure Cosmos DB
                query = "SELECT * FROM c WHERE c.assignee = @assignee"
                parameters = [{"name": "@assignee", "value": agent_name}]
                
                if status_filter:
                    query += " AND c.status = @status"
                    parameters.append({"name": "@status", "value": status_filter})
                
                query += " ORDER BY c.priority DESC, c.created_at ASC"
                
                items = self.tasks_container.query_items(
                    query=query,
                    parameters=parameters,
                    enable_cross_partition_query=True
                )
                
                tasks = [self._dict_to_task(item) for item in items]
                print(f"📋 Found {len(tasks)} tasks for {agent_name}")
                return tasks
            else:
                return self._get_tasks_fallback(agent_name, status_filter)
                
        except Exception as e:
            print(f"❌ Error retrieving tasks: {e}")
            return self._get_tasks_fallback(agent_name, status_filter)
    
    def update_task_status(self, task_id: str, status: str, agent_name: str,
                          progress_notes: str = None) -> bool:
        """
        MCP Tool: Update Task Status
        Uses Azure Cosmos DB (covered by your credits)
        """
        try:
            if self.tasks_container:
                # Retrieve and update task
                task_items = list(self.tasks_container.query_items(
                    query="SELECT * FROM c WHERE c.task_id = @task_id",
                    parameters=[{"name": "@task_id", "value": task_id}],
                    enable_cross_partition_query=True
                ))
                
                if task_items:
                    task_data = task_items[0]
                    task_data['status'] = status
                    task_data['updated_at'] = datetime.now().isoformat()
                    
                    if progress_notes:
                        if 'progress_notes' not in task_data:
                            task_data['progress_notes'] = []
                        task_data['progress_notes'].append({
                            'timestamp': datetime.now().isoformat(),
                            'agent': agent_name,
                            'notes': progress_notes
                        })
                    
                    self.tasks_container.replace_item(item=task_data['id'], body=task_data)
                    
                    # Notify requester of status change
                    self._send_status_notification(task_data, agent_name)
                    
                    print(f"✅ Task {task_id} updated to status: {status}")
                    return True
                
        except Exception as e:
            print(f"❌ Error updating task status: {e}")
            
        return False
    
    def share_artifact(self, creator: str, artifact_name: str, artifact_type: str,
                      content: str, metadata: Dict = None, 
                      access_permissions: List[str] = None) -> str:
        """
        MCP Tool: Share Artifact Between Agents
        Uses Azure Blob Storage (covered by your credits)
        """
        artifact_id = f"artifact_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
        
        try:
            if self.blob_service_client:
                # Store content in Azure Blob Storage
                container_name = "shared-artifacts"
                blob_name = f"{creator}/{artifact_id}.json"
                
                # Ensure container exists
                try:
                    self.blob_service_client.create_container(container_name)
                except:
                    pass  # Container might already exist
                
                # Upload artifact content
                blob_client = self.blob_service_client.get_blob_client(
                    container=container_name, 
                    blob=blob_name
                )
                
                artifact_data = {
                    "content": content,
                    "metadata": metadata or {},
                    "created_at": datetime.now().isoformat(),
                    "creator": creator
                }
                
                blob_client.upload_blob(
                    json.dumps(artifact_data, indent=2),
                    overwrite=True
                )
                
                blob_url = blob_client.url
                
                # Store artifact metadata in Cosmos DB
                artifact = SharedArtifact(
                    artifact_id=artifact_id,
                    name=artifact_name,
                    type=artifact_type,
                    creator=creator,
                    content=content[:500] + "..." if len(content) > 500 else content,
                    metadata=metadata or {},
                    blob_url=blob_url,
                    created_at=datetime.now(),
                    access_permissions=access_permissions or ["all"]
                )
                
                if self.artifacts_container:
                    self.artifacts_container.create_item(body=self._artifact_to_dict(artifact))
                
                print(f"📎 Artifact shared: {artifact_name} by {creator}")
                return artifact_id
            else:
                return self._store_artifact_fallback(creator, artifact_name, content)
                
        except Exception as e:
            print(f"❌ Error sharing artifact: {e}")
            return self._store_artifact_fallback(creator, artifact_name, content)
    
    def get_shared_artifacts(self, agent_name: str, artifact_type: str = None) -> List[SharedArtifact]:
        """
        MCP Tool: Get Accessible Shared Artifacts  
        Uses Azure Cosmos DB and Blob Storage (covered by your credits)
        """
        try:
            if self.artifacts_container:
                # Query artifacts the agent can access
                query = "SELECT * FROM c WHERE ARRAY_CONTAINS(c.access_permissions, @agent) OR ARRAY_CONTAINS(c.access_permissions, 'all')"
                parameters = [{"name": "@agent", "value": agent_name}]
                
                if artifact_type:
                    query += " AND c.type = @type"
                    parameters.append({"name": "@type", "value": artifact_type})
                
                query += " ORDER BY c.created_at DESC"
                
                items = self.artifacts_container.query_items(
                    query=query,
                    parameters=parameters,
                    enable_cross_partition_query=True
                )
                
                artifacts = [self._dict_to_artifact(item) for item in items]
                print(f"📚 Found {len(artifacts)} accessible artifacts for {agent_name}")
                return artifacts
            else:
                return self._get_artifacts_fallback(agent_name)
                
        except Exception as e:
            print(f"❌ Error retrieving artifacts: {e}")
            return self._get_artifacts_fallback(agent_name)
    
    def request_peer_review(self, requester: str, content: str, 
                           reviewers: List[str], review_criteria: str = None) -> List[str]:
        """
        MCP Tool: Request Peer Review from Multiple Agents
        Creates collaboration tasks for reviews
        """
        task_ids = []
        
        for reviewer in reviewers:
            context = {
                "content_to_review": content,
                "review_criteria": review_criteria or "General quality and accuracy review",
                "review_type": "peer_review"
            }
            
            task_id = self.create_collaboration_task(
                requester=requester,
                assignee=reviewer,
                task_type=CollaborationMessageType.PEER_REVIEW,
                description=f"Please review the following content: {content[:100]}...",
                context=context,
                priority=4,
                deadline=datetime.now() + timedelta(hours=2)
            )
            
            task_ids.append(task_id)
        
        print(f"👥 Peer review requested from {len(reviewers)} agents")
        return task_ids
    
    def build_consensus(self, initiator: str, topic: str, options: List[str],
                       participants: List[str]) -> str:
        """
        MCP Tool: Build Consensus Among Agents
        Uses collaborative decision-making process
        """
        consensus_id = f"consensus_{int(datetime.now().timestamp())}"
        
        # Create consensus-building tasks for all participants
        for participant in participants:
            context = {
                "consensus_id": consensus_id,
                "topic": topic,
                "options": options,
                "participants": participants,
                "voting_deadline": (datetime.now() + timedelta(hours=1)).isoformat()
            }
            
            self.create_collaboration_task(
                requester=initiator,
                assignee=participant,
                task_type=CollaborationMessageType.CONSENSUS_BUILDING,
                description=f"Please provide input on: {topic}",
                context=context,
                priority=4
            )
        
        print(f"🤝 Consensus building initiated: {topic}")
        return consensus_id
    
    def _send_task_notification(self, task: CollaborationTask):
        """Send real-time notification via Azure Service Bus"""
        try:
            if self.servicebus_client:
                sender = self.servicebus_client.get_queue_sender(queue_name="agent-notifications")
                
                message = ServiceBusMessage(
                    json.dumps({
                        "type": "new_task",
                        "task_id": task.task_id,
                        "assignee": task.assignee,
                        "requester": task.requester,
                        "priority": task.priority,
                        "description": task.description
                    })
                )
                
                sender.send_messages(message)
                sender.close()
                
        except Exception as e:
            print(f"⚠️ Could not send real-time notification: {e}")
    
    def _send_status_notification(self, task_data: Dict, agent_name: str):
        """Send status update notification"""
        try:
            if self.servicebus_client:
                sender = self.servicebus_client.get_queue_sender(queue_name="agent-notifications")
                
                message = ServiceBusMessage(
                    json.dumps({
                        "type": "task_status_update",
                        "task_id": task_data['task_id'],
                        "status": task_data['status'],
                        "updated_by": agent_name,
                        "requester": task_data['requester']
                    })
                )
                
                sender.send_messages(message)
                sender.close()
                
        except Exception as e:
            print(f"⚠️ Could not send status notification: {e}")
    
    # Helper methods for data conversion
    def _task_to_dict(self, task: CollaborationTask) -> Dict:
        result = asdict(task)
        result['created_at'] = task.created_at.isoformat()
        result['updated_at'] = task.updated_at.isoformat() 
        result['task_type'] = task.task_type.value
        if task.deadline:
            result['deadline'] = task.deadline.isoformat()
        result['id'] = task.task_id  # Cosmos DB requires 'id' field
        return result
    
    def _dict_to_task(self, data: Dict) -> CollaborationTask:
        return CollaborationTask(
            task_id=data['task_id'],
            requester=data['requester'],
            assignee=data['assignee'],
            task_type=CollaborationMessageType(data['task_type']),
            description=data['description'],
            context=data['context'],
            priority=data['priority'],
            deadline=datetime.fromisoformat(data['deadline']) if data.get('deadline') else None,
            status=data['status'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            dependencies=data.get('dependencies', []),
            artifacts=data.get('artifacts', [])
        )
    
    def _artifact_to_dict(self, artifact: SharedArtifact) -> Dict:
        result = asdict(artifact)
        result['created_at'] = artifact.created_at.isoformat()
        result['id'] = artifact.artifact_id
        return result
    
    def _dict_to_artifact(self, data: Dict) -> SharedArtifact:
        return SharedArtifact(
            artifact_id=data['artifact_id'],
            name=data['name'],
            type=data['type'],
            creator=data['creator'],
            content=data['content'],
            metadata=data['metadata'],
            blob_url=data['blob_url'],
            created_at=datetime.fromisoformat(data['created_at']),
            access_permissions=data['access_permissions']
        )
    
    # Fallback methods for development
    def _store_task_fallback(self, task: CollaborationTask) -> str:
        print(f"⚠️ Using fallback task storage - configure Azure services for full functionality")
        return task.task_id
    
    def _get_tasks_fallback(self, agent_name: str, status_filter: str = None) -> List[CollaborationTask]:
        print(f"⚠️ Using fallback task retrieval - configure Azure services for full functionality")
        return []
    
    def _store_artifact_fallback(self, creator: str, name: str, content: str) -> str:
        artifact_id = f"fallback_{uuid.uuid4().hex[:8]}"
        print(f"⚠️ Using fallback artifact storage - configure Azure Blob Storage for full functionality")
        return artifact_id
    
    def _get_artifacts_fallback(self, agent_name: str) -> List[SharedArtifact]:
        print(f"⚠️ Using fallback artifact retrieval - configure Azure services for full functionality")
        return []

# MCP Collaboration Tool Registry
COLLABORATION_TOOLS = {
    "create_task": {
        "name": "Create Collaboration Task",
        "description": "Create a task for another agent to complete",
        "azure_service": "Cosmos DB + Service Bus",
        "cost": "$0.01-0.05 per task"
    },
    
    "get_tasks": {
        "name": "Get Assigned Tasks",
        "description": "Retrieve tasks assigned to this agent", 
        "azure_service": "Cosmos DB",
        "cost": "$0.001-0.01 per query"
    },
    
    "share_artifact": {
        "name": "Share Artifact",
        "description": "Share documents/analysis with other agents",
        "azure_service": "Blob Storage + Cosmos DB",
        "cost": "$0.01-0.05 per artifact"
    },
    
    "peer_review": {
        "name": "Request Peer Review",
        "description": "Get other agents to review your work",
        "azure_service": "Multiple services",
        "cost": "$0.02-0.10 per review request"
    },
    
    "build_consensus": {
        "name": "Build Consensus",
        "description": "Collaborative decision making between agents",
        "azure_service": "Multiple services", 
        "cost": "$0.05-0.20 per consensus process"
    }
}

def create_collaboration_tools():
    """Initialize Azure-powered MCP collaboration tools"""
    tools = AzureMCPCollaborationTools()
    
    print("🤝 Azure MCP Collaboration Tools initialized:")
    for tool_name, tool_info in COLLABORATION_TOOLS.items():
        print(f"  ✅ {tool_info['name']} - {tool_info['azure_service']}")
    
    return tools

if __name__ == "__main__":
    # Test collaboration tools
    tools = create_collaboration_tools()
    
    print("🧪 Testing Azure MCP Collaboration Tools...")
    
    # Test task creation
    task_id = tools.create_collaboration_task(
        requester="general_manager",
        assignee="research_agent", 
        task_type=CollaborationMessageType.TASK_REQUEST,
        description="Research NSF funding opportunities for AI projects",
        priority=4
    )
    print(f"✅ Created collaboration task: {task_id}")
    
    # Test artifact sharing
    artifact_id = tools.share_artifact(
        creator="research_agent",
        artifact_name="NSF Research Findings",
        artifact_type="research",
        content="Sample research findings about NSF AI funding...",
        access_permissions=["budget_agent", "writing_agent"]
    )
    print(f"✅ Shared artifact: {artifact_id}")
    
    print("🚀 Azure MCP Collaboration Tools ready!")