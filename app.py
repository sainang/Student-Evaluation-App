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
    "Group 01": "Tesla",
    "Group 02": "Zara",
    "Group 03": "McDonald’s",
    "Group 04": "Starbucks",
    "Group 05": "Walmart",
    "Group 06": "Apple",
    "Group 07": "Amazon",
    "Group 08": "IKEA",
    "Group 09": "Coca-Cola",
    "Group 10": "NVIDIA",
    "Group 11": "Microsoft",
    "Group 12": "Grab"
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
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame()

st.title("👨‍🏫 Group Peer Evaluation System")
st.markdown("Assess all your teammates at once. Remark is mandatory if total score ≤ 50.")

# --- Step 1: Evaluator's Info ---
st.subheader("Step 1: Your Information")
col_a, col_b = st.columns(2)
with col_a:
    my_id = st.text_input("Your Student ID (Evaluator)")
with col_b:
    # 学生选择组号
    group_no = st.selectbox("Your Group No.", list(GROUP_TOPICS.keys()))
    # 根据组号自动获取 Topic
    selected_topic = GROUP_TOPICS[group_no]
    st.info(f"Assigned Topic: **{selected_topic}**")

# --- Step 2: Choose how many members to evaluate ---
st.write("---")
st.subheader("Step 2: Evaluate Teammates")
num_members = st.number_input("How many teammates are you evaluating?", min_value=1, max_value=10, value=1)

all_evaluations = []

for i in range(int(num_members)):
    with st.expander(f"Teammate #{i+1}", expanded=True):
        col_id, col_empty = st.columns([1, 2])
        with col_id:
            t_id = st.text_input(f"Student ID of Teammate #{i+1}", key=f"id_{i}")
        
        st.write("Criteria Scoring (0-20):")
        c_scores = {}
        cols = st.columns(5)
        for idx, (display, backend) in enumerate(DIMENSIONS.items()):
            with cols[idx]:
                # 使用滑动条或数字输入，这里沿用 slider 保证体验，或者按你习惯改回 number_input
                score = st.slider(f"{backend}", 0, 20, 15, key=f"score_{i}_{idx}")
                c_scores[backend] = score
        
        total = sum(c_scores.values())
        is_low = (total <= 50)
        
        if is_low:
            st.warning(f"Total Score: {total}/100 - Remark is REQUIRED.")
        else:
            st.success(f"Total Score: {total}/100")
            
        t_remark = st.text_area(f"Remarks for Teammate #{i+1}", key=f"remark_{i}", placeholder="Mandatory if total ≤ 50")
        
        all_evaluations.append({
            "target_id": t_id,
            "scores": c_scores,
            "total": total,
            "remark": t_remark,
            "is_low": is_low
        })

# --- Step 3: Global Submit ---
st.write("---")
if st.button("🚀 Submit All Evaluations", use_container_width=True):
    error_found = False
    if not my_id:
        st.error("Please fill in your Student ID.")
        error_found = True
    
    for idx, eval_item in enumerate(all_evaluations):
        if not eval_item["target_id"]:
            st.error(f"Teammate #{idx+1} is missing a Student ID.")
            error_found = True
        if eval_item["is_low"] and not eval_item["remark"].strip():
            st.error(f"Teammate #{idx+1} needs a mandatory remark (Total ≤ 50).")
            error_found = True
            
    if not error_found:
        new_rows = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        for item in all_evaluations:
            row = {
                "Timestamp": timestamp,
                "Evaluator_ID": my_id,
                "Group_No": group_no,
                "Group_Topic": selected_topic, # 这里自动存入对应的主题
                "Groupmembers_ID": item["target_id"],
                **item["scores"],
                "Total_Score": item["total"],
                "Remarks": item["remark"]
            }
            new_rows.append(row)
        
        df = load_data()
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        
        st.balloons()
        st.success(f"Successfully submitted {len(new_rows)} evaluations for {selected_topic}!")

# --- Admin Dashboard ---
st.write("---")
if st.checkbox("Teacher's Dashboard"):
    pwd = st.text_input("Enter Admin Password", type="password")
    if pwd == ADMIN_PASSWORD:
        data = load_data()
        if not data.empty:
            st.subheader("Real-time Summary")
            summary = data.groupby("Groupmembers_ID")["Total_Score"].mean().reset_index()
            st.dataframe(summary, use_container_width=True)
            
            csv_data = data.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Download All Records (CSV)", csv_data, "final_results.csv", "text/csv")
        else:
            st.info("No data available yet.")
