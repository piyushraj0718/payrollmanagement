from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    basic_salary = Column(Float, nullable=False)
    organization = Column(String, nullable=False)  # Added organization column

    attendances = relationship("Attendance", back_populates="employee")

    def __repr__(self):
        return f"<Employee(id={self.id}, name={self.name}, department={self.department}, basic_salary={self.basic_salary}, organization={self.organization})>"

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    organization = Column(String, nullable=False)  # Added organization column

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, organization={self.organization})>"

class ContactMessage(Base):
    __tablename__ = 'contact_messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    message = Column(String, nullable=False)

    def __repr__(self):
        return f"<ContactMessage(id={self.id}, name={self.name}, email={self.email})>"

class Attendance(Base):
    __tablename__ = 'attendances'

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    date = Column(Date, nullable=False)
    is_present = Column(Boolean, nullable=False)

    employee = relationship("Employee", back_populates="attendances")

    def __repr__(self):
        return f"<Attendance(id={self.id}, employee_id={self.employee_id}, date={self.date}, is_present={self.is_present})>"