from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.agents.supervisor import get_supervisor_node
from src.agents.workers import research_agent_node, data_extractor_node, code_executor_node

# Explicit Human-in-the-Loop function
def human_review_node(state: AgentState):
    print("\n⚠️ [HUMAN-IN-THE-LOOP] A high-risk action or low-confidence step was flagged.")
    print(f"Current System State History length: {len(state['messages'])} messages.")
    
    # In production, this would be a Slack hook webhook or API callback
    user_approval = input("Proceed with system recommendation? (yes/no): ").strip().lower()
    
    if user_approval == "yes":
        print("[HUMAN] Approved. Handing back control to Supervisor.")
        return {"next_step": "FINISH"}
    else:
        print("[HUMAN] Rejected/Terminated execution.")
        return {"next_step": "FINISH"}

# This is the exact function main.py is trying to import
def build_graph():
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("Supervisor", get_supervisor_node())
    workflow.add_node("Research_Agent", research_agent_node)
    workflow.add_node("Data_Extractor", data_extractor_node)
    workflow.add_node("Code_Executor", code_executor_node)
    workflow.add_node("Human_Review", human_review_node)
    
    # Define Core Structural Routing
    workflow.set_entry_point("Supervisor")
    
    # Workers always route back to the Supervisor for evaluation
    workflow.add_edge("Research_Agent", "Supervisor")
    workflow.add_edge("Data_Extractor", "Supervisor")
    workflow.add_edge("Code_Executor", "Supervisor")
    workflow.add_edge("Human_Review", "Supervisor")
    
    # Conditional edge routing driven purely by the Supervisor's structured choice
    workflow.add_conditional_edges(
        "Supervisor",
        lambda state: state["next_step"],
        {
            "Research_Agent": "Research_Agent",
            "Data_Extractor": "Data_Extractor",
            "Code_Executor": "Code_Executor",
            "Human_Review": "Human_Review",
            "FINISH": END
        }
    )
    
    return workflow.compile()
