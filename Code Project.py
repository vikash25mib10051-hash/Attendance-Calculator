import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import json

# Page Configuration
st.set_page_config(page_title="Attendance Calculator", page_icon="🎓", layout="wide")

# Hide Streamlit menu
hide_menu_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display:none;}
</style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

# Initialize session state
if 'timetable' not in st.session_state:
    st.session_state.timetable = {}
if 'subjects' not in st.session_state:
    st.session_state.subjects = {}
if 'exam_date' not in st.session_state:
    st.session_state.exam_date = date.today() + timedelta(days=30)
if 'holidays' not in st.session_state:
    st.session_state.holidays = []
if 'timetable_submitted' not in st.session_state:
    st.session_state.timetable_submitted = False

# Title
# st.markdown("# 🎓 ATTENDANCE CALCULATOR")
st.markdown("<h1 style='color: #FFFFFF;'>🎓 ATTENDANCE CALCULATOR</h1>", unsafe_allow_html=True)
st.markdown("---")

# Helper Functions
def calculate_percentage(attended, total):
    return round((attended / total) * 100, 1) if total > 0 else 0

def parse_timetable(timetable_data):
    """Parse timetable to extract subjects and their schedule"""
    subjects = {}
    for day, slots in timetable_data.items():
        for time, subject in slots.items():
            if subject and subject.strip():
                if subject not in subjects:
                    subjects[subject] = {
                        'days': [],
                        'slots': [],
                        'classes_per_week': 0
                    }
                subjects[subject]['days'].append(day)
                subjects[subject]['slots'].append(f"{day} {time}")
                subjects[subject]['classes_per_week'] += 1
    return subjects

def count_classes_until_exam(subject_schedule, start_date, exam_date, holidays):
    """Count number of classes for a subject until exam date, excluding holidays"""
    days_map = {
        'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 
        'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6
    }
    
    class_count = 0
    current = start_date
    
    while current < exam_date:
        # Skip if it's a holiday
        if current in holidays:
            current += timedelta(days=1)
            continue
            
        # Check if this day has classes for the subject
        day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                   'Friday', 'Saturday', 'Sunday'][current.weekday()]
        
        if day_name in subject_schedule['days']:
            # Count how many classes on this day
            classes_today = subject_schedule['days'].count(day_name)
            class_count += classes_today
        
        current += timedelta(days=1)
    
    return class_count

