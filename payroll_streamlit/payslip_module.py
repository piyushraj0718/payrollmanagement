import streamlit as st
from sqlalchemy.orm import sessionmaker
from datetime import date, timedelta
from connection import engine
from db_setup import Employee, Attendance
import pandas as pd
import plotly.express as px
import calendar

Session = sessionmaker(bind=engine)

def payslip_page():
    st.title("Generate Payslip")

    if not st.session_state.get('is_logged_in', False):
        st.warning("Please login first in 'Login / Sign Up' tab.")
        return

    organization = st.session_state.get('organization')
    if not organization:
        st.error("Organization info missing. Please login again.")
        return

    session = Session()

    employees = session.query(Employee).filter(Employee.organization == organization).all()
    if not employees:
        st.info("No employees found for your organization.")
        session.close()
        return

    employee_names = [emp.name for emp in employees]
    selected_name = st.selectbox("Select Employee", employee_names)
    selected_emp = next((emp for emp in employees if emp.name == selected_name), None)

    if selected_emp:
        today = date.today()
        year = st.selectbox("Select Year", options=[today.year, today.year - 1, today.year - 2], index=0)

        # Month names and mapping
        month_name_to_number = {name: i for i, name in enumerate(calendar.month_name) if name}
        month_names = list(month_name_to_number.keys())
        selected_month_name = st.selectbox("Select Month", options=month_names, index=today.month - 1)
        month = month_name_to_number[selected_month_name]

        try:
            start_date = date(year, month, 1)
            end_date = date(year + 1, 1, 1) - timedelta(days=1) if month == 12 else date(year, month + 1, 1) - timedelta(days=1)
        except Exception as e:
            st.error(f"Date error: {e}")
            return

        all_dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
        workdays = [d for d in all_dates if d.weekday() < 6]

        attendance_records = session.query(Attendance).filter(
            Attendance.employee_id == selected_emp.id,
            Attendance.date >= start_date,
            Attendance.date <= end_date
        ).all()

        attendance_map = {att.date: att.is_present for att in attendance_records}
        days_present = sum(1 for d in workdays if attendance_map.get(d, False))
        total_workdays = len(workdays)
        attendance_percentage = (days_present / total_workdays) * 100 if total_workdays > 0 else 0

        is_past_month = (year < today.year) or (year == today.year and month < today.month)

        basic_salary = selected_emp.basic_salary
        attendance_ratio = days_present / total_workdays if total_workdays > 0 else 0
        basic_pay = basic_salary * attendance_ratio
        hra = 0.20 * basic_pay
        da = 0.10 * basic_pay
        bonus = 0.05 * basic_salary if attendance_percentage >= 95 else 0

        gross_salary = basic_pay + hra + da + bonus

        penalty_amount = 0
        if is_past_month and attendance_percentage < 75:
            penalty_amount = 0.30 * gross_salary
            gross_salary -= penalty_amount
            st.warning(f"Attendance below 75% for a completed month. Penalty of ₹{penalty_amount:.2f} applied.")

        deductions = 0
        if gross_salary <= 15000:
            tax = 0
        elif gross_salary <= 30000:
            tax = 0.05 * gross_salary
        else:
            tax = 0.10 * gross_salary

        net_salary = gross_salary - tax

        st.markdown("---")
        st.subheader(f"Payslip for {selected_emp.name} - {start_date.strftime('%B %Y')}")
        st.write(f"**Basic Salary (pro-rata):** ₹{basic_pay:.2f}")
        st.write(f"**HRA (20% of Basic):** ₹{hra:.2f}")
        st.write(f"**DA (10% of Basic):** ₹{da:.2f}")
        st.write(f"**Attendance:** {days_present} / {total_workdays} days ({attendance_percentage:.2f}%)")
        st.write(f"**Bonus:** ₹{bonus:.2f}")
        st.write(f"**Deductions:** ₹{deductions:.2f}")
        st.write(f"**Gross Salary:** ₹{gross_salary:.2f}")
        st.write(f"**Tax:** -₹{tax:.2f}")
        st.success(f"**Net Salary (Payable): ₹{net_salary:.2f}**")

        # Plotting
        salary_data = {
            'Component': ['Basic Pay', 'HRA', 'DA', 'Bonus', 'Deductions', 'Tax'],
            'Amount': [basic_pay, hra, da, bonus, deductions, tax]
        }
        df_salary = pd.DataFrame(salary_data)
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

        fig_bar = px.bar(
            df_salary,
            y='Component',
            x='Amount',
            orientation='h',
            text='Amount',
            color='Component',
            color_discrete_sequence=colors,
            title='Salary Breakdown',
            labels={'Amount': 'Amount (₹)', 'Component': 'Salary Components'}
        )
        fig_bar.update_traces(texttemplate='₹%{x:.2f}', textposition='outside')
        fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False, margin=dict(l=120))
        st.plotly_chart(fig_bar, use_container_width=True)

        fig_pie = px.pie(
            df_salary,
            values='Amount',
            names='Component',
            title='Salary Components Distribution',
            color='Component',
            color_discrete_sequence=colors,
            hole=0.3
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    session.close()

