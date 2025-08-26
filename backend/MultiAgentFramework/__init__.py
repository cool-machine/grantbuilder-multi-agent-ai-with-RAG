"""
Multi-Agent Grant Writing Framework with Transparent Chat Interface
Implements the complete algorithm with orchestrator, voting, and evaluation
"""

import azure.functions as func
import json
import logging
import os
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

class AgentRole(Enum):
    GENERAL_MANAGER = "general_manager"
    RESEARCH_AGENT = "research_agent"
    BUDGET_AGENT = "budget_agent"
    WRITING_AGENT = "writing_agent"
    IMPACT_AGENT = "impact_agent"
    NETWORKING_AGENT = "networking_agent"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    NEEDS_IMPROVEMENT = "needs_improvement"

class VoteResult(Enum):
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"

@dataclass
class ChatMessage:
    timestamp: str
    agent: str
    message_type: str  # plan, action, evaluation, vote, result
    content: str
    task_id: Optional[str] = None
    vote_result: Optional[str] = None

@dataclass
class AgentTask:
    task_id: str
    assigned_to: str
    description: str
    status: str
    plan: Optional[str] = None
    actions: List[str] = None
    result: Optional[str] = None
    evaluation_votes: Dict[str, str] = None
    feedback: List[str] = None

@dataclass
class AgentDeliverable:
    agent: str
    content: str
    status: str
    votes: Dict[str, str] = None
    feedback: List[str] = None
    approved: bool = False

class MultiAgentOrchestrator:
    """
    Implements the complete multi-agent framework with transparent chat
    """
    
    def __init__(self):
        self.agents = {
            AgentRole.GENERAL_MANAGER: "General Manager (Orchestrator)",
            AgentRole.RESEARCH_AGENT: "Research Specialist", 
            AgentRole.BUDGET_AGENT: "Budget Specialist",
            AgentRole.WRITING_AGENT: "Writing Specialist",
            AgentRole.IMPACT_AGENT: "Impact Assessment Specialist",
            AgentRole.NETWORKING_AGENT: "Networking & Partnership Specialist"
        }
        self.chat_history: List[ChatMessage] = []
        self.tasks: List[AgentTask] = []
        self.deliverables: List[AgentDeliverable] = []
        self.final_result: Optional[str] = None
        
    async def process_grant_request(self, prompt: str, context: Dict) -> Dict:
        """
        Main entry point - implements the complete algorithm
        """
        self._add_chat_message("system", "system", "🚀 Starting Multi-Agent Grant Writing Process")
        
        try:
            # PART 1: General Manager Orchestration
            await self._part1_orchestration(prompt, context)
            
            # PART 2: Agent Execution and Evaluation  
            await self._part2_agent_execution()
            
            # PART 3: Final Synthesis and Validation
            await self._part3_final_synthesis()
            
            return {
                "success": True,
                "result": self.final_result,
                "chat_history": [asdict(msg) for msg in self.chat_history],
                "tasks": [asdict(task) for task in self.tasks],
                "deliverables": [asdict(d) for d in self.deliverables],
                "processing_summary": {
                    "total_messages": len(self.chat_history),
                    "total_tasks": len(self.tasks),
                    "total_deliverables": len(self.deliverables),
                    "agents_participated": len(self.agents)
                }
            }
            
        except Exception as e:
            self._add_chat_message("system", "error", f"❌ Framework error: {str(e)}")
            raise
    
    async def _part1_orchestration(self, prompt: str, context: Dict):
        """
        PART 1: General Manager designs plan and allocates tasks
        """
        self._add_chat_message(
            AgentRole.GENERAL_MANAGER.value, 
            "plan", 
            "📋 STEP 1: Analyzing grant requirement and designing action plan..."
        )
        
        # Step 1: Design general action plan
        action_plan = await self._gm_design_action_plan(prompt, context)
        self._add_chat_message(
            AgentRole.GENERAL_MANAGER.value,
            "plan", 
            f"📋 ACTION PLAN CREATED:\n{action_plan}"
        )
        
        # Step 2: Divide plan into tasks
        tasks = await self._gm_divide_into_tasks(action_plan)
        self._add_chat_message(
            AgentRole.GENERAL_MANAGER.value,
            "plan",
            f"📝 TASKS IDENTIFIED: {len(tasks)} tasks created"
        )
        
        # Step 3: Allocate tasks to agents
        await self._gm_allocate_tasks(tasks)
        self._add_chat_message(
            AgentRole.GENERAL_MANAGER.value,
            "plan",
            f"👥 TASK ALLOCATION: Tasks assigned to {len(set(task.assigned_to for task in self.tasks))} agents"
        )
    
    async def _part2_agent_execution(self):
        """
        PART 2: Each agent executes using the 4-step template + evaluation
        """
        self._add_chat_message(
            "system",
            "system", 
            "🔄 PART 2: Starting agent execution phase"
        )
        
        for task in self.tasks:
            await self._execute_agent_task(task)
            
            # Evaluation by all other agents
            await self._evaluate_agent_result(task)
    
    async def _part3_final_synthesis(self):
        """
        PART 3: Final synthesis and group validation
        """
        self._add_chat_message(
            "system",
            "system",
            "🎯 PART 3: Starting final synthesis phase"
        )
        
        # Step 1: Orchestrator synchronizes all deliverables
        final_synthesis = await self._gm_synchronize_deliverables()
        self._add_chat_message(
            AgentRole.GENERAL_MANAGER.value,
            "result",
            f"📋 FINAL SYNTHESIS:\n{final_synthesis}"
        )
        
        # Step 2: Group voting on final result
        final_votes = await self._conduct_final_vote(final_synthesis)
        self._add_chat_message(
            "system",
            "vote",
            f"🗳️ FINAL VOTE RESULTS: {json.dumps(final_votes, indent=2)}"
        )
        
        # Step 3: Decision based on vote
        if self._is_vote_approved(final_votes):
            self.final_result = final_synthesis
            self._add_chat_message(
                "system",
                "result",
                "✅ FINAL RESULT APPROVED BY GROUP VOTE"
            )
        else:
            # Send back for improvement
            self._add_chat_message(
                AgentRole.GENERAL_MANAGER.value,
                "action",
                "🔄 Improving final synthesis based on feedback..."
            )
            # Recursive improvement (simplified for now)
            improved_synthesis = await self._gm_improve_synthesis(final_synthesis, final_votes)
            self.final_result = improved_synthesis
    
    async def _execute_agent_task(self, task: AgentTask):
        """
        Execute single agent task using the 4-step template
        """
        agent_name = self.agents[AgentRole(task.assigned_to)]
        
        self._add_chat_message(
            task.assigned_to,
            "action",
            f"🎯 Starting task: {task.description}",
            task.task_id
        )
        
        iteration = 0
        max_iterations = 3  # Prevent infinite loops
        
        while task.status != TaskStatus.COMPLETED.value and iteration < max_iterations:
            iteration += 1
            
            # Step 1: Write plan of actions and tools
            plan = await self._agent_create_plan(task)
            task.plan = plan
            self._add_chat_message(
                task.assigned_to,
                "plan",
                f"📋 PLAN (Iteration {iteration}):\n{plan}",
                task.task_id
            )
            
            # Step 2: Execute actions with tools
            actions_result = await self._agent_execute_actions(task)
            self._add_chat_message(
                task.assigned_to,
                "action", 
                f"⚡ EXECUTION RESULT:\n{actions_result}",
                task.task_id
            )
            
            # Step 3: Evaluate the result
            evaluation = await self._agent_self_evaluate(task, actions_result)
            self._add_chat_message(
                task.assigned_to,
                "evaluation",
                f"🔍 SELF-EVALUATION:\n{evaluation}",
                task.task_id
            )
            
            # Step 4: Decision based on evaluation
            if evaluation.get("is_good", False):
                task.result = actions_result
                task.status = TaskStatus.COMPLETED.value
                self._add_chat_message(
                    task.assigned_to,
                    "result",
                    f"✅ TASK COMPLETED: {task.description}",
                    task.task_id
                )
            else:
                task.status = TaskStatus.NEEDS_IMPROVEMENT.value
                self._add_chat_message(
                    task.assigned_to,
                    "action",
                    f"🔄 IMPROVING (Iteration {iteration}): {evaluation.get('improvement_reason', 'Need to refine approach')}",
                    task.task_id
                )
    
    async def _evaluate_agent_result(self, task: AgentTask):
        """
        All other agents evaluate the completed task result
        """
        if task.status != TaskStatus.COMPLETED.value:
            return
            
        self._add_chat_message(
            "system",
            "evaluation",
            f"🗳️ Starting group evaluation for task: {task.description}",
            task.task_id
        )
        
        votes = {}
        feedback = []
        
        # Get votes from all other agents (excluding the author)
        for agent_role in self.agents:
            if agent_role.value != task.assigned_to:
                vote, agent_feedback = await self._get_agent_vote(agent_role, task)
                votes[agent_role.value] = vote
                if agent_feedback:
                    feedback.append(f"{self.agents[agent_role]}: {agent_feedback}")
                
                self._add_chat_message(
                    agent_role.value,
                    "vote",
                    f"🗳️ VOTE: {vote.upper()}" + (f" - {agent_feedback}" if agent_feedback else ""),
                    task.task_id,
                    vote
                )
        
        task.evaluation_votes = votes
        task.feedback = feedback
        
        # Determine if task is approved by group vote
        is_approved = self._is_vote_approved(votes)
        
        if is_approved:
            self._add_chat_message(
                "system",
                "result",
                f"✅ TASK APPROVED by group vote: {task.description}",
                task.task_id
            )
        else:
            self._add_chat_message(
                "system", 
                "evaluation",
                f"❌ TASK NEEDS IMPROVEMENT based on group vote: {task.description}",
                task.task_id
            )
            # Send back for improvement
            task.status = TaskStatus.NEEDS_IMPROVEMENT.value
            await self._execute_agent_task(task)  # Re-execute with feedback
    
    def _is_vote_approved(self, votes: Dict[str, str]) -> bool:
        """
        Determine if a vote passes by simple majority
        Orchestrator vote breaks ties
        """
        approve_count = sum(1 for vote in votes.values() if vote == VoteResult.APPROVE.value)
        reject_count = sum(1 for vote in votes.values() if vote == VoteResult.REJECT.value)
        
        # Simple majority wins
        if approve_count > reject_count:
            return True
        elif reject_count > approve_count:
            return False
        else:
            # Tie - orchestrator vote decides
            gm_vote = votes.get(AgentRole.GENERAL_MANAGER.value)
            return gm_vote == VoteResult.APPROVE.value
    
    def _add_chat_message(self, agent: str, msg_type: str, content: str, task_id: str = None, vote_result: str = None):
        """
        Add message to chat history for transparency
        """
        message = ChatMessage(
            timestamp=datetime.utcnow().isoformat(),
            agent=agent,
            message_type=msg_type,
            content=content,
            task_id=task_id,
            vote_result=vote_result
        )
        self.chat_history.append(message)
        logging.info(f"💬 [{agent}] {msg_type.upper()}: {content[:100]}...")
    
    # Simplified AI integration methods (would call DeepSeek R1 in production)
    async def _gm_design_action_plan(self, prompt: str, context: Dict) -> str:
        return f"Action Plan for Grant: {prompt[:100]}... - Comprehensive strategy with research, budget, writing, impact assessment, and networking components."
    
    async def _gm_divide_into_tasks(self, action_plan: str) -> List[str]:
        tasks = [
            "Conduct comprehensive grant opportunity research",
            "Develop detailed project budget with justification", 
            "Write compelling grant proposal narrative",
            "Create impact measurement framework",
            "Identify strategic partnerships and collaborations"
        ]
        
        for i, task_desc in enumerate(tasks):
            task = AgentTask(
                task_id=f"task_{i+1}",
                assigned_to=list(self.agents.keys())[i+1].value,  # Skip GM
                description=task_desc,
                status=TaskStatus.PENDING.value,
                actions=[],
                evaluation_votes={},
                feedback=[]
            )
            self.tasks.append(task)
        
        return tasks
    
    async def _gm_allocate_tasks(self, tasks: List[str]):
        # Tasks already allocated in _gm_divide_into_tasks
        pass
    
    async def _agent_create_plan(self, task: AgentTask) -> str:
        return f"Plan for {task.description}: 1. Research approach 2. Execute analysis 3. Generate deliverable"
    
    async def _agent_execute_actions(self, task: AgentTask) -> str:
        return f"Completed execution for: {task.description} - Professional deliverable ready for review"
    
    async def _agent_self_evaluate(self, task: AgentTask, result: str) -> Dict:
        return {"is_good": True, "confidence": 0.85, "improvement_reason": None}
    
    async def _get_agent_vote(self, agent_role: AgentRole, task: AgentTask) -> tuple:
        # Simplified voting - would use DeepSeek R1 for actual evaluation
        vote = VoteResult.APPROVE.value if "deliverable ready" in task.result else VoteResult.REJECT.value
        feedback = f"Task meets quality standards" if vote == VoteResult.APPROVE.value else "Needs more detail"
        return vote, feedback
    
    async def _gm_synchronize_deliverables(self) -> str:
        completed_tasks = [task for task in self.tasks if task.status == TaskStatus.COMPLETED.value]
        return f"Final Grant Application: Synthesized {len(completed_tasks)} components into comprehensive proposal"
    
    async def _conduct_final_vote(self, synthesis: str) -> Dict[str, str]:
        # All agents vote on final synthesis
        votes = {}
        for agent_role in self.agents:
            votes[agent_role.value] = VoteResult.APPROVE.value  # Simplified
        return votes
    
    async def _gm_improve_synthesis(self, synthesis: str, votes: Dict) -> str:
        return f"Improved {synthesis} based on feedback"

async def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function entry point for multi-agent framework
    """
    logging.info('🤖 Multi-Agent Framework triggered')
    
    try:
        if req.method == 'GET':
            return func.HttpResponse(
                json.dumps({
                    "service": "Multi-Agent Grant Writing Framework", 
                    "status": "ready",
                    "capabilities": [
                        "🎯 General Manager Orchestration",
                        "👥 6 Specialized Agents",
                        "🗳️ Democratic Voting System", 
                        "💬 Transparent Chat Interface",
                        "🔄 Iterative Improvement Loops",
                        "📋 Task Allocation & Tracking"
                    ],
                    "algorithm": "3-Part Process: Orchestration → Execution & Evaluation → Final Synthesis"
                }),
                status_code=200,
                mimetype="application/json"
            )
        
        elif req.method == 'POST':
            req_body = req.get_json()
            
            orchestrator = MultiAgentOrchestrator()
            result = await orchestrator.process_grant_request(
                prompt=req_body.get('prompt', ''),
                context=req_body.get('context', {})
            )
            
            return func.HttpResponse(
                json.dumps(result),
                status_code=200,
                mimetype="application/json"
            )
            
    except Exception as e:
        logging.error(f'❌ Multi-Agent Framework error: {str(e)}')
        return func.HttpResponse(
            json.dumps({
                "error": f"Framework error: {str(e)}",
                "success": False
            }),
            status_code=500,
            mimetype="application/json"
        )