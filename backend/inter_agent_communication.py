"""
Inter-Agent Communication System for DeepSeek R1 Multi-Agent Architecture
Enables real-time collaboration and knowledge sharing between agents
"""

import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import uuid

class MessageType(Enum):
    """Types of inter-agent messages"""
    REQUEST_INFO = "request_info"
    SHARE_FINDINGS = "share_findings"
    REQUEST_REVIEW = "request_review"
    PROVIDE_FEEDBACK = "provide_feedback"
    COLLABORATION_REQUEST = "collaboration_request"
    QUESTION = "question"
    ANSWER = "answer"
    STATUS_UPDATE = "status_update"
    EMERGENCY_CONSULT = "emergency_consult"

@dataclass
class AgentMessage:
    """Structure for messages between agents"""
    id: str
    sender: str
    recipient: str  # Can be "broadcast" for all agents
    message_type: MessageType
    content: str
    context: Dict[str, Any]
    timestamp: datetime
    priority: int = 1  # 1=low, 2=medium, 3=high, 4=urgent
    requires_response: bool = False
    response_deadline: Optional[datetime] = None
    thread_id: Optional[str] = None

    def to_dict(self) -> Dict:
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        result['message_type'] = self.message_type.value
        if self.response_deadline:
            result['response_deadline'] = self.response_deadline.isoformat()
        return result

class CommunicationBus:
    """Central communication hub for all agents"""
    
    def __init__(self):
        self.messages: List[AgentMessage] = []
        self.agent_subscriptions: Dict[str, List[MessageType]] = {}
        self.active_threads: Dict[str, List[str]] = {}  # thread_id -> message_ids
        self.agent_status: Dict[str, str] = {}
        
    def register_agent(self, agent_name: str, subscriptions: List[MessageType] = None):
        """Register an agent with optional message subscriptions"""
        if subscriptions is None:
            subscriptions = list(MessageType)  # Subscribe to all by default
        
        self.agent_subscriptions[agent_name] = subscriptions
        self.agent_status[agent_name] = "active"
        print(f"✅ Agent {agent_name} registered for communication")
    
    def send_message(self, message: AgentMessage) -> str:
        """Send a message through the communication bus"""
        message.id = str(uuid.uuid4())
        message.timestamp = datetime.now()
        
        self.messages.append(message)
        
        # Handle threading
        if message.thread_id:
            if message.thread_id not in self.active_threads:
                self.active_threads[message.thread_id] = []
            self.active_threads[message.thread_id].append(message.id)
        
        print(f"📨 Message sent: {message.sender} → {message.recipient} ({message.message_type.value})")
        return message.id
    
    def get_messages_for_agent(self, agent_name: str, unread_only: bool = True) -> List[AgentMessage]:
        """Get messages for a specific agent"""
        relevant_messages = []
        
        for message in self.messages:
            # Check if message is for this agent
            if message.recipient == agent_name or message.recipient == "broadcast":
                # Check if agent is subscribed to this message type
                if message.message_type in self.agent_subscriptions.get(agent_name, []):
                    relevant_messages.append(message)
        
        return relevant_messages
    
    def create_thread(self, initiator: str, topic: str) -> str:
        """Create a new conversation thread"""
        thread_id = f"thread_{int(time.time())}_{initiator}"
        self.active_threads[thread_id] = []
        print(f"🧵 New thread created: {thread_id} by {initiator} on '{topic}'")
        return thread_id

