import streamlit as st
import pandas as pd
from datetime import datetime
import os
import time 

# 1. Basic Config
st.set_page_config(page_title="Peer Evaluation", page_icon="👥", layout="wide")

# 3. Data Mapping
GROUP_TOPICS = {
    "Group 01": "Tesla", "Group 02": "Zara", "Group 03": "McDonald’s",
    "Group 04": "Starbucks", "Group 05": "Walmart", "Group 06": "Apple",
    "Group 07": "Amazon", "Group 08": "IKEA", "Group 09": "Coca-Cola",
    "Group 10": "NVIDIA", "Group 11": "Microsoft", "Group 12": "Grab"
}

DIMENSIONS = ["Contribution", "Quality", "Collaboration", "Innovation", "Responsibility"]
DATA_FILE = "evaluation_data.csv"

# 4. Helper Function
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE, dtype={'Evaluator_ID': str, 'Groupmembers_ID': str})
    return pd.DataFrame()

# 5. UI - Header
st.title("👨‍🏫 Group Peer Evaluation System")
st.info("New submissions overwrite previous ones for the same person.")

# 6. Step 1: Evaluator
st.subheader("Step 1: Your Information")
col1, col2 = st.columns(2)
with col1:
    my_id = st.text_input("Your Student ID (Evaluator)").strip()
with col2:
    group_no = st.selectbox("Your Group No.", list(GROUP_TOPICS.keys()))
    st.info(f"Topic: **{GROUP_TOPICS[group_no]}**")

# 7. Step 2: Details
st.write("---")
st.subheader("Step 2: Evaluation Details")
num = st.number_input("How many members (including yourself)?", 1, 12, 1)

all_evals = []
for i in range(int(num)):
    is_self = (i == 0)
    label = f"Member #{i+1} (Your Self-Evaluation)" if is_self else f"Member #{i+1} (Teammate)"
    with st.expander(label, expanded=True):
        t_id = st.text_input(f"Student ID for {label}", key=f"t_id_{i}").strip()
        st.write("Criteria Scoring (0-20):")
        scores = {}
        cols = st.columns(5)
        for idx, name in enumerate(DIMENSIONS):
            with cols[idx]:
                s = st.slider(name, 0, 20, 15, key=f"s_{i}_{idx}")
                scores[name] = s
        
        total = sum(scores.values())
        if total <= 50:
            st.error(f"Current Total: {total}/100 (Justification required! ⚠️)")
        else:
            st.success(f"Current Total: {total}/100")
        
        remark = st.text_area(f"Remarks for {label}", key=f"r_{i}")
        all_evals.append({"id": t_id, "scores": scores, "total": total, "remark": remark})

# 8. Step 3: Submit
st.write("---")
if st.button("🚀 Submit All", use_container_width=True):
    if not my_id:
        st.error("Please enter Your ID!")
    else:
        # Validate remarks for low scores
        valid = True
        for e in all_evals:
            if not e["id"]:
                st.error("Missing Student ID!"); valid = False; break
            if e["total"] <= 50 and not e["remark"].strip():
                st.error(f"Remark required for {e['id']} (Score <= 50)!"); valid = False; break
        
        if valid:
            df = load_data()
            ts = datetime.now().strftime("%Y-%m-%d %H:%M")
            for e in all_evals:
                row = {
                    "Timestamp": ts, "Evaluator_ID": my_id, "Group_No": group_no, 
                    "Topic": GROUP_TOPICS[group_no], "Groupmembers_ID": e["id"], 
                    **e["scores"], "Total_Score": e["total"], "Remarks": e["remark"]
                }
                if not df.empty:
                    mask = (df['Evaluator_ID'] == my_id) & (df['Groupmembers_ID'] == e['id'])
                    df = df[~mask]
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
            
            df.to_csv(DATA_FILE, index=False)
            
            st.balloons()
            st.success("🎉 SUBMISSION SUCCESSFUL! Your evaluations have been recorded.")
            
            time.sleep(6)
            st.rerun()
# 2. Teacher Password
ADMIN_PASSWORD = "123321" 
# 9. Admin Dashboard
st.write("---")
if st.checkbox("Teacher's Dashboard"):
    pwd = st.text_input("Password", type="password")
    if pwd == ADMIN_PASSWORD:
        data = load_data()
        if not data.empty:
            st.write("Average Scores:")
            st.table(data.groupby("Groupmembers_ID")["Total_Score"].mean())
            st.download_button("Download CSV", data.to_csv(index=False).encode('utf-8-sig'), "results.csv")
            
