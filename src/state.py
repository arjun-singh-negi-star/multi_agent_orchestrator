import operator
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    # Tracks the full conversation history. 
    # Annotated with operator.add means new messages are automatically appended to the list
    messages: Annotated[Sequence[BaseMessage], operator.add]
    
    # Tracks which agent or node should execute next (managed by the Supervisor)
    next_step: str
    
    # Tracks the confidence score of the last action (0.0 to 1.0)
    confidence_score: float
    
    # A boolean flag that determines if the workflow needs to halt for Human-in-the-Loop approval
    requires_approval: bool
    