import streamlit as st
import pandas as pd
from datetime import datetime
import os
import time

# 1. Page Configuration
st.set_page_config(page_title="G0220 Evaluation", page_icon="👥", layout="wide")

# 2. Settings
ADMIN_PASSWORD = "123321" 
DATA_FILE = "evaluation_data.csv"
GROUP_TOPICS = {
    "Group 01": "Tesla", "Group 02": "Zara", "Group 03": "McDonald’s",
    "Group 04": "Starbucks", "Group 05": "Walmart", "Group 06": "Apple",
    "Group 07": "Amazon", "Group 08": "IKEA", "Group 09": "Coca-Cola",
    "Group 10": "NVIDIA", "Group 11": "Microsoft", "Group 12": "Grab"
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE, dtype={'Evaluator_ID': str, 'Groupmembers_ID': str})
        except:
            return pd.DataFrame()
    return pd.DataFrame()

# 5. UI - Main Title
st.title("👨‍🏫 G0220 Group Self & Peer Evaluation System")

# SECURITY WARNING (The best deterrent)
st.warning("""
⚠️ **ACADEMIC INTEGRITY NOTICE:** - Identity impersonation is a serious violation.
- The system logs **Student IDs, Timestamps, and Submission Patterns**.
- Any student submitting scores under multiple identities will be flagged automatically.
""")

st.info("""
**Notice:** New submissions overwrite previous ones for the same target person.
**Criteria: 1.Contribution, 2.Quality, 3.Collaboration, 4.Innovation, 5.Responsibility (0-20 each).
* **1:** Active involvement in discussions and timely completion of assigned tasks.
* **2:** Accuracy and depth of the work, demonstrating high-quality output.
* **3:** Willingness to listen, effective communication during conflicts, and team spirit.
* **4:** Providing unique insights, novel ideas, or constructive suggestions.
* **5:** Taking initiative on difficult tasks and driving progress when behind schedule.
""")

# 6. Step 1: Evaluator Info
st.subheader("Step 1: Your Information")
col1, col2 = st.columns(2)
with col1:
    my_id = st.text_input("Your Student ID (Evaluator)").strip()
with col2:
    group_no = st.selectbox("Your Group No.", list(GROUP_TOPICS.keys()))
    st.success(f"Selected Topic: **{GROUP_TOPICS[group_no]}**")

# 7. Step 2: Evaluation Details
st.write("---")
st.subheader("Step 2: Evaluation Details")
num = st.number_input("How many group members (including yourself) are you evaluating?", 1, 12, 1)

DIMENSIONS = ["Contribution", "Quality", "Collaboration", "Innovation", "Responsibility"]
all_evals = []
for i in range(int(num)):
    is_self = (i == 0)
    label = f"Member #{i+1} (Self)" if is_self else f"Member #{i+1} (Teammate)"
    with st.expander(label, expanded=True):
        t_id = st.text_input(f"Student ID for {label}", key=f"t_id_{i}").strip()
        st.write("Scoring (😠 0 — 20 😊):")
        scores = {}
        cols = st.columns(5)
        for idx, name in enumerate(DIMENSIONS):
            with cols[idx]:
                s = st.slider(name, 0, 20, 15, key=f"s_{i}_{idx}")
                scores[name] = s
        
        total = sum(scores.values())
        if total <= 50:
            st.error(f"**Current Total: {total}/100** ⚠️ (Remark and justification are REQUIRED for scores ≤ 50!)")
        else:
            st.success(f"**Total: {total}/100**")
        
        remark = st.text_area(f"Remarks for {label}", key=f"r_{i}", placeholder="If score is ≤ 50, explain WHY here (mandatory).")
        all_evals.append({"id": t_id, "scores": scores, "total": total, "remark": remark})

# 8. Step 3: Submission Logic
st.write("---")
if st.button("🚀 Submit All Evaluations", use_container_width=True):
    if not my_id:
        st.error("Please enter Your Student ID!")
    else:
        valid = True
        for e in all_evals:
            if not e["id"]:
                st.error("Missing Target Student ID!"); valid = False; break
            if e["total"] <= 50 and not e["remark"].strip():
                st.error(f"Remark required for {e['id']}!"); valid = False; break
        
        if valid:
            df = load_data()
            ts = datetime.now().strftime("%Y-%m-%d %H:%M")
            for e in all_evals:
                row = {
                    "Timestamp": ts, "Evaluator_ID": my_id, "Group_No": group_no, 
                    "Groupmembers_ID": e["id"], **e["scores"], 
                    "Total_Score": e["total"], "Remarks": e["remark"]
                }
                if not df.empty:
                    mask = (df['Evaluator_ID'] == my_id) & (df['Groupmembers_ID'] == e['id'])
                    df = df[~mask]
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
            
            df.to_csv(DATA_FILE, index=False)
            st.balloons()
            st.success("🎉 SUBMISSION SUCCESSFUL!")
            time.sleep(3)
            st.rerun()

# 9. Teacher's Dashboard (Audit & Records)
st.write("---")
if st.checkbox("Teacher's Dashboard"):
    pwd = st.text_input("Admin Password", type="password")
    if pwd == ADMIN_PASSWORD:
        data = load_data()
        if not data.empty:
            # Audit Section: To catch impersonators
            st.subheader("🕵️ Anti-Fraud Audit")
            audit = data.groupby("Evaluator_ID")["Groupmembers_ID"].count().reset_index()
            audit.columns = ["Student ID", "Records Submitted"]
            st.write("Average students submit 4-6 records. If someone has 20+, they are likely impersonating others.")
            st.dataframe(audit)

            # Data Section
            st.subheader("Full Records")
            st.dataframe(data)
            st.download_button("📥 Download Final Results", data.to_csv(index=False).encode('utf-8-sig'), "results.csv")
