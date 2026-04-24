import mysql.connector
from tabulate import tabulate
import getpass
from openpyxl import Workbook
from dotenv import load_dotenv
import os
import hashlib

load_dotenv()


class StudentDB():

    def __init__(self):
        try:
            self.mydb = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )
            self.cursor = self.mydb.cursor()
        except Exception as e:
            print("Database connection failed:", e)

    # ---------------- LOGIN ---------------- #
    def login(self):
        attempts = 3

        while attempts > 0:
            username = input("Enter the Username: ")
            password = getpass.getpass("Enter the Password: ")

            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            query = "SELECT user_role FROM users WHERE username = %s AND user_password = %s"
            self.cursor.execute(query, (username, hashed_password))
            result = self.cursor.fetchone()

            if result:
                role = result[0].lower()
                print(f"{role} login successful")
                return username, role
            else:
                attempts -= 1
                print("Invalid Credentials")

        print("Too many attempts!")
        return None, None

    # ---------------- DISPLAY ---------------- #
    def display(self, record):
        if record:
            column = [col[0] for col in self.cursor.description]
            print(tabulate(record, column, tablefmt='grid'))
        else:
            print("No Data Found")

    # ---------------- MARK INPUT ---------------- #
    def get_marks(self, msg):
        while True:
            try:
                mark = int(input(msg))
                if 0 <= mark <= 100:
                    return mark
                else:
                    print("Enter marks between 0-100")
            except:
                print("Invalid input")

    # ---------------- GRADE ---------------- #
    def calculate_grade(self, avg):
        if avg >= 90:
            return 'A'
        elif avg >= 80:
            return 'B'
        elif avg >= 70:
            return 'C'
        elif avg >= 60:
            return 'D'
        else:
            return 'Fail'

    # ---------------- ADD STUDENT ---------------- #
    def add_student(self):
        try:
            n = int(input("Enter number of students: "))
        except:
            print("Invalid input")
            return

        for i in range(n):
            print(f"\nStudent {i+1}")

            name = input("Enter Student Name: ")

            password = getpass.getpass("Set Password: ")
            confirm = getpass.getpass("Confirm Password: ")

            if password != confirm:
                print("Passwords do not match!")
                return

            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            m1 = self.get_marks("Mark 1: ")
            m2 = self.get_marks("Mark 2: ")
            m3 = self.get_marks("Mark 3: ")
            m4 = self.get_marks("Mark 4: ")
            m5 = self.get_marks("Mark 5: ")

            total = m1 + m2 + m3 + m4 + m5
            avg = total / 5
            grade = self.calculate_grade(avg)

            # Insert into users
            self.cursor.execute(
                "INSERT INTO users (username, user_password, user_role) VALUES (%s,%s,%s)",
                (name, hashed_password, 'student')
            )

            # Insert into students
            self.cursor.execute(
                """INSERT INTO students 
                (student_name, subject_1, subject_2, subject_3, subject_4, subject_5, total, average, grade)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (name, m1, m2, m3, m4, m5, total, avg, grade)
            )

        self.mydb.commit()
        print("Students added successfully!")

    # ---------------- SHOW ---------------- #
    def show_student_table(self):
        self.cursor.execute("SELECT * FROM students")
        self.display(self.cursor.fetchall())

    def search_student(self):
        name = input("Enter student name: ")
        self.cursor.execute("SELECT * FROM students WHERE student_name = %s", (name,))
        self.display(self.cursor.fetchall())

    def show_my_details(self, uname):
        self.cursor.execute("SELECT * FROM students WHERE student_name = %s", (uname,))
        self.display(self.cursor.fetchall())

    # ---------------- UPDATE ---------------- #
    def update_student(self):
        name = input("Enter student name: ")

        self.cursor.execute("SELECT * FROM students WHERE student_name = %s", (name,))
        if not self.cursor.fetchone():
            print("Student not found")
            return

        m1 = self.get_marks("Mark 1: ")
        m2 = self.get_marks("Mark 2: ")
        m3 = self.get_marks("Mark 3: ")
        m4 = self.get_marks("Mark 4: ")
        m5 = self.get_marks("Mark 5: ")

        total = m1 + m2 + m3 + m4 + m5
        avg = total / 5
        grade = self.calculate_grade(avg)

        self.cursor.execute(
            """UPDATE students SET subject_1=%s, subject_2=%s, subject_3=%s,
            subject_4=%s, subject_5=%s, total=%s, average=%s, grade=%s
            WHERE student_name=%s""",
            (m1, m2, m3, m4, m5, total, avg, grade, name)
        )

        self.mydb.commit()
        print("Updated successfully")

    # ---------------- DELETE ---------------- #
    def delete_student(self):
        name = input("Enter student name: ")

        self.cursor.execute("SELECT * FROM students WHERE student_name=%s", (name,))
        if not self.cursor.fetchone():
            print("Student not found")
            return

        confirm = input("Delete? (y/n): ").lower()
        if confirm == 'y':
            self.cursor.execute("DELETE FROM students WHERE student_name=%s", (name,))
            self.mydb.commit()
            print("Deleted successfully")

    # ---------------- TOPPER ---------------- #
    def show_topper(self):
        self.cursor.execute("SELECT * FROM students ORDER BY total DESC LIMIT 1")
        self.display(self.cursor.fetchall())

    # ---------------- EXPORT ---------------- #
    def export(self):
        self.cursor.execute("SELECT * FROM students")
        records = self.cursor.fetchall()

        if not records:
            print("No data")
            return

        wb = Workbook()
        ws = wb.active

        columns = [col[0] for col in self.cursor.description]
        ws.append(columns)

        for row in records:
            ws.append(row)

        wb.save("Student_Detail.xlsx")
        print("Exported successfully")

    # ---------------- MENU ---------------- #
    def menu(self):
        while True:
            print("\n1.Add  2.Show  3.Search  4.Update  5.Delete  6.Topper  7.Export  8.Exit")

            try:
                choice = int(input("Enter choice: "))
            except:
                print("Invalid input")
                continue

            match choice:
                case 1: self.add_student()
                case 2: self.show_student_table()
                case 3: self.search_student()
                case 4: self.update_student()
                case 5: self.delete_student()
                case 6: self.show_topper()
                case 7: self.export()
                case 8: break

    def close(self):
        self.cursor.close()
        self.mydb.close()


# ---------------- MAIN ---------------- #
if __name__ == "__main__":

    app = StudentDB()

    username, role = app.login()

    if role == 'admin':
        app.menu()

    elif role == 'student':
        while True:
            print("\n1.Show My Details  2.Exit")
            choice = int(input("Enter choice: "))
            if choice == 1:
                app.show_my_details(username)
            else:
                break

    else:
        print("Access Denied")

    app.close()
