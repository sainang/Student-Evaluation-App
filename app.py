import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Page Configuration ---
st.set_page_config(page_title="Group Peer Evaluation", page_icon="👥", layout="wide")

# --- Security: Set your new password here ---
ADMIN_PASSWORD = "YourNewSecurePassword789" 

# --- Group & Topic Data ---
GROUP_TOPICS = {
    "Group 01": "Tesla", "Group 02": "Zara", "Group 03": "McDonald’s",
    "Group 04": "Starbucks", "Group 05": "Walmart", "Group 06": "Apple",
    "Group 07": "Amazon", "Group 08": "IKEA", "Group 09": "Coca-Cola",
    "Group 10": "NVIDIA", "Group 11": "Microsoft", "Group 12": "Grab"
}

# --- Mapping: Criteria ---
DIMENSIONS = {
    "Criterion 1 Contribution & Participation": "Crit1_Contribution",
    "Criterion 2 Professionalism & Quality": "Crit2_Quality",
    "Criterion 3 Collaboration & Communication": "Crit3_Collaboration",
    "Criterion 4 Innovation & Critical Thinking": "Crit4_Innovation",
    "Criterion 5 Responsibility & Leadership": "Crit5_Responsibility"
}

DATA_FILE = "evaluation_data.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE, encoding='utf-8')
    return pd.DataFrame()

st.title("👨‍🏫 Group Peer Evaluation System")
st.markdown("Assess your teammates and yourself. **Scores update in real-time.**")

# --- Step 1: Evaluator's Info ---
st.subheader("Step 1: Your Information")
col_a, col_b = st.columns(2)
with col_a:
    my_id = st.text_input("Your Student ID (Evaluator)")
with col_b:
    group_no = st.selectbox("Your Group No.", list(GROUP_TOPICS.keys()))
    selected_topic = GROUP_TOPICS[group_no]
    st.info(f"Assigned Topic: **{selected_topic}**")

# --- Step 2: Evaluation Details ---
st.write("---")
st.subheader("Step 2: Evaluation Details")

num_members = st.number_input(
    "How many group members (including yourself) are you evaluating?", 
    min_value=1, max_value=12, value=1
)

all_evaluations = []

for i in range(int(num_members)):
    if i == 0:
        label = f"Member #{i+1} (Your Self-Evaluation)"
    else:
        label = f"Member #{i+1} (Teammate Evaluation)"
        
    with st.expander(label, expanded=True):
        col_id, _ = st.columns([1, 2])
        with col_id:
            t_id = st.text_input(f"Student ID for {label}", key=f"id_{i}")
        
        st.write("Criteria Scoring (0-20):")
        c_scores = {}
        cols = st.columns(5)
        
        for idx, (display, backend) in enumerate(DIMENSIONS.items()):
            with cols[idx]:
                score = st.slider(f"{backend}", 0, 20, 15, key=f"score_{i}_{idx}")
                c_scores[backend] = score
        
        member_total = sum(c_scores.values())
        
        # --- Real-time Logic: Remark and justification required for score <= 50 ---
        if member_total <= 50:
            st.error(f"**Current Total: {member_total}/100** (Remark and justification are required for scores ≤ 50! ⚠️)")
        else:
            st.success(f"**Current Total: {member_total}/100**")
            
        t_remark = st.text_area(f"Remarks for {label}", key=f"remark_{i}", 
                                placeholder="If total score is ≤ 50, you must provide a detailed justification here.")
        
        all_evaluations.append({
            "target_id": t_id, "scores": c_scores, "total": member_total, "remark": t_remark
        })

# --- Step 3: Global Submit ---
st.write("---")
if st.button("🚀 Submit All Evaluations", use_container_width=True):
    error_found = False
    
    if not my_id:
        st.error("Please enter Your Student ID in Step 1.")
        error_found = True
    
    for idx, item in enumerate(all_evaluations):
        if not item["target_id"]:
            st.error(f"Student ID for Member #{idx+1} is missing.")
            error_found = True
        if item["total"] <= 50 and not item["remark"].strip():
            st.error(f"Submission failed: Member #{idx+1} has a score ≤ 50. A remark and justification are mandatory.")
            error_found = True
            
    if not error_found:
        new_rows = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        for item in all_evaluations:
            new_rows.append({
                "Timestamp": timestamp,
                "Evaluator_ID": my_id,
                "Group_No": group_no,
                "Group_Topic": selected_topic,
                "Groupmembers_ID": item["target_id"],
                **item["scores"],
                "Total_Score": item["total"],
                "Remarks": item["remark"]
            })
        
        df = load_data()
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        
        st.balloons()
        st.success(f"Successfully submitted all evaluations! Dashboard updated.")
        st.rerun()

# --- Admin Dashboard ---
st.write("---")
if st.checkbox("Teacher's Dashboard"):
    pwd = st.text_input("Enter Admin Password", type="password")
    if pwd == ADMIN_PASSWORD:
        data = load_data()
        if not data.empty:
            st.subheader("Real-time Summary")
            summary = data.groupby("Groupmembers_ID")["Total_Score"].mean().reset_index()
            summary.columns = ["Student ID", "Average Score"]
            st.dataframe(summary, use_container_width=True)
            
            st.write("Recent Submissions (Last 10):")
            st.dataframe(data.tail(10), use_container_width=True)
            
            csv_data = data.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Download Final Results (CSV)", csv_data, "evaluation_results.csv", "text/csv")
        else:
            st.info("No records found yet.")
