import streamlit as st 
from connection import get_session
from sqlalchemy import func
from db_setup import Employee, Attendance
from datetime import datetime
import pandas as pd
import calendar

def mark_attendance(session, employee_name, date, is_present, organization):
    employee = session.query(Employee).filter_by(name=employee_name, organization=organization).first()
    if not employee:
        st.error("Employee not found in the database.")
        return

    attendance_record = session.query(Attendance).filter_by(employee_id=employee.id, date=date).first()

    if attendance_record:
        attendance_record.is_present = is_present
    else:
        attendance_record = Attendance(employee_id=employee.id, date=date, is_present=is_present)
        session.add(attendance_record)

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        st.error(f"Failed to mark attendance: {e}")

def delete_employee(session, employee_name, organization):
    employee = session.query(Employee).filter_by(name=employee_name, organization=organization).first()
    if employee:
        try:
            # Delete all attendance records linked to this employee first
            session.query(Attendance).filter_by(employee_id=employee.id).delete()
            
            # Now delete the employee
            session.delete(employee)
            
            session.commit()
            st.success(f"Deleted employee '{employee_name}' and their attendance records successfully.")
        except Exception as e:
            session.rollback()
            st.error(f"Failed to delete employee: {e}")
    else:
        st.error("Employee not found.")

def refresh_treeview(session, selected_date, organization):
    employees = session.query(Employee).filter_by(organization=organization).all()
    if not employees:
        st.info("No employees found for your organization.")
        return

    attendance_data = []
    for emp in employees:
        attendance = session.query(Attendance).filter_by(employee_id=emp.id, date=selected_date).first()
        status = "Present" if attendance and attendance.is_present else "Absent"
        attendance_data.append([emp.name, emp.department, status])

    df = pd.DataFrame(attendance_data, columns=["Name", "Department", "Attendance"])
    st.dataframe(df)

def attendance_page():
    if not st.session_state.get('is_logged_in', False):
        st.warning("Please login first in 'Login / Sign Up' tab.")
        return

    organization = st.session_state.get('organization')
    if not organization:
        st.error("Organization info missing. Please login again.")
        return

    session = get_session()

    st.title("Attendance Management")

    employees = session.query(Employee).filter_by(organization=organization).all()
    if not employees:
        st.info("No employees found for your organization. Please add employees first.")
        return

    employee_names = [emp.name for emp in employees]
    selected_employee = st.selectbox("Select Employee", employee_names)

    today = datetime.today()
    year = st.selectbox("Select Year", options=[today.year, today.year - 1, today.year - 2], index=0)
    month = st.selectbox("Select Month", options=[
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ], index=today.month - 1)

    month_num = datetime.strptime(str(month), "%B").month

    start_date = datetime(year, month_num, 1).date()
    end_date = (pd.Period(f'{year}-{month_num}').asfreq('M').end_time).date()

    employee = session.query(Employee).filter_by(name=selected_employee, organization=organization).first()
    existing_attendance = session.query(Attendance).filter(
        Attendance.employee_id == employee.id,
        Attendance.date >= start_date,
        Attendance.date <= end_date
    ).all()
    attendance_map = {att.date: att.is_present for att in existing_attendance}

    st.write(f"Mark attendance for **{selected_employee}** in **{month} {year}**")

    st.markdown("""
        <style>
        .attendance-scroll {
            max-height: 280px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
            background-color: rgba(255,255,255,0.9);
            border-radius: 6px;
        }
        .weekend-label {
            color: #888888;
            font-style: italic;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.expander("Expand to mark monthly attendance", expanded=True):
        st.markdown('<div class="attendance-scroll">', unsafe_allow_html=True)

        cal = calendar.Calendar(firstweekday=6)  # Sunday start
        month_days = list(cal.itermonthdates(year, month_num))

        day_names = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        cols = st.columns(7)
        for i, day_name in enumerate(day_names):
            cols[i].markdown(f"**{day_name}**")

        col_index = 0
        for day in month_days:
            col = cols[col_index % 7]
            col_index += 1

            if day.month == month_num:
                is_sunday = day.weekday() == 6  # Only Sunday
                key = f"att_{employee.id}_{day.isoformat()}"
                default_val = attendance_map.get(day, False)

                if is_sunday:
                    col.markdown(f'<span class="weekend-label">{day.day}</span>', unsafe_allow_html=True)
                    col.checkbox("Present", value=False, key=key, disabled=True)
                else:
                    col.checkbox(f"{day.day}", value=default_val, key=key)

                
            else:
                col.markdown(" ")

        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Save Attendance"):
        count = 0
        for day in month_days:
            if day.month != month_num:
                continue
            key = f"att_{employee.id}_{day.isoformat()}"
            is_present = st.session_state.get(key, False)
            mark_attendance(session, selected_employee, day, is_present, organization)
            count += 1
        st.success(f"Attendance saved for {count} days for {selected_employee}.")

    st.subheader("Delete Employee")
    delete_employee_name = st.selectbox("Select Employee to Delete", employee_names, key="delete_emp")

    if st.button("Delete Selected Employee"):
        delete_employee(session, delete_employee_name, organization)

    st.subheader(f"Attendance on Selected Month: {month} {year}")
    refresh_treeview(session, start_date, organization)
