import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Student Peer Evaluation", page_icon="📊")

# --- Mapping: Display Name ---
DIMENSIONS = {
    "Criterion 1 Contribution & Participation": "Crit1_Contribution",
    "Criterion 2 Professionalism & Quality": "Crit2_Quality",
    "Criterion 3 Collaboration & Communication": "Crit3_Collaboration",
    "Criterion 4 Innovation & Critical Thinking": "Crit4_Innovation",
    "Criterion 5 Responsibility & Leadership": "Crit5_Responsibility"
}

st.title("👨‍🏫 Peer Evaluation System")

# We use a local file to store data (Streamlit Cloud persists this during the session)
DATA_FILE = "evaluation_data.csv"

# Function to load data
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame()

with st.form("eval_form", clear_on_submit=True):
    st.subheader("Step 1: Basic Information")
    my_id = st.text_input("Your Student ID (Evaluator)")
    group_no = st.selectbox("Group No.", [f"Group {i:02d}" for i in range(1, 16)])
    target_id = st.text_input("Groupmembers ID (Being Evaluated)")
    group_topic = st.text_input("Group_Topic Name")

    st.write("---")
    st.subheader("Step 2: Scoring (0-20 per criterion)")
    
    current_scores = {}
    for display_name, backend_id in DIMENSIONS.items():
        score = st.slider(f"**{display_name}**", 0, 20, 15)
        current_scores[backend_id] = score
            
    total = sum(current_scores.values())
    is_low_total = (total <= 50)
    st.markdown(f"### Current Total: :red[{total}] / 100" if is_low_total else f"### Current Total: :blue[{total}] / 100")
    
    remarks = st.text_area("Remarks")
    submit = st.form_submit_button("Submit Evaluation")
    
    if submit:
        if not my_id or not target_id or not group_topic:
            st.error("Please fill in all fields.")
        elif is_low_total and not remarks.strip():
            st.error("A remark is mandatory for score ≤ 50.")
        else:
            # Prepare data
            new_entry = pd.DataFrame([{
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Evaluator_ID": my_id,
                "Group_No": group_no,
                "Group_Topic": group_topic,
                "Groupmembers_ID": target_id,
                **current_scores,
                "Total_Score": total,
                "Remarks": remarks
            }])
            
            # Save to local CSV (within Streamlit Cloud)
            df = load_data()
            df = pd.concat([df, new_entry], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            
            st.success("Submitted successfully! Data recorded.")
            st.balloons()

# --- Admin Dashboard ---
st.write("---")
if st.checkbox("Teacher's Dashboard"):
    admin_pwd = st.text_input("Password", type="password")
    if admin_pwd == "123456":
        df = load_data()
        if not df.empty:
            st.subheader("Current Summary")
            summary = df.groupby("Groupmembers_ID")["Total_Score"].mean().reset_index()
            st.table(summary)
            # You can download the data anytime
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Download Final Results", csv, "final_results.csv", "text/csv")
        else:
            st.info("No data yet.")
