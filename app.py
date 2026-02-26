import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Page Configuration ---
st.set_page_config(page_title="Peer Evaluation", page_icon="👥", layout="wide")

# --- Teacher Dashboard Password ---
ADMIN_PASSWORD = "123321" 

# --- Group & Topic Mapping ---
GROUP_TOPICS = {
    "Group 01": "Tesla", "Group 02": "Zara", "Group 03": "McDonald’s",
    "Group 04": "Starbucks", "Group 05": "Walmart", "Group 06": "Apple",
    "Group 07": "Amazon", "Group 08": "IKEA", "Group 09": "Coca-Cola",
    "Group 10": "NVIDIA", "Group 11": "Microsoft", "Group 12": "Grab"
}

# --- Scoring Criteria ---
DIMENSIONS = {
    "Crit1_Contribution": "Contribution",
    "Crit2_Quality": "Quality",
    "Crit3_Collaboration": "Collaboration",
    "Crit4_Innovation": "Innovation",
    "Crit5_Responsibility": "Responsibility"
}

DATA_FILE = "evaluation_data.csv"

# --- Data Loading ---
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, encoding='utf-8', dtype={'Evaluator_ID': str, 'Groupmembers_ID': str})
        return df
    return pd.DataFrame()

st.title("👨‍🏫 Group Peer Evaluation System")
st.markdown("Scores update in real-time. New submissions overwrite previous ones for the same target.")

# --- Step 1: Evaluator Information ---
st.subheader("Step 1: Your Information")
col_a, col_b = st.columns(2)
with col_a:
    my_id = st.text_input("Your Student ID (Evaluator)").strip()
with col_b:
    group_no = st.selectbox("Your Group No.", list(GROUP_TOPICS.keys()))
    selected_topic = GROUP_TOPICS[group_no]
    st.info(f"Topic: **{selected_topic}**")

# --- Step 2: Evaluation Details ---
st.write("---")
st.subheader("Step 2: Evaluation Details")
num_members = st.number_input("How many group members (including yourself) are you evaluating?", 1, 12, 1)

all_evaluations = []
for i in range(int(num_members)):
    is_self = (i == 0)
    # 更新后的标签文案
    section_label = f"Member #{i+1} (Your Self-Evaluation)" if is_self else f"Member #{i+1} (Teammate Evaluation)"
    
    with st.expander(section_label, expanded=True):
        # 更新后的输入框标签
        t_id = st.text_input(f"Student ID for {section_label}", key=f"id_{i}").strip() 
        
        # 更新后的评分标题
        st.write("Criteria Scoring (0-20):")
        c_scores = {}
        cols = st.columns(5)
        for idx, (backend_id, display_name) in enumerate(DIMENSIONS.items()):
            with cols[idx]:
                score = st.slider(f"{display_name}", 0, 20, 15, key=f"score_{i}_{idx}")
                c_scores[backend_id] = score
        
        member_total = sum(c_scores.values())
        
        # 更新为 "Current Total" 及其强制备注逻辑
        if member_total <= 50:
            st.error(f"**Current Total: {member_total}/100** (Remark and justification are required for scores ≤ 50! ⚠️)")
        else:
            st.success(f"**Current Total: {member_total}/100**")
            
        t_remark = st.text_area(f"Remarks for {section_label}", key=f"remark_{i}", placeholder="If total score is ≤ 50, you must provide a detailed justification here.")
        all_evaluations.append({"target_id": t_id, "scores": c_scores, "total": member_total, "remark": t_remark})

# --- Step 3: Submission ---
st.write("---")
if st.button("🚀 Submit All Evaluations", use_container_width=True):
    if not my_id:
        st.error("Please enter Your Student ID in Step 1.")
    else:
        df = load_data()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        valid_to_submit = True
        new_entries = []

        for item in all_evaluations:
            if not item["target_id"]:
                st.error("One or more Student IDs are missing!")
                valid_to_submit = False
                break
            if item["total"] <= 50 and not item["remark"].strip():
                st.error(f"Submission failed: A remark and justification are mandatory for scores ≤ 50.")
                valid_to_submit = False
                break
                
            new_entries.append({
                "Timestamp": timestamp,
                "Evaluator_ID": str(my_id),
                "Group_No": group_no,
                "Group_Topic": selected_topic,
                "Groupmembers_ID": str(item["target_id"]),
                **item["scores"],
                "Total_Score": item["total"],
                "Remarks": item["remark"]
            })

        if valid_to_submit:
            for entry in new_entries:
                if not df.empty:
                    mask = (df['Evaluator_ID'] == entry['Evaluator_ID']) & \
                           (df['Groupmembers_ID'] == entry['Groupmembers_ID'])
                    if mask.any():
                        df = df[~mask]
                df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
            
            df.to_csv(DATA_FILE, index=False)
            st.balloons()
            st.success("Submitted successfully! Records updated.")
            st.rerun()

# --- Admin Dashboard ---
st.write("---")
if st.checkbox("Teacher's Dashboard"):
    pwd = st.text_input("Enter Admin Password", type="password")
    if pwd == ADMIN_PASSWORD:
        data = load_data()
        if not data.empty:
            st.subheader("Results Summary (Average Score)")
            data['Total_Score'] = pd.to_numeric(data['Total_Score'])
            summary = data.groupby("Groupmembers_ID")["Total_Score"].mean().reset_index()
            summary.columns = ["Student ID", "Average Score"]
            st.table(summary) 
            
            st.write("Full Records:")
            st.dataframe(data)
            st.download_button("📥 Download Final Records (CSV)", data.to_csv(index=False).encode('utf-8-sig'), "evaluation_results.csv")
        else:
            st.info("No data submitted yet.")
