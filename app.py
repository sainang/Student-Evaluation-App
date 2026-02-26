import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="Student Peer Evaluation", page_icon="📊")

# --- Database Connection (Google Sheets) ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- Mapping of Evaluation Criteria ---
# Keys: Display labels on the web | Values: Column headers in Google Sheets
DIMENSIONS = {
    "Criterion 1 Contribution & Participation": "Criterion 1 Contribution",
    "Criterion 2 Professionalism & Quality": "Criterion 2 Quality",
    "Criterion 3 Collaboration & Communication": "Criterion 3 Collaboration",
    "Criterion 4 Innovation & Critical Thinking": "Criterion 4 Innovation",
    "Criterion 5 Responsibility & Leadership": "Criterion 5 Responsibility"
}

st.title("👨‍🏫 Peer Evaluation System")
st.markdown("Please evaluate your teammates based on the 5 criteria below.")

# --- 1. Student Evaluation Form ---
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
    st.subheader("Step 2: Scoring (0-20 points per criterion)")
    st.info("💡 Total score is 100. If the total evaluated score is ≤ 50, a remark is mandatory.")
    
    current_scores = {}
    
    # Generate sliders dynamically
    for display_name, excel_header in DIMENSIONS.items():
        score = st.slider(f"**{display_name}**", 0, 20, 15)
        current_scores[excel_header] = score
            
    # Calculate Total Score
    total = sum(current_scores.values())
    is_low_total = (total <= 50)
    
    # Color coding for total score
    if is_low_total:
        st.markdown(f"### Current Total: :red[{total}] / 100")
    else:
        st.markdown(f"### Current Total: :blue[{total}] / 100")
    
    # Remark logic: Mandatory if total <= 50
    remark_label = "Remarks (Mandatory: explain why total score is ≤ 50)" if is_low_total else "Remarks (Optional)"
    remarks = st.text_area(remark_label, placeholder="Provide specific feedback here...")
    
    submit = st.form_submit_button("Submit Evaluation")
    
    if submit:
        # Basic validation
        if not my_id or not target_id or not group_topic:
            st.error("Submission Failed: Please fill in IDs and Group_Topic Name.")
        # Remark validation for low scores
        elif is_low_total and not remarks.strip():
            st.error("Submission Failed: A remark is mandatory for a total score of 50 or below.")
        else:
            try:
                # Read existing data from Google Sheets (ttl=0 ensures real-time)
                existing_data = conn.read(worksheet="Sheet1", ttl=0)
                
                # Prepare new entry
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
                
                # Append new data and update the spreadsheet
                updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
                conn.update(worksheet="Sheet1", data=updated_df)
                
                st.success(f"Evaluation for {target_id} submitted successfully!")
                st.balloons()
            except Exception as e:
                st.error(f"Cloud Connection Error: {e}")

# --- 2. Teacher's Admin Dashboard ---
st.write("---")
if st.checkbox("Teacher's Dashboard (Access Data)"):
    admin_pwd = st.text_input("Admin Password", type="password")
    if admin_pwd == "123456": # Default password: Change this as needed
        try:
            # Refresh data from cloud
            df = conn.read(worksheet="Sheet1", ttl=0)
            if not df.empty:
                st.subheader("Individual Results Summary")
                
                # Calculate average scores per student
                summary = df.groupby("Groupmembers_ID")["Total_Score"].mean().reset_index()
                summary.columns = ["Student ID", "Average Score"]
                st.table(summary)
                
                # Download button for the full report
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 Download Full Report (.csv)",
                    data=csv,
                    file_name=f"Peer_Eval_Results_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("The database is currently empty.")
        except:
            st.warning("Database connection failed. Please check your Secret configuration.")
