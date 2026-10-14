
import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        database="employee_db",
        user="postgres",
        password="shree@8382",
        port=5432
    )

    print("Database connected successfully!")

    cur = conn.cursor()
    cur.execute("SELECT * FROM employee")

    rows = cur.fetchall()

    print("Employee records:")

    for row in rows:
        print(row)

    cur.close()
    conn.close()

except Exception as e:
    print("Error:", e)



