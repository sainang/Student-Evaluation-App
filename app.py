import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Student Peer Evaluation", page_icon="📊")

# Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# --- Mapping: Display Name vs Backend ID (No Spaces for Backend) ---
# We use simple headers for the spreadsheet to avoid 400 errors
DIMENSIONS = {
    "Criterion 1 Contribution & Participation": "Crit1_Contribution",
    "Criterion 2 Professionalism & Quality": "Crit2_Quality",
    "Criterion 3 Collaboration & Communication": "Crit3_Collaboration",
    "Criterion 4 Innovation & Critical Thinking": "Crit4_Innovation",
    "Criterion 5 Responsibility & Leadership": "Crit5_Responsibility"
}

st.title("👨‍🏫 Peer Evaluation System")

with st.form("eval_form", clear_on_submit=True):
    st.subheader("Step 1: Basic Information")
    col1, col2 = st.columns(2)
    with col1:
        my_id = st.text_input("Your Student ID (Evaluator)")
        group_no = st.selectbox("Group No.", [f"Group {i:02d}" for i in range(1, 16)])
    with col2:
        target_id = st.text_input("Groupmembers ID (Being Evaluated)")
        group_topic = st.text_input("Group_Topic Name")

    st.write("---")
    st.subheader("Step 2: Scoring (0-20 per criterion)")
    st.info("💡 Total score is 100. If total score is ≤ 50, a remark is mandatory.")
    
    current_scores = {}
    for display_name, backend_id in DIMENSIONS.items():
        score = st.slider(f"**{display_name}**", 0, 20, 15)
        current_scores[backend_id] = score # Store using the simple ID
            
    total = sum(current_scores.values())
    is_low_total = (total <= 50)
    
    st.markdown(f"### Current Total: :red[{total}] / 100" if is_low_total else f"### Current Total: :blue[{total}] / 100")
    
    remark_label = "Remarks (Mandatory for score ≤ 50)" if is_low_total else "Remarks (Optional)"
    remarks = st.text_area(remark_label)
    
    submit = st.form_submit_button("Submit Evaluation")
    
    if submit:
        if not my_id or not target_id or not group_topic:
            st.error("Please fill in all fields.")
        elif is_low_total and not remarks.strip():
            st.error("A remark is mandatory for score ≤ 50.")
        else:
            try:
                # 1. Prepare data with simple column names
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
                
                # 2. Read existing data (ttl=0 to bypass cache)
                try:
                    df = conn.read(worksheet="Sheet1", ttl=0)
                    updated_df = pd.concat([df, new_entry], ignore_index=True)
                except:
                    # If sheet is empty/new
                    updated_df = new_entry
                
                # 3. Update spreadsheet
                conn.update(worksheet="Sheet1", data=updated_df)
                
                st.success("Submitted successfully!")
                st.balloons()
            except Exception as e:
                st.error(f"Cloud Connection Error: {e}")

# --- Admin Dashboard ---
st.write("---")
if st.checkbox("Teacher's Dashboard"):
    admin_pwd = st.text_input("Password", type="password")
    if admin_pwd == "123456":
        try:
            df = conn.read(worksheet="Sheet1", ttl=0)
            if not df.empty:
                st.subheader("Summary")
                summary = df.groupby("Groupmembers_ID")["Total_Score"].mean().reset_index()
                st.table(summary)
                st.download_button("Download CSV", df.to_csv(index=False).encode('utf-8-sig'), "results.csv")
        except:
            st.warning("Empty or connection issue.")