# Section 1: Timetable Input
with st.expander("📋 TIMETABLE INPUT & SETUP", expanded=True):
    # st.markdown("### 📅 Enter Your Timetable")
    st.markdown("<h3 style='color: #FFE100;'>📅 Enter Your Timetable</h3>", unsafe_allow_html=True)
    st.markdown("*Enter subject names in the time slots when you have classes*")
    
    # Time slots (as shown in image)
    time_slots = [
        "8:30 - 10:00", "10:05 - 11:35", "11:40 - 01:10", "01:15 - 2:45",
        "2:50 - 4:20", "4:25 - 5:55", "6:00 - 7:30"
    ]
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    
    # Create timetable input grid
    timetable_data = {}
    
    # Create header row
    cols = st.columns([2] + [1]*len(time_slots))
    cols[0].markdown("**Day/Time**")
    for i, time in enumerate(time_slots, 1):
        cols[i].markdown(f"**{time}**")
    
    # Create input rows for each day
    for day in days:
        cols = st.columns([2] + [1]*len(time_slots))
        cols[0].markdown(f"**{day}**")
        
        if day not in timetable_data:
            timetable_data[day] = {}
        
        for i, time in enumerate(time_slots, 1):
            key = f"{day}_{time}"
            timetable_data[day][time] = cols[i].text_input(
                label="",
                key=key,
                placeholder="-",
                label_visibility="collapsed"
            )
    
    st.markdown("---")
    
    # Current Attendance Input
    # st.markdown("### 📊 Current Attendance Status")
    st.markdown("<h3 style='color: #FFE100;'>📊 Current Attendance Status</h3>", unsafe_allow_html=True)
    st.markdown("*Enter your current attendance for each subject*")
    
    if st.button("Analyse My Timetable"):
        st.session_state.timetable = timetable_data
        parsed_subjects = parse_timetable(timetable_data)
        
        if parsed_subjects:
            st.session_state.subjects = {}
            for subject, schedule in parsed_subjects.items():
                st.session_state.subjects[subject] = {
                    'schedule': schedule,
                    'attended': 0,
                    'total': 0,
                    'percentage': 0
                }
            st.success(f"Found {len(parsed_subjects)} subjects in your timetable!")
            st.session_state.timetable_submitted = True
            st.rerun()
        else:
            st.error("No subjects found! Please enter at least one subject in the timetable.")
    
    # If timetable is parsed, show attendance input
    if st.session_state.subjects:
        st.markdown("#### Enter Current Attendance:")
        
        cols = st.columns(3)
        col_idx = 0
        
        for subject in st.session_state.subjects:
            with cols[col_idx % 3]:
                st.markdown(f"**{subject}**")
                attended = st.number_input(
                    "Classes Attended",
                    min_value=0,
                    key=f"attended_{subject}",
                    value=st.session_state.subjects[subject].get('attended', 0)
                )
                total = st.number_input(
                    "Total Classes Held",
                    min_value=0,
                    key=f"total_{subject}",
                    value=st.session_state.subjects[subject].get('total', 0)
                )
                
                st.session_state.subjects[subject]['attended'] = attended
                st.session_state.subjects[subject]['total'] = total
                st.session_state.subjects[subject]['percentage'] = calculate_percentage(attended, total)
                
            col_idx += 1
    
    st.markdown("---")
    
    # Exam Date and Holidays
    # st.markdown("### 📆 Holidays & Exams")
    st.markdown("<h3 style='color: #FFE100;'>📆 Holidays & Exams</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Exam Start Date")
        exam_date = st.date_input(
            "When does your exam start?",
            value=st.session_state.exam_date,
            min_value=date.today()
        )
        st.session_state.exam_date = exam_date
        st.info(f"Classes will be counted until: {exam_date - timedelta(days=1)}")
    
    with col2:
        st.markdown("#### Holidays")
        has_holidays = st.radio("Are there any holidays?", ["No", "Yes"])
        
        if has_holidays == "Yes":
            holiday_start = st.date_input("Holiday Start Date", min_value=date.today())
            holiday_end = st.date_input("Holiday End Date", min_value=holiday_start)
            
            if st.button("Add Holiday Period"):
                # Add all dates in the range to holidays
                current = holiday_start
                added_count = 0
                while current <= holiday_end:
                    if current not in st.session_state.holidays:
                        st.session_state.holidays.append(current)
                        added_count += 1
                    current += timedelta(days=1)
                st.success(f"Added {added_count} holiday days")
        
        if st.session_state.holidays:
            st.write(f"Total holidays: {len(st.session_state.holidays)} days")

st.markdown("---")

# Section 2: Subject-wise Analysis (Only show if timetable is submitted)
if st.session_state.timetable_submitted and st.session_state.subjects:
    st.markdown("## 📚 Subject-wise Analysis")
    
    for subject_name, subject_data in st.session_state.subjects.items():
        # Calculate remaining classes
        remaining_classes = count_classes_until_exam(
            subject_data['schedule'],
            date.today() + timedelta(days=1),
            st.session_state.exam_date,
            st.session_state.holidays
        )
        
        current_percentage = subject_data['percentage']
        
        # Determine status and color
        if current_percentage >= 75:
            status = "🟢 SAFE"
            bg_color = "#e8f5e9"
        elif current_percentage >= 60:
            status = "🟡 WARNING"
            bg_color = "#fff9c4"
        else:
            status = "🔴 RISK"
            bg_color = "#ffebee"
        

