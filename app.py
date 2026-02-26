import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Page Configuration ---
st.set_page_config(page_title="Peer Evaluation", page_icon="👥", layout="wide")

# --- Security: Get password from Streamlit Secrets ---
# Replace your old hardcoded password with this:
ADMIN_PASSWORD = st.secrets["teacher_password"]

# --- Group & Topic Mapping ---
GROUP_TOPICS = {
    "Group 01": "Tesla", "Group 02": "Zara", "Group 03": "McDonald’s",
    "Group 04": "Starbucks", "Group 05": "Walmart", "Group 06": "Apple",
    "Group 07": "Amazon", "Group 08": "IKEA", "Group 09": "Coca-Cola",
    "Group 10": "NVIDIA", "Group 11": "Microsoft", "Group 12": "Grab"
}

# --- Scoring Dimensions ---
DIMENSIONS = {
    "Crit1_Contribution": "Contribution",
    "Crit2_Quality": "Quality",
    "Crit3_Collaboration": "Collaboration",
    "Crit4_Innovation": "Innovation",
    "Crit5_Responsibility": "Responsibility"
}

DATA_FILE = "evaluation_data.csv"

# --- Data Loading (Force IDs as String) ---
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
    my_id = st.text_input("Your Student ID (Evaluator)").strip() # Auto-trim whitespace
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
    label = f"Member #{i+1} (Self-Eval)" if is_self else f"Member #{i+1} (Teammate)"
    
    with st.expander(label, expanded=True):
        t_id = st.text_input(f"Student ID for {label}", key=f"id_{i}").strip() 
        
        st.write("Scoring (0-20 per item):")
        c_scores = {}
        cols = st.columns(5)
        for idx, backend_id in enumerate(DIMENSIONS.keys()):
            with cols[idx]:
                score = st.slider(f"{DIMENSIONS[backend_id]}", 0, 20, 15, key=f"score_{i}_{idx}")
                c_scores[backend_id] = score
        
        total = sum(c_scores.values())
        if total <= 50:
            st.error(f"**Total: {total}/100** (Remark and justification required! ⚠️)")
        else:
            st.success(f"**Total: {total}/100**")
            
        remark = st.text_area(f"Remarks for {label}", key=f"remark_{i}", placeholder="Mandatory if total score ≤ 50")
        all_evaluations.append({"target_id": t_id, "scores": c_scores, "total": total, "remark": remark})

# --- Step 3: Submission & Overwrite Logic ---
st.write("---")
if st.button("🚀 Submit All Evaluations", use_container_width=True):
    if not my_id:
        st.error("Missing Evaluator ID!")
    else:
        df = load_data()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        valid_to_submit = True
        new_entries = []

        for item in all_evaluations:
            if not item["target_id"]:
                st.error("Missing Member ID!")
                valid_to_submit = False
                break
            if item["total"] <= 50 and not item["remark"].strip():
                st.error(f"Remark needed for {item['target_id']} (Total ≤ 50)!")
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
                    # Match by Evaluator, Group, and Target Member
                    mask = (df['Evaluator_ID'] == entry['Evaluator_ID']) & \
                           (df['Groupmembers_ID'] == entry['Groupmembers_ID'])
                    if mask.any():
                        df = df[~mask] # Remove old record
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
            st.subheader("Results Summary")
            data['Total_Score'] = pd.to_numeric(data['Total_Score'])
            summary = data.groupby("Groupmembers_ID")["Total_Score"].mean().reset_index()
            summary.columns = ["Student ID", "Average Score"]
            st.table(summary) 
            
            st.write("Full Records:")
            st.dataframe(data)
            st.download_button("Download CSV", data.to_csv(index=False).encode('utf-8-sig'), "final_results.csv")