class AgentCommunicator:
    """Communication interface for individual agents"""
    
    def __init__(self, agent_name: str, bus: CommunicationBus, deepseek_client):
        self.agent_name = agent_name
        self.bus = bus
        self.deepseek_client = deepseek_client
        self.processed_messages: set = set()
        
        # Register with the bus
        self.bus.register_agent(agent_name)
    
    def send_to_agent(self, recipient: str, message_type: MessageType, content: str, 
                     context: Dict = None, priority: int = 1, requires_response: bool = False) -> str:
        """Send a message to another specific agent"""
        message = AgentMessage(
            id="",  # Will be set by bus
            sender=self.agent_name,
            recipient=recipient,
            message_type=message_type,
            content=content,
            context=context or {},
            timestamp=datetime.now(),
            priority=priority,
            requires_response=requires_response
        )
        
        return self.bus.send_message(message)
    
    def broadcast(self, message_type: MessageType, content: str, context: Dict = None) -> str:
        """Broadcast a message to all agents"""
        return self.send_to_agent("broadcast", message_type, content, context)
    
    def ask_agent(self, recipient: str, question: str, context: Dict = None, priority: int = 2) -> str:
        """Ask a specific agent a question"""
        return self.send_to_agent(
            recipient, MessageType.QUESTION, question, context, priority, requires_response=True
        )
    
    def request_collaboration(self, recipient: str, task_description: str, context: Dict = None) -> str:
        """Request collaboration from another agent"""
        return self.send_to_agent(
            recipient, MessageType.COLLABORATION_REQUEST, task_description, context, 
            priority=2, requires_response=True
        )
    
    def share_findings(self, findings: str, context: Dict = None) -> str:
        """Share findings with all other agents"""
        return self.broadcast(MessageType.SHARE_FINDINGS, findings, context)
    
    def request_review(self, content: str, reviewer: str, context: Dict = None) -> str:
        """Request another agent to review your work"""
        return self.send_to_agent(
            reviewer, MessageType.REQUEST_REVIEW, content, context, priority=2, requires_response=True
        )
    
    def check_messages(self) -> List[AgentMessage]:
        """Check for new messages"""
        all_messages = self.bus.get_messages_for_agent(self.agent_name)
        new_messages = [msg for msg in all_messages if msg.id not in self.processed_messages]
        
        # Mark as processed
        for msg in new_messages:
            self.processed_messages.add(msg.id)
        
        return new_messages
    
    def respond_to_message(self, original_message: AgentMessage, response_content: str):
        """Respond to a message that requires response"""
        response = AgentMessage(
            id="",
            sender=self.agent_name,
            recipient=original_message.sender,
            message_type=MessageType.ANSWER if original_message.message_type == MessageType.QUESTION else MessageType.PROVIDE_FEEDBACK,
            content=response_content,
            context={"responding_to": original_message.id},
            timestamp=datetime.now(),
            thread_id=original_message.thread_id
        )
        
        return self.bus.send_message(response)
    
    def process_messages_with_deepseek(self) -> Dict[str, str]:
        """Process incoming messages using DeepSeek R1 reasoning"""
        new_messages = self.check_messages()
        responses = {}
        
        for message in new_messages:
            if message.requires_response:
                # Use DeepSeek R1 to generate intelligent response
                system_prompt = f"""You are the {self.agent_name} in a multi-agent grant writing system.
                
<think>
Another agent ({message.sender}) has sent you a {message.message_type.value}.
Consider your specialized role and expertise to provide the most helpful response.
Use your 671B parameter reasoning to give valuable insights.
</think>

Process this message and provide an appropriate response based on your role."""
                
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Message from {message.sender}: {message.content}"}
                ]
                
                try:
                    response_content = self.deepseek_client.chat_completion(messages, self.agent_name)
                    response_id = self.respond_to_message(message, response_content)
                    responses[message.id] = response_id
                except Exception as e:
                    print(f"❌ Error processing message: {e}")
        
        return responses

# Communication patterns for grant writing
GRANT_COMMUNICATION_PATTERNS = {
    "research_to_budget": {
        "trigger": "research_findings_complete",
        "message_type": MessageType.SHARE_FINDINGS,
        "content_template": "Research findings for budget planning: {findings}"
    },
    
    "budget_to_writing": {
        "trigger": "budget_analysis_complete", 
        "message_type": MessageType.COLLABORATION_REQUEST,
        "content_template": "Budget analysis ready for narrative integration: {budget_summary}"
    },
    
    "cross_validation": {
        "trigger": "any_agent_completion",
        "message_type": MessageType.REQUEST_REVIEW,
        "content_template": "Please review this work for accuracy and alignment: {work_output}"
    },
    
    "general_manager_oversight": {
        "trigger": "major_decision_needed",
        "message_type": MessageType.EMERGENCY_CONSULT,
        "content_template": "Need strategic guidance on: {decision_context}"
    }
}

def create_communication_system():
    """Initialize the inter-agent communication system"""
    bus = CommunicationBus()
    
    # Define agent roles for communication
    agent_roles = [
        "general_manager",
        "research_agent", 
        "budget_agent",
        "writing_agent",
        "impact_agent",
        "networking_agent"
    ]
    
    communicators = {}
    for agent in agent_roles:
        # Note: deepseek_client will be injected when used
        communicators[agent] = None  # Placeholder
    
    print("🔄 Inter-agent communication system initialized")
    print(f"📡 Communication bus ready for {len(agent_roles)} agents")
    
    return bus, communicators

if __name__ == "__main__":
    bus, comms = create_communication_system()
    print("✅ Communication system ready for deployment!")