# Subject container with expander
        with st.expander(f"📊 {subject_name} - Current: {current_percentage}% {status}", expanded=False):
            st.markdown(f"*Classes on: {', '.join(set(subject_data['schedule']['days']))}*")

            
            # A. Current Status
            st.markdown("**A. Current Status**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.write(f"📌 Classes/week: {subject_data['schedule']['classes_per_week']}")
            with col2:
                st.write(f"📌 Current: {current_percentage}%")
            with col3:
                st.write(f"📌 Attended/Total: {subject_data['attended']}/{subject_data['total']}")
            with col4:
                st.write(f"📌 Status: {status}")
            
            st.write(f"📌 Remaining classes till exam: {remaining_classes}")
            
            # B. Future Scenarios
            st.markdown("**B. Future Scenarios**")
            
            total_future = subject_data['total'] + remaining_classes
            attend_all = calculate_percentage(
                subject_data['attended'] + remaining_classes,
                total_future
            )
            bunk_all = calculate_percentage(subject_data['attended'], total_future)
            bunk_today = calculate_percentage(
                subject_data['attended'] + max(0, remaining_classes - 1),
                total_future
            )
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.success(f"✅ **Attend ALL {remaining_classes} classes:**\n\n→ Final: {attend_all}% {'(Safe)' if attend_all >= 75 else '(Risk)'}")
            with col2:
                st.warning(f"⚠️ **Bunk ALL {remaining_classes} classes:**\n\n→ Final: {bunk_all}% {'(Debarred)' if bunk_all < 60 else ''}")
            with col3:
                st.info(f"📅 **Bunk TODAY only:**\n\n→ Final: {bunk_today}%")
            
            # C. Next 5 Classes Projection
            if remaining_classes > 0:
                st.markdown("**C. Next 5 Classes Projection**")
                projection_data = []
                
                for i in range(1, min(6, remaining_classes + 1)):
                    future_percent = calculate_percentage(
                        subject_data['attended'] + i,
                        subject_data['total'] + i
                    )
                    projection_data.append({
                        "After Class": i,
                        "Attendance %": f"{future_percent}%",
                        "Status": "✅" if future_percent >= 75 else ""
                    })
                
                if projection_data:
                    proj_df = pd.DataFrame(projection_data)
                    st.dataframe(proj_df, hide_index=True, use_container_width=True)
            
            # D. Warning if below 75%
            if current_percentage < 75 and remaining_classes > 0:
                st.markdown("**D. Warning/Goal Status**")
                classes_needed = 0
                for i in range(remaining_classes + 1):
                    if calculate_percentage(
                        subject_data['attended'] + i,
                        subject_data['total'] + remaining_classes
                    ) >= 75:
                        classes_needed = i
                        break
                
                if classes_needed > 0:
                    st.error(f"""
                    ⚠️ **ALERT:** Current attendance below 75%  
                    🎯 To reach 75% → Attend at least **{classes_needed}** more classes
                    """)
                else:
                    st.error("⚠️ Cannot reach 75% even by attending all remaining classes")
    
    st.markdown("---")
    
    # Section 3: Custom Goal Calculator
    st.markdown("## 🎯 CUSTOM GOAL CALCULATOR")
    
    # Subject selection
    selected_subject = st.selectbox(
        "Select Subject for Goal Calculation:",
        options=list(st.session_state.subjects.keys())
    )
    
    if selected_subject:
        subject = st.session_state.subjects[selected_subject]
        remaining = count_classes_until_exam(
            subject['schedule'],
            date.today() + timedelta(days=1),
            st.session_state.exam_date,
            st.session_state.holidays
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # st.markdown("### CHECK: Max Bunks")
            st.markdown("<h3 style='color: #F75270;'>CHECK: Max Bunks</h3>", unsafe_allow_html=True)
            target_1 = st.number_input("Target %", 60, 100, 75, key="g1")
            if st.button("Calculate Max Bunks"):
                max_bunks = 0
                for i in range(remaining + 1):
                    future = calculate_percentage(
                        subject['attended'] + (remaining - i),
                        subject['total'] + remaining
                    )
                    if future < target_1:
                        max_bunks = max(0, i - 1)
                        break
                    max_bunks = i
                st.info(f"You can bunk **{max_bunks}** classes maximum")
        
        with col2:
            # st.markdown("### CHECK : To Reach Target")
            st.markdown("<h3 style='color: #F75270;'>CHECK : To Reach Target</h3>", unsafe_allow_html=True)
            target_2 = st.number_input("Want to reach %", 60, 100, 80, key="g2")
            if st.button("Calculate Classes Needed"):
                classes_needed = remaining
                for i in range(remaining + 1):
                    if calculate_percentage(
                        subject['attended'] + i,
                        subject['total'] + remaining
                    ) >= target_2:
                        classes_needed = i
                        break
                st.success(f"Attend **{classes_needed}** more classes")
                can_bunk = remaining - classes_needed
                if can_bunk > 0:
                    st.write(f"OR: You can bunk **{can_bunk}** classes")
        
        with col3:
            # st.markdown("### CHECK: Prediction")
            st.markdown("<h3 style='color: #F75270;'>CHECK: Prediction</h3>", unsafe_allow_html=True)
            classes_to_attend = st.number_input(
                "If I attend next",
                0,
                remaining,
                min(5, remaining),
                key="g3"
            )
            if st.button("Calculate Future %"):
                final = calculate_percentage(
                    subject['attended'] + classes_to_attend,
                    subject['total'] + classes_to_attend
                )
                st.info(f"Your attendance will be **{final}%**")

else:
    st.info("👆 Please fill in your timetable above to see analysis")

st.markdown("---")
st.markdown("<center>Developed By | Prateek Kumar</center>", unsafe_allow_html=True)