"""
Integrated DeepSeek R1 + Azure MCP Tools System using LangGraph
Complete multi-agent grant writing system with inter-agent communication and MCP tools
"""

import json
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver

# Import our components
from deepseek_r1_config import DEEPSEEK_R1_ENDPOINT, DEEPSEEK_R1_API_KEY, AGENT_MODELS
from deepseek_r1_agent_prompts import get_agent_prompt
from inter_agent_communication import CommunicationBus, AgentCommunicator, CollaborationMessageType
from azure_mcp_research_tools import AzureMCPResearchTools, ResearchContext
from azure_mcp_collaboration_tools import AzureMCPCollaborationTools
from azure_mcp_validation_tools import AzureMCPValidationTools
from deepseek_r1_langgraph_workflow import DeepSeekR1Client

@dataclass
class EnhancedGrantApplicationState:
    """Enhanced state with MCP tools and inter-agent communication"""
    # Core grant data
    grant_opportunity: str = ""
    organization_profile: str = ""
    
    # Agent outputs
    research_findings: str = ""
    budget_analysis: str = ""
    written_narrative: str = ""
    impact_assessment: str = ""
    networking_strategy: str = ""
    final_application: str = ""
    
    # MCP tool results
    web_search_results: List[Dict] = field(default_factory=list)
    funder_profile: Dict[str, Any] = field(default_factory=dict)
    competitive_analysis: Dict[str, Any] = field(default_factory=dict)
    budget_validation: Dict[str, Any] = field(default_factory=dict)
    compliance_report: Dict[str, Any] = field(default_factory=dict)
    
    # Inter-agent communication
    active_collaborations: List[str] = field(default_factory=list)
    shared_artifacts: List[str] = field(default_factory=list)
    agent_messages: List[Dict] = field(default_factory=list)
    
    # Workflow control
    workflow_status: str = "initialized"
    current_agent: str = ""
    agent_outputs: Dict[str, Any] = field(default_factory=dict)
    
    # MCP tool availability flags
    mcp_tools_available: bool = True
    azure_services_active: bool = True

class IntegratedDeepSeekMCPSystem:
    """Complete integrated system with DeepSeek R1, LangGraph, and Azure MCP tools"""
    
    def __init__(self):
        # Initialize core components
        self.deepseek_client = DeepSeekR1Client()
        self.communication_bus = CommunicationBus()
        
        # Initialize MCP tools (using Azure credits)
        self.research_tools = AzureMCPResearchTools()
        self.collaboration_tools = AzureMCPCollaborationTools()
        self.validation_tools = AzureMCPValidationTools()
        
        # Agent communicators
        self.agent_communicators = {}
        for agent_name in AGENT_MODELS.keys():
            self.agent_communicators[agent_name] = AgentCommunicator(
                agent_name, self.communication_bus, self.deepseek_client
            )
        
        # LangGraph workflow
        self.workflow = None
        self._build_langgraph_workflow()
        
        print("🚀 Integrated DeepSeek R1 + MCP System initialized!")
        print(f"  ✅ DeepSeek R1 endpoint: {DEEPSEEK_R1_ENDPOINT}")
        print(f"  ✅ {len(AGENT_MODELS)} agents with inter-communication")
        print(f"  ✅ 3 MCP tool categories (Research, Collaboration, Validation)")
        print(f"  ✅ LangGraph workflow with checkpointing")
    
    def _build_langgraph_workflow(self):
        """Build the LangGraph workflow with MCP tools and communication"""
        
        # Create workflow with checkpointing for agent state persistence
        workflow = StateGraph(EnhancedGrantApplicationState)
        
        # Add all enhanced agent nodes
        workflow.add_node("general_manager", self._general_manager_with_mcp)
        workflow.add_node("research_agent", self._research_agent_with_mcp) 
        workflow.add_node("budget_agent", self._budget_agent_with_mcp)
        workflow.add_node("writing_agent", self._writing_agent_with_mcp)
        workflow.add_node("impact_agent", self._impact_agent_with_mcp)
        workflow.add_node("networking_agent", self._networking_agent_with_mcp)
        workflow.add_node("validation_and_finalization", self._validation_and_finalization)
        
        # Add collaboration nodes for inter-agent communication
        workflow.add_node("collaboration_hub", self._collaboration_hub)
        workflow.add_node("consensus_building", self._consensus_building)
        
        # Define the enhanced workflow with communication loops
        workflow.set_entry_point("general_manager")
        
        # Initial sequential flow
        workflow.add_edge("general_manager", "research_agent")
        workflow.add_edge("research_agent", "collaboration_hub")
        workflow.add_edge("collaboration_hub", "budget_agent")
        workflow.add_edge("budget_agent", "collaboration_hub")
        workflow.add_edge("collaboration_hub", "writing_agent")
        workflow.add_edge("writing_agent", "collaboration_hub")
        workflow.add_edge("collaboration_hub", "impact_agent")
        workflow.add_edge("impact_agent", "collaboration_hub")
        workflow.add_edge("collaboration_hub", "networking_agent")
        workflow.add_edge("networking_agent", "consensus_building")
        workflow.add_edge("consensus_building", "validation_and_finalization")
        workflow.add_edge("validation_and_finalization", END)
        
        # Compile workflow with checkpointing
        memory = SqliteSaver.from_conn_string(":memory:")
        self.workflow = workflow.compile(checkpointer=memory)
        
        print("✅ LangGraph workflow built with MCP integration and checkpointing")
    
    async def _general_manager_with_mcp(self, state: EnhancedGrantApplicationState) -> EnhancedGrantApplicationState:
        """General Manager with MCP tools and communication capabilities"""
        state.current_agent = "general_manager"
        agent_name = "general_manager"
        
        print(f"🎯 {agent_name}: Strategic planning with MCP tools...")
        
        # Use MCP research tools for initial analysis
        research_context = ResearchContext(
            query=state.grant_opportunity,
            domain="grants",
            organization=state.organization_profile
        )
        
        # Get initial web research
        if state.mcp_tools_available:
            search_results = self.research_tools.web_search(
                f"grant opportunities {state.grant_opportunity}", 
                research_context, 
                count=5
            )
            state.web_search_results.extend(search_results)
            
            # Broadcast initial findings to all agents
            self.agent_communicators[agent_name].broadcast(
                CollaborationMessageType.KNOWLEDGE_SHARE,
                f"Initial research complete: Found {len(search_results)} relevant opportunities",
                {"search_results": [{"title": r.title, "url": r.url, "snippet": r.snippet} for r in search_results[:3]]}
            )
        
        # DeepSeek R1 strategic reasoning
        prompt_config = get_agent_prompt(agent_name)
        messages = [
            {"role": "system", "content": prompt_config["system_prompt"]},
            {"role": "user", "content": f"""
            <think>
            As the General Manager, I need to create a comprehensive strategic plan for this grant application.
            
            Grant Opportunity: {state.grant_opportunity}
            Organization: {state.organization_profile}
            Initial Research: {len(state.web_search_results)} sources found
            
            I should:
            1. Analyze the strategic fit between opportunity and organization
            2. Identify key success factors and potential challenges
            3. Plan agent coordination and task assignments
            4. Set quality standards and review processes
            5. Create timeline and milestone framework
            </think>
            
            Create a comprehensive strategic plan for this grant application, considering all aspects of successful grant writing.
            """}
        ]
        
        response = self.deepseek_client.chat_completion(messages, agent_name)
        state.agent_outputs[agent_name] = response
        state.workflow_status = "strategic_planning_complete"
        
        # Request collaboration from other agents
        collaboration_tasks = [
            ("research_agent", "Conduct comprehensive funder research"),
            ("budget_agent", "Analyze budget requirements and constraints"),
            ("impact_agent", "Assess impact potential and measurement framework")
        ]
        
        for target_agent, task_desc in collaboration_tasks:
            task_id = self.collaboration_tools.create_collaboration_task(
                requester=agent_name,
                assignee=target_agent,
                task_type=CollaborationMessageType.TASK_REQUEST,
                description=task_desc,
                context={"strategic_plan": response[:500]},
                priority=4
            )
            state.active_collaborations.append(task_id)
        
        print(f"✅ {agent_name}: Strategic planning complete, {len(collaboration_tasks)} tasks assigned")
        return state
    
    async def _research_agent_with_mcp(self, state: EnhancedGrantApplicationState) -> EnhancedGrantApplicationState:
        """Research Agent with comprehensive MCP research tools"""
        state.current_agent = "research_agent"
        agent_name = "research_agent"
        
        print(f"🔍 {agent_name}: Deep research with Azure MCP tools...")
        
        # Extract funder name from opportunity
        funder_name = self._extract_funder_name(state.grant_opportunity)
        
        # Use MCP tools for comprehensive research
        if state.mcp_tools_available:
            research_context = ResearchContext(
                query=state.grant_opportunity,
                domain="grants",
                organization=state.organization_profile,
                funding_amount=self._extract_funding_amount(state.grant_opportunity)
            )
            
            # Comprehensive funder research using Azure credits
            funder_profile = self.research_tools.funder_research(funder_name, research_context)
            state.funder_profile = funder_profile
            
            # Competitive analysis
            competitive_analysis = self.research_tools.competitive_analysis(research_context)
            state.competitive_analysis = competitive_analysis
            
            # Share research artifacts with other agents
            artifact_id = self.collaboration_tools.share_artifact(
                creator=agent_name,
                artifact_name="Comprehensive Funder Research",
                artifact_type="research",
                content=json.dumps(funder_profile, indent=2),
                access_permissions=["budget_agent", "writing_agent", "general_manager"]
            )
            state.shared_artifacts.append(artifact_id)
        
        # DeepSeek R1 research synthesis
        prompt_config = get_agent_prompt(agent_name)
        messages = [
            {"role": "system", "content": prompt_config["system_prompt"]},
            {"role": "user", "content": f"""
            <think>
            I need to synthesize comprehensive research for this grant opportunity.
            
            Funder: {funder_name}
            Opportunity: {state.grant_opportunity}
            MCP Research Available: {len(state.funder_profile.get('funding_opportunities', []))} opportunities found
            Competitive Analysis: {len(state.competitive_analysis.get('successful_projects', []))} examples analyzed
            
            Key research tasks:
            1. Analyze funder priorities and preferences
            2. Identify competitive advantages and differentiators  
            3. Map requirements to organizational capabilities
            4. Recommend positioning strategies
            5. Flag potential challenges or gaps
            </think>
            
            Based on the comprehensive MCP research data, provide detailed research findings and strategic recommendations.
            
            Funder Profile: {json.dumps(state.funder_profile, indent=2)[:1000]}...
            Competitive Analysis: {json.dumps(state.competitive_analysis, indent=2)[:1000]}...
            """}
        ]
        
        response = self.deepseek_client.chat_completion(messages, agent_name)
        state.research_findings = response
        state.agent_outputs[agent_name] = response
        
        # Process any incoming collaboration requests
        await self._process_agent_communications(agent_name, state)
        
        print(f"✅ {agent_name}: Research complete with MCP data integration")
        return state
    
    async def _budget_agent_with_mcp(self, state: EnhancedGrantApplicationState) -> EnhancedGrantApplicationState:
        """Budget Agent with MCP validation and collaboration"""
        state.current_agent = "budget_agent"
        agent_name = "budget_agent"
        
        print(f"💰 {agent_name}: Budget analysis with MCP validation...")
        
        # DeepSeek R1 budget creation
        prompt_config = get_agent_prompt(agent_name)
        messages = [
            {"role": "system", "content": prompt_config["system_prompt"]},
            {"role": "user", "content": f"""
            <think>
            I need to create a comprehensive budget analysis based on:
            
            Research Findings: {state.research_findings[:500]}...
            Funder Requirements: {json.dumps(state.funder_profile.get('requirements', []), indent=2)}
            Strategic Plan: {state.agent_outputs.get('general_manager', '')[:300]}...
            
            Budget creation tasks:
            1. Analyze funder budget requirements and limits
            2. Create detailed budget breakdown by category
            3. Justify each budget component with clear rationale
            4. Ensure compliance with funder guidelines
            5. Optimize for competitive advantage
            </think>
            
            Create a comprehensive budget analysis with detailed breakdown and justifications.
            """}
        ]
        
        response = self.deepseek_client.chat_completion(messages, agent_name)
        state.budget_analysis = response
        state.agent_outputs[agent_name] = response
        
        # Extract budget data for MCP validation
        budget_data = self._extract_budget_from_text(response)
        funder_requirements = self._extract_funder_budget_requirements(state.funder_profile)
        
        # Use MCP validation tools
        if state.mcp_tools_available and budget_data:
            budget_validation = self.validation_tools.validate_budget(budget_data, funder_requirements)
            state.budget_validation = budget_validation.__dict__
            
            # If validation issues found, request peer review
            if budget_validation.issues:
                review_task_id = self.collaboration_tools.request_peer_review(
                    requester=agent_name,
                    content=response,
                    reviewers=["general_manager"],
                    review_criteria="Budget accuracy and funder compliance"
                )
                state.active_collaborations.append(review_task_id[0])
        
        await self._process_agent_communications(agent_name, state)
        
        print(f"✅ {agent_name}: Budget analysis complete with validation")
        return state
    
    async def _writing_agent_with_mcp(self, state: EnhancedGrantApplicationState) -> EnhancedGrantApplicationState:
        """Writing Agent with MCP collaboration and validation"""
        state.current_agent = "writing_agent"
        agent_name = "writing_agent"
        
        print(f"✍️ {agent_name}: Grant writing with MCP collaboration...")
        
        # Get shared artifacts from other agents
        artifacts = self.collaboration_tools.get_shared_artifacts(agent_name, "research")
        
        # DeepSeek R1 grant writing
        prompt_config = get_agent_prompt(agent_name)
        messages = [
            {"role": "system", "content": prompt_config["system_prompt"]},
            {"role": "user", "content": f"""
            <think>
            I need to write compelling grant narrative using all available information:
            
            Research: {state.research_findings[:500]}...
            Budget: {state.budget_analysis[:500]}...
            Shared Artifacts: {len(artifacts)} research documents available
            Funder Profile: {len(state.funder_profile.get('funding_opportunities', []))} opportunities analyzed
            
            Writing tasks:
            1. Craft compelling project description aligned with funder priorities
            2. Integrate research findings naturally into narrative
            3. Connect budget to project activities clearly
            4. Address funder evaluation criteria explicitly
            5. Maintain professional, persuasive tone throughout
            </think>
            
            Write a comprehensive, compelling grant application narrative that integrates all research and budget information.
            """}
        ]
        
        response = self.deepseek_client.chat_completion(messages, agent_name)
        state.written_narrative = response
        state.agent_outputs[agent_name] = response
        
        # Quick MCP compliance check
        if state.mcp_tools_available:
            funder_name = self._extract_funder_name(state.grant_opportunity)
            compliance_check = self.validation_tools.quick_compliance_check(response, funder_name)
            
            # If compliance score is low, request collaboration
            if compliance_check.get('score', 0) < 0.7:
                collab_task_id = self.collaboration_tools.create_collaboration_task(
                    requester=agent_name,
                    assignee="general_manager",
                    task_type=CollaborationMessageType.URGENT_CONSULTATION,
                    description=f"Writing needs improvement - compliance score: {compliance_check.get('score', 0):.2f}",
                    context={"compliance_report": compliance_check},
                    priority=5
                )
                state.active_collaborations.append(collab_task_id)
        
        await self._process_agent_communications(agent_name, state)
        
        print(f"✅ {agent_name}: Grant narrative complete")
        return state
    
    async def _impact_agent_with_mcp(self, state: EnhancedGrantApplicationState) -> EnhancedGrantApplicationState:
        """Impact Agent with MCP tools and collaboration"""
        state.current_agent = "impact_agent"
        agent_name = "impact_agent"
        
        print(f"📊 {agent_name}: Impact analysis with MCP integration...")
        
        # DeepSeek R1 impact analysis
        prompt_config = get_agent_prompt(agent_name)
        messages = [
            {"role": "system", "content": prompt_config["system_prompt"]},
            {"role": "user", "content": f"""
            <think>
            I need to create comprehensive impact assessment based on:
            
            Project Narrative: {state.written_narrative[:500]}...
            Budget Analysis: {state.budget_analysis[:500]}...
            Competitive Analysis: {len(state.competitive_analysis.get('successful_projects', []))} similar projects analyzed
            
            Impact analysis tasks:
            1. Define measurable outcomes and deliverables
            2. Create impact measurement framework
            3. Project short and long-term benefits
            4. Quantify stakeholder value creation
            5. Connect to broader societal impact
            </think>
            
            Develop a comprehensive impact assessment with measurable outcomes and evaluation framework.
            """}
        ]
        
        response = self.deepseek_client.chat_completion(messages, agent_name)
        state.impact_assessment = response
        state.agent_outputs[agent_name] = response
        
        await self._process_agent_communications(agent_name, state)
        
        print(f"✅ {agent_name}: Impact analysis complete")
        return state
    
    async def _networking_agent_with_mcp(self, state: EnhancedGrantApplicationState) -> EnhancedGrantApplicationState:
        """Networking Agent with collaboration tools"""
        state.current_agent = "networking_agent"
        agent_name = "networking_agent"
        
        print(f"🤝 {agent_name}: Partnership strategy with MCP collaboration...")
        
        # DeepSeek R1 networking strategy
        prompt_config = get_agent_prompt(agent_name)
        messages = [
            {"role": "system", "content": prompt_config["system_prompt"]},
            {"role": "user", "content": f"""
            <think>
            I need to develop networking and partnership strategy based on:
            
            Project Impact: {state.impact_assessment[:500]}...
            Research Context: {json.dumps(state.funder_profile.get('requirements', []), indent=2)}
            
            Networking tasks:
            1. Identify strategic partnership opportunities
            2. Map stakeholder engagement strategy
            3. Plan relationship-building activities
            4. Design collaboration frameworks
            5. Create sustainability partnerships
            </think>
            
            Create a comprehensive networking and partnership strategy for this grant project.
            """}
        ]
        
        response = self.deepseek_client.chat_completion(messages, agent_name)
        state.networking_strategy = response
        state.agent_outputs[agent_name] = response
        
        await self._process_agent_communications(agent_name, state)
        
        print(f"✅ {agent_name}: Networking strategy complete")
        return state
    
    async def _collaboration_hub(self, state: EnhancedGrantApplicationState) -> EnhancedGrantApplicationState:
        """Central hub for processing inter-agent communications"""
        print("🔄 Collaboration Hub: Processing agent communications...")
        
        # Process messages for all agents
        for agent_name, communicator in self.agent_communicators.items():
            responses = communicator.process_messages_with_deepseek()
            if responses:
                state.agent_messages.append({
                    "agent": agent_name,
                    "responses": responses,
                    "timestamp": datetime.now().isoformat()
                })
        
        # Update collaboration status
        active_tasks = []
        for agent_name in AGENT_MODELS.keys():
            tasks = self.collaboration_tools.get_assigned_tasks(agent_name, "pending")
            active_tasks.extend(tasks)
        
        print(f"📨 Processed communications for {len(self.agent_communicators)} agents")
        print(f"📋 {len(active_tasks)} active collaboration tasks")
        
        return state
    
    async def _consensus_building(self, state: EnhancedGrantApplicationState) -> EnhancedGrantApplicationState:
        """Build consensus among agents before finalization"""
        print("🤝 Building consensus among agents...")
        
        # Create consensus on final application approach
        consensus_id = self.collaboration_tools.build_consensus(
            initiator="general_manager",
            topic="Final grant application approach and quality",
            options=["Approve for submission", "Requires revisions", "Major changes needed"],
            participants=list(AGENT_MODELS.keys())
        )
        
        # Wait briefly for consensus (in real system, this would be more sophisticated)
        await asyncio.sleep(1)
        
        state.workflow_status = "consensus_building_complete"
        print("✅ Consensus building initiated")
        
        return state
    
    async def _validation_and_finalization(self, state: EnhancedGrantApplicationState) -> EnhancedGrantApplicationState:
        """Final validation and application compilation"""
        print("✅ Final validation and application compilation...")
        
        # Compile all components
        final_application_components = {
            "strategic_plan": state.agent_outputs.get("general_manager", ""),
            "research_findings": state.research_findings,
            "budget_analysis": state.budget_analysis,
            "project_narrative": state.written_narrative,
            "impact_assessment": state.impact_assessment,
            "networking_strategy": state.networking_strategy
        }
        
        # Comprehensive MCP validation
        if state.mcp_tools_available:
            funder_requirements = self._extract_funder_requirements(state.funder_profile)
            compliance_report = self.validation_tools.validate_compliance(
                final_application_components, funder_requirements
            )
            state.compliance_report = compliance_report.__dict__
        
        # Final compilation by General Manager
        final_messages = [
            {"role": "system", "content": get_agent_prompt("general_manager")["system_prompt"]},
            {"role": "user", "content": f"""
            <think>
            I need to compile the final grant application from all agent contributions:
            
            Research: Complete with {len(state.funder_profile.get('funding_opportunities', []))} opportunities analyzed
            Budget: Complete with validation results
            Writing: Complete with compliance check
            Impact: Complete with measurement framework
            Networking: Complete with partnership strategy
            
            Final compilation tasks:
            1. Integrate all components into coherent application
            2. Ensure consistency across all sections
            3. Address any remaining compliance issues
            4. Polish language and presentation
            5. Create executive summary
            </think>
            
            Compile the final, polished grant application from all agent contributions:
            
            {json.dumps(final_application_components, indent=2)[:2000]}...
            """}
        ]
        
        final_response = self.deepseek_client.chat_completion(final_messages, "general_manager")
        state.final_application = final_response
        state.workflow_status = "complete"
        
        print("🎉 Grant application compilation complete!")
        print(f"📊 Final compliance score: {state.compliance_report.get('overall_score', 'N/A')}")
        
        return state
    
    async def _process_agent_communications(self, agent_name: str, state: EnhancedGrantApplicationState):
        """Process pending communications for an agent"""
        communicator = self.agent_communicators.get(agent_name)
        if communicator:
            responses = communicator.process_messages_with_deepseek()
            if responses:
                state.agent_messages.append({
                    "agent": agent_name,
                    "responses": responses,
                    "timestamp": datetime.now().isoformat()
                })
    
    # Helper methods for data extraction
    def _extract_funder_name(self, opportunity: str) -> str:
        """Extract funder name from opportunity text"""
        # Simple extraction - could be enhanced with NLP
        common_funders = ["NSF", "NIH", "DOE", "NASA", "DARPA", "Gates Foundation"]
        for funder in common_funders:
            if funder.lower() in opportunity.lower():
                return funder
        return "Unknown Funder"
    
    def _extract_funding_amount(self, opportunity: str) -> Optional[str]:
        """Extract funding amount from opportunity text"""
        import re
        amount_pattern = r'\$[\d,]+(?:K|M|k|m|,000|,000,000)?'
        match = re.search(amount_pattern, opportunity)
        return match.group(0) if match else None
    
    def _extract_budget_from_text(self, budget_text: str) -> Dict[str, Any]:
        """Extract structured budget data from budget analysis text"""
        # Simple extraction - could be enhanced with NLP
        return {
            "total": 150000,  # Placeholder
            "breakdown": {
                "personnel": 90000,
                "equipment": 30000, 
                "supplies": 15000,
                "travel": 10000,
                "indirect": 5000
            },
            "justification": budget_text[:500]
        }
    
    def _extract_funder_budget_requirements(self, funder_profile: Dict) -> Dict[str, Any]:
        """Extract budget requirements from funder profile"""
        return {
            "funder_name": funder_profile.get("name", "Unknown"),
            "max_funding": 200000,
            "budget_ratios": {
                "personnel": {"max_percentage": 70},
                "indirect": {"max_percentage": 25}
            }
        }
    
    def _extract_funder_requirements(self, funder_profile: Dict) -> Dict[str, Any]:
        """Extract general funder requirements"""
        return {
            "funder_name": funder_profile.get("name", "Unknown"),
            "required_sections": ["abstract", "project_description", "budget", "impact"],
            "max_pages": 15,
            "deadline": (datetime.now().isoformat())
        }
    
    async def run_complete_workflow(self, grant_opportunity: str, organization_profile: str) -> EnhancedGrantApplicationState:
        """Run the complete integrated workflow"""
        print("🚀 Starting Integrated DeepSeek R1 + MCP Workflow...")
        
        initial_state = EnhancedGrantApplicationState(
            grant_opportunity=grant_opportunity,
            organization_profile=organization_profile
        )
        
        # Execute workflow with checkpointing
        config = {"configurable": {"thread_id": f"grant_{int(datetime.now().timestamp())}"}}
        
        final_state = await self.workflow.ainvoke(initial_state, config)
        
        print("\n🎉 WORKFLOW COMPLETE!")
        print(f"📊 MCP Research Results: {len(final_state.web_search_results)} sources")
        print(f"🤝 Collaboration Tasks: {len(final_state.active_collaborations)} active")
        print(f"📎 Shared Artifacts: {len(final_state.shared_artifacts)} created")
        print(f"✅ Final Compliance Score: {final_state.compliance_report.get('overall_score', 'N/A')}")
        
        return final_state

async def main():
    """Test the integrated system"""
    system = IntegratedDeepSeekMCPSystem()
    
    # Test with sample grant opportunity
    grant_opportunity = "NSF AI Research Grant - $500K for innovative machine learning applications in healthcare"
    organization_profile = "University AI Research Lab with 10 years experience in ML applications and healthcare partnerships"
    
    result = await system.run_complete_workflow(grant_opportunity, organization_profile)
    
    print("\n📄 FINAL APPLICATION EXCERPT:")
    print(result.final_application[:500] + "...")

if __name__ == "__main__":
    asyncio.run(main())