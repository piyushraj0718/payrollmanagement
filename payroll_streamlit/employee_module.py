import streamlit as st
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from connection import engine
from db_setup import Employee, Attendance 

Session = sessionmaker(bind=engine)

def employee_page():
    st.title("Employee Management")

    if not st.session_state.get('is_logged_in', False):
        st.warning("Please login first in 'Login / Sign Up' tab.")
        return

    organization = st.session_state.get('organization')
    if not organization:
        st.error("Organization info missing. Please login again.")
        return

    session = Session()
    employees = session.query(Employee).filter(Employee.organization == organization).all()

    st.subheader(f"Employees in {organization}")

    search_term = st.text_input("Search employees by name").strip().lower()
    filtered_employees = [emp for emp in employees if search_term in emp.name.lower()] if search_term else employees

    if filtered_employees:
        for emp in filtered_employees:
            col1, col2, col3, col4, col5 = st.columns([3, 3, 3, 2, 2])
            col1.write(emp.name)
            col2.write(emp.department)
            col3.write(f"{emp.basic_salary:.2f}")

            if col4.button("Edit", key=f"edit_{emp.id}"):
                st.session_state['edit_employee_id'] = emp.id
                st.rerun()

            delete_key = f"delete_confirm_{emp.id}"
            if delete_key not in st.session_state:
                if col5.button("Delete", key=f"delete_{emp.id}"):
                    st.session_state[delete_key] = True
                    st.rerun()
            else:
                st.warning(f"Confirm delete employee '{emp.name}'?")
                confirm_col, cancel_col = st.columns(2)
                if confirm_col.button("Yes", key=f"confirm_{emp.id}"):
                    try:
                        
                        session.query(Attendance).filter_by(employee_id=emp.id).delete()

                        
                        session.delete(emp)
                        session.commit()

                        st.success(f"Deleted employee '{emp.name}' successfully.")
                    except Exception as e:
                        session.rollback()
                        st.error(f"Failed to delete employee '{emp.name}': {str(e)}")

                    del st.session_state[delete_key]
                    st.rerun()

                if cancel_col.button("No", key=f"cancel_{emp.id}"):
                    del st.session_state[delete_key]
                    st.rerun()
    else:
        st.info("No employees found for your organization.")

    if 'edit_employee_id' in st.session_state:
        emp_id = st.session_state['edit_employee_id']
        emp_to_edit = session.query(Employee).filter(Employee.id == emp_id).first()
        if emp_to_edit:
            st.markdown("---")
            st.subheader(f"Edit Employee: {emp_to_edit.name}")

            with st.form("edit_employee_form"):
                new_name = st.text_input("Employee Name", value=emp_to_edit.name)
                new_department = st.text_input("Department", value=emp_to_edit.department)
                new_basic_salary = st.number_input("Basic Salary", value=emp_to_edit.basic_salary, min_value=0.0, step=100.0)

                submitted = st.form_submit_button("Update")

                if submitted:
                    if not new_name.strip():
                        st.error("Employee name cannot be empty.")
                    elif not new_department.strip():
                        st.error("Department cannot be empty.")
                    elif new_basic_salary <= 0:
                        st.error("Basic salary must be greater than 0.")
                    else:
                        emp_to_edit.name = new_name.strip()
                        emp_to_edit.department = new_department.strip()
                        emp_to_edit.basic_salary = new_basic_salary
                        session.commit()
                        st.success("Employee updated successfully.")
                        del st.session_state['edit_employee_id']
                        st.rerun()

            if st.button("Cancel"):
                del st.session_state['edit_employee_id']
                st.rerun()

    else:
        st.markdown("---")
        st.subheader("Add New Employee")

        with st.form("add_employee_form", clear_on_submit=True):
            name = st.text_input("Employee Name")
            department = st.text_input("Department")
            basic_salary = st.number_input("Basic Salary", min_value=0.0, step=100.0)

            submitted = st.form_submit_button("Add Employee")

            if submitted:
                if not name.strip():
                    st.error("Employee name cannot be empty.")
                elif not department.strip():
                    st.error("Department cannot be empty.")
                elif basic_salary <= 0:
                    st.error("Basic salary must be greater than 0.")
                else:
                    new_employee = Employee(
                        name=name.strip(),
                        department=department.strip(),
                        basic_salary=basic_salary,
                        organization=organization
                    )
                    session.add(new_employee)
                    session.commit()
                    st.success(f"Employee '{name}' added successfully to {department} department.")
                    st.rerun()

    session.close()
