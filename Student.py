import mysql.connector
from tabulate import tabulate
import getpass
from openpyxl import Workbook
from dotenv import load_dotenv
import os

load_dotenv()


class StudentDB():
    
        def __init__(self):          
            self.mydb = mysql.connector.connect(
                host = os.getenv('DB_HOST'),
                user = os.getenv('DB_USER'),
                password = os.getenv('DB_PASSWORD'),
                database = os.getenv('DB_NAME')
            )
            self.cursor = self.mydb.cursor()
            
        def login(self):
             
            attempts = 3
            
            while attempts > 0:
                username = input("Enter the Username:")
                password = getpass.getpass("Enter the Password:")
                
                query = "select user_role from users where username = %s and user_word = %s"
                values = (username, password)
                
                self.cursor.execute(query,values)
                result = self.cursor.fetchone()
                
                
                if result:
                    role = result[0].lower()
                    print(f"{role} login Successfull")
                    return username, role
                else:
                    attempts -= 1
                    print("Invalid Credentials")
            print("Too Many Attempts Check Your Password")
            return None,None
                    
        def show_my_details(self,uname):
            
            try:
                query = "select * from students where student_name = %s"
                self.cursor.execute(query,(uname,))
                record = self.cursor.fetchall()
        
                if record:
                    column = [col[0] for col in self.cursor.description]
                    print(tabulate(record,column,tablefmt='grid'))
                else:
                    print("No Data Found")
        
            except Exception as e:
                print(e ,"\n")   
            
        def get_marks(self,msg):
            
            while True:
                try:
                    mark = int(input(msg))
                    if 0 <= mark <= 100:
                        return mark
                    else:
                        print(f"{mark} is invalid. Enter marks between (0-100).\n")
                except:
                    print("Invalid input! Please enter a number.\n")
        
        def calculate_grade(self,mark):
        
                if mark >= 90:
                    return 'A'
                elif mark >= 80 and mark < 90:
                    return 'B'
                elif mark >= 70 and mark < 80:
                    return 'C'
                elif mark >= 60 and mark <70:
                    return 'D'
                else:
                    return 'Fail'
        
        
        def add_Student(self):
            
            n = int(input("Enter Number of Students:"))
            for i in range(n):
                  print(f"Student -{i+1}")
                  name = input("Enter Student Name:")
                  m1 = self.get_marks("Enter Mark-1:")
                  m2 = self.get_marks("Enter Mark-2:")
                  m3 = self.get_marks("Enter Mark-3:")
                  m4 = self.get_marks("Enter Mark-4:")
                  m5 = self.get_marks("Enter Mark-5:")
              
                  total = m1+m2+m3+m4+m5
              
                  avg = total / 5
              
                  grade = self.calculate_grade(avg)
                  
                  query = "insert into users (username, user_word, user_role) values(%s,%s,%s)"
                  values = (name,'12345','student')
                  self.cursor.execute(query,values)
                  self.mydb.commit()
              
                  query = "insert into students(student_name, subject_1, subject_2, subject_3, subject_4, subject_5,total, average,grade) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                  values = (name, m1, m2, m3, m4, m5, total, avg, str(grade))
              
                  self.cursor.execute(query,values)
            self.mydb.commit()
            print("Data's inserted into the table")
        
        def show_student_table(self):
            
            try:
               
               self.cursor.execute('select * from students')
               record = self.cursor.fetchall()
               column = [col[0] for col in self.cursor.description]
               print(tabulate(record,column,tablefmt='grid'))
        
            except Exception as e:
                print(e)
        
        
        def search_student(self):
            
            name = input("Enter student Name:")
            
            try:
        
                query = "select * from students where student_name = %s"
                self.cursor.execute(query,(name,))
                record = self.cursor.fetchall()
        
                if record:
                    column = [col[0] for col in self.cursor.description]
                    print(tabulate(record,column,tablefmt='grid'))
                else:
                    print("No Student Found \n")
        
            except Exception as e:
                print(e ,"\n")            
        
        def update_student(self):
            
                  try:
                  
                      name = input("Enter Student Name:")
        
                      query = """
                                  select * from students where student_name = %s"""
                      self.cursor.execute(query,(name,))
                      record = self.cursor.fetchone()
        
                      if not record:
                          print("Student Doesn't Exists \n")
                          return
                      
                      m1 = self.get_marks("Enter Mark-1:")
                      m2 = self.get_marks("Enter Mark-2:")
                      m3 = self.get_marks("Enter Mark-3:")
                      m4 = self.get_marks("Enter Mark-4:")
                      m5 = self.get_marks("Enter Mark-5:")
                  
                      total = m1+m2+m3+m4+m5
                  
                      avg = total / 5
        
                      grade = self.calculate_grade(avg)
                  
                      query = """update students set subject_1 = %s, subject_2 = %s, subject_3 = %s, subject_4 = %s, subject_5 = %s,total = %s, average = %s, grade =%s where student_name = %s"""
                      values = (m1, m2, m3, m4, m5,total,avg,grade, name)
                  
                      self.cursor.execute(query,values)
                      self.mydb.commit()
        
                      if self.cursor.rowcount:
                       print("Student's Details Updated Successfully \n") 
                      
                  except Exception as e:
                      print(e)
        
        def delete_student(self):
                
             try:   
            
                name = input("Enter Student Name:")
                query = """
                              select * from students where student_name = %s"""
                self.cursor.execute(query,(name,))
                record = self.cursor.fetchone()
        
                if not record:
                      print("Student Doesn't Exists \n")
                      return
                else:
                    choice = input("Are you sure to Delete the  Student Detail from Table(Y/N):").lower()
                    if choice == 'y':
                            query = "delete from students where student_name = %s"
                            self.cursor.execute(query,(name,))
                            self.mydb.commit()
                    else:
                        print("Deletion Cancelled")
                        return        
        
                if self.cursor.rowcount:
                   print("Student's Details were Deleted")
        
             except Exception as e:
                 print(e)      
        
        def clear_table(self):
        
            try:
                self.cursor.execute("select 1 from students limit 1")
                record = self.cursor.fetchone()
        
                if record:
                        choice = input("Are You Sure to Delete Table(Y/N).").lower()
                        if choice == 'y':
                              self.cursor.execute("truncate table students")
                              self.mydb.commit()
                              print("Table Data's are deleted")
                        else:
                            print("*" * 40)
                            print("\nDeletion Cancelled")      
                else:
                    print("*" * 40)
                    print("\nTable is Already Empty")        
            except Exception as e:
                print(e)    
        
        
        def show_topper(self):
            
            query = """ 
                        select * from students order by total desc limit 1"""
            self.cursor.execute(query)
            record = self.cursor.fetchall()
        
            if record:
                column = [col[0] for col in self.cursor.description]
                print("Topper:")
                print(tabulate(record,column,tablefmt='grid'))
            else:
                print("*" * 30)
                print("\nNo Data Found")    
        
        
        def export(self):
            try:
                
                self.cursor.execute("select * from students")
                records = self.cursor.fetchall()
                
                if not records:
                    print("No Datas to be  Export")
                    return
                
                column = [col[0] for col in self.cursor.description]
                
                wb = Workbook()
                ws = wb.active
                ws.title = "Students Data"
                
                ws.append(column)
                
                for row in records:
                    ws.append(row)
                    
                file_name = 'Student_Detail.xlsx'
                wb.save(file_name)
                
                print("Data Exported Successfully")    
                
            except Exception as e:
                print(e)    
        
        def menu(self):
            
            while True:
                print("=" * 50)
                print("*" * 11, "STUDENT MANAGEMENT SYSTEM", "*" * 11)
                print("=" * 50)
                print("1.Add Student")
                print("2.Show Student Table")
                print("3.Search Student")
                print("4.Update Student")
                print("5.Delete Student")
                print("6.Clear Table")
                print("7.Show Topper")
                print("8.Export All Details")
                print("9.Exit")
                print("=" * 50)
        
                try:
                   choice = int(input("\nEnter input:"))
                   match(choice):
                      case 1:
                          self.add_Student()
                      case 2:
                          self.show_student_table()
                      case 3:
                          self.search_student()
                      case 4:
                          self.update_student()
                      case 5:
                          self.delete_student()    
                      case 6:
                          self.clear_table()
                      case 7:
                          self.show_topper()    
                      case 8:
                          self.export()
                      case 9:
                          break         
                except Exception as e:
                    print(e)         
                     
        def close(self):
            
            self.cursor.close()
            self.mydb.close()

if __name__ == '__main__':
    
    app = StudentDB()
    
    username, role = app.login()
    
    if role == 'admin':
        app.menu()
        
    elif role == 'student':
        while True:
                print("*" * 40)
                print("1.Show My Details")
                print("2.Exit\n")    
                print("*" * 40,"\n")
                
                choice = int(input("Enter your choice: "))
                match(choice):
                    case 1:
                        app.show_my_details(username)
                    case 2:
                        break
    else:
        print("*" * 30)
        print("\nAccess Denied")            
                  
    app.close()        