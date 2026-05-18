import sys
from langchain_core.messages import HumanMessage
from src.graph import build_graph

def main():
    print("🚀 Initializing Multi-Agent Orchestrator with Gemini...")
    graph = build_graph()
    
    print("\n" + "="*50)
    print("📋 ENTER THE RAW DATA OR CONTEXT BELOW:")
    print("(Paste text, then press Enter and Ctrl+D or Ctrl+Z to finish input)")
    print("="*50)
    
    # Read multiline input from clipboard/terminal safely
    try:
        raw_context = sys.stdin.read().strip()
    except Exception:
        print("Error reading input context.")
        return

    if not raw_context:
        print("❌ No data provided. Aborting framework.")
        return

    print("\n" + "="*50)
    user_goal = input("🎯 What is your objective with this data?:\n>> ")
    print("="*50)
    
    # Bundle data and objectives together into the graph initial memory state
    compiled_prompt = f"Context Data:\n{raw_context}\n\nUser Objective:\n{user_goal}"
    
    initial_state = {
        "messages": [HumanMessage(content=compiled_prompt)],
        "next_step": "Supervisor",
        "confidence_score": 1.0,
        "requires_approval": False
    }
    
    print(f"\n[Processing Pipeline Started...]\n" + "-"*50)
    
    # Stream the graph state nodes live as they process
    for event in graph.stream(initial_state):
        for node, state in event.items():
            print(f"\n--- Node Executed: {node} ---")
            if "messages" in state and state["messages"]:
                last_msg = state["messages"][-1]
                sender = getattr(last_msg, 'name', 'System') or 'System'
                print(f"🤖 Output from {sender}:\n{last_msg.content}")

if __name__ == "__main__":
    main()