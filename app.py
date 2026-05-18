import streamlit as st
import requests

st.set_page_config(page_title="Gemini Multi-Agent Orchestrator", page_icon="🤖", layout="centered")

st.title("🤖 Gemini Multi-Agent Orchestrator")
st.write("Ingest raw data and let the autonomous agent swarm handle the objective.")

# User Inputs
raw_context = st.text_area("📋 ENTER THE RAW DATA OR CONTEXT BELOW:", height=200, placeholder="Paste competitor data, reviews, or logs here...")
user_goal = st.text_input("🎯 What is your objective with this data?:", placeholder="e.g., Find 3 major weaknesses...")

if st.button("🚀 Run Orchestrator Pipeline", type="primary"):
    if not raw_context or not user_goal:
        st.error("Kripya dono fields me data fill karein!")
    else:
        with st.spinner("Agents are collaborating... Please wait..."):
            try:
                # Aapke FastAPI server (server.py) ko hit karega
                payload = {"context_data": raw_context, "objective": user_goal}
                response = requests.post("http://127.0.0.1:8000/api/analyze", json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Analysis Complete!")
                    
                    # Output Display
                    st.subheader("🤖 Final Analysis Summary:")
                    st.write(result.get("final_analysis"))
                    st.info(f"Confidence Score: {result.get('confidence')}")
                else:
                    st.error(f"Server Error: {response.text}")
            except Exception as e:
                st.error(f"Backend se connect nahi ho paya: {str(e)}")