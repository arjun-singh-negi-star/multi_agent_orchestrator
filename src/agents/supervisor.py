import os
from pydantic import BaseModel, Field
from typing import Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from src.state import AgentState
from config.settings import MODEL_NAME, SUPERVISOR_PROMPT

class SupervisorRouter(BaseModel):
    next_step: Literal["Research_Agent", "Data_Extractor", "Code_Executor", "Human_Review", "FINISH"] = Field(
        description="The next node to route the workflow to based on the current state."
    )
    confidence_score: float = Field(
        description="A confidence score from 0.0 to 1.0 assessing the completeness/accuracy of the current progress."
    )
    reasoning: str = Field(description="A brief justification for this routing choice.")

def get_supervisor_node():
    # Forceful environment fetch to prevent dynamic local caching bugs
    active_key = os.environ.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    # Initialize the Gemini model with a direct inline key pass guardrail
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME, 
        temperature=0.1,
        google_api_key="AIzaSyDR6MEFIogl7YYV-YHX7X7NybFnI8DnfcQ"  # <-- Fixed: Inline injection to bypass Windows OS key cache lock
    )
    structured_llm = llm.with_structured_output(SupervisorRouter)
    
    def supervisor_node(state: AgentState):
        messages = [SystemMessage(content=SUPERVISOR_PROMPT)] + list(state["messages"])
        response = structured_llm.invoke(messages)
        
        chosen_step = response.next_step
        
        # 🛡️ ANTI-EARLY-FINISH GUARDRAIL:
        if len(state["messages"]) <= 1 and chosen_step == "FINISH":
            chosen_step = "Data_Extractor"  
            print("\n⚠️ [GUARDRAIL ACTIVATED] Supervisor tried to FINISH too early. Forcing route to Data_Extractor for response generation.")

        requires_approval = response.confidence_score < 0.80
        next_step = "Human_Review" if requires_approval else chosen_step
        
        print(f"\n[SUPERVISOR via Gemini] Next Step: {next_step} | Confidence: {response.confidence_score:.2f} | Reason: {response.reasoning}")
        
        return {
            "next_step": next_step,
            "confidence_score": response.confidence_score,
            "requires_approval": requires_approval
        }
    
    return supervisor_node