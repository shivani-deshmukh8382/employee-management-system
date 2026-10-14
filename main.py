
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Employee Management API is running!"}

# Connect to PostgreSQL
def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="employee_db",
        user="postgres",
        password="shree@8382",
        port=5432
    )


# Request body
class Employee(BaseModel):
    name: str
    age: int | None = None
    course: str | None = None


# CREATE: Add a new employee
@app.post("/employees")
def create_employee(employee: Employee):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO employee (name, age, course)
                VALUES (%s, %s, %s)
                RETURNING id, name, age, course
                """,
                (employee.name, employee.age, employee.course)
            )
            result = cur.fetchone()

        conn.commit()
        return result
    except psycopg2.Error:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Database operation failed")
    finally:
        conn.close()


# READ: Get all employees
@app.get("/employees")
def get_employees():
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, name, age, course FROM employee ORDER BY id"
            )
            return cur.fetchall()
    finally:
        conn.close()


# READ: Get employee by ID
@app.get("/employees/{employee_id}")
def get_employee(employee_id: int):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, name, age, course FROM employee WHERE id = %s",
                (employee_id,)
            )
            employee = cur.fetchone()

        if employee is None:
            raise HTTPException(status_code=404, detail="Employee not found")

        return employee
    finally:
        conn.close()


# UPDATE: Update employee
@app.put("/employees/{employee_id}")
def update_employee(employee_id: int, employee: Employee):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                UPDATE employee
                SET name = %s, age = %s, course = %s
                WHERE id = %s
                RETURNING id, name, age, course
                """,
                (employee.name, employee.age, employee.course, employee_id)
            )
            result = cur.fetchone()

        if result is None:
            raise HTTPException(status_code=404, detail="Employee not found")

        conn.commit()
        return result
    finally:
        conn.close()


# DELETE: Delete employee
@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM employee WHERE id = %s RETURNING id",
                (employee_id,)
            )
            deleted = cur.fetchone()

        if deleted is None:
            raise HTTPException(status_code=404, detail="Employee not found")

        conn.commit()
        return {"message": "Employee deleted successfully", "id": deleted[0]}
    finally:
        conn.close()
