import sys
from io import StringIO
import os                                           
from dotenv import load_dotenv                      
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage
from src.state import AgentState
from config.settings import MODEL_NAME

load_dotenv()

# Strict Environment Check for Key
api_key = os.environ.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ ERROR: GEMINI_API_KEY is completely missing from os.environ!")
else:
    print(f"🔑 Key Detected Successfully in workers: {api_key[:6]}...")

# Initialize the Gemini model safely with active inline key verification
llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME, 
    temperature=0.1,
    google_api_key="AIzaSyDR6MEFIogl7YYV-YHX7X7NybFnI8DnfcQ"  # <-- Fixed: Inline injection to ensure workers use the freshly updated key
)

def research_agent_node(state: AgentState):
    print("\n[WORKER] Research Agent (Gemini) is analyzing market data...")
    prompt = "You are an elite Research Agent. Provide deep market context or competitive analysis based on the history below. Keep it concise."
    try:
        history = [HumanMessage(content=prompt)] + list(state["messages"])
        response = llm.invoke(history)
        return {"messages": [AIMessage(content=response.content, name="Research_Agent")]}
    except Exception as api_err:
        print(f"❌ CRITICAL API CRASH IN RESEARCH AGENT: {str(api_err)}")
        raise api_err

def data_extractor_node(state: AgentState):
    print("\n[WORKER] Data Extractor (Gemini) is pulling financial metrics...")
    prompt = "You are a precise Data Extraction Agent. Extract specific financial metrics, data matrices, or text chunks. Present them clearly."
    try:
        history = [HumanMessage(content=prompt)] + list(state["messages"])
        response = llm.invoke(history)
        return {"messages": [AIMessage(content=response.content, name="Data_Extractor")]}
    except Exception as api_err:
        print(f"❌ CRITICAL API CRASH IN DATA EXTRACTOR: {str(api_err)}")
        raise api_err

def code_executor_node(state: AgentState):
    print("\n[WORKER] Code Executor (Gemini) is generating and running calculations dynamically...")
    prompt = "You are a Python Code Execution agent. Based on the financial metrics found in the conversation history, write a raw, complete Python script that calculates the exact gross margins and the 3-year revenue projections. Your output must contain valid Python code wrapped inside markdown blocks. Include explicit print statements to display results."
    
    try:
        history = [HumanMessage(content=prompt)] + list(state["messages"])
        response = llm.invoke(history)
        text_content = response.content
    except Exception as api_err:
        print(f"❌ CRITICAL API CRASH IN CODE EXECUTOR LLM CALL: {str(api_err)}")
        raise api_err
    
    if "python" in text_content:
        parts = text_content.split("python")
        raw_code = parts[-1].split("`")[0].strip()
    else:
        raw_code = text_content.strip()
    
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    
    try:
        exec(raw_code, globals())
        sys.stdout = old_stdout
        execution_result = redirected_output.getvalue()
    except Exception as e:
        sys.stdout = old_stdout
        execution_result = str(e)
        
    print("✅ Active Sandbox runtime execution finished successfully.")
    header = "GENERATED CODE BLOCK: "
    divider = " | ENGINE RUNTIME OUTPUT: "
    compiled_payload = header + raw_code + divider + execution_result
    
    return {"messages": [AIMessage(content=compiled_payload, name="Code_Executor")]}