from tkinter import *
from tkinter import messagebox
import sqlite3
import time
from tkinter import PhotoImage
import tkinter as tk
import re
import matplotlib.pyplot as plt
import numpy as np
from tkinter import ttk  # Import ttk separately for Combobox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
from tkinter import filedialog
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from collections import defaultdict



root = tk.Tk(   )
root.configure(bg='black')  #for login
root.title("LOGIN / REGISTER")
root.geometry("1000x700")

# Exception handling 
def connect():
    try:
        conn = sqlite3.connect("loginpage.db")
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users(name TEXT,username TEXT,password TEXT)")
        conn.commit()
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Error connecting to database: {e}")
    finally:
        conn.close()


connect()


def fetch_expenses():
    try:
        conn = sqlite3.connect("expenseapp.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM expensetable")
        rows = cur.fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", str(e))

def view():
    try:
        conn = sqlite3.connect("expenseapp.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM expensetable")
        rows = cur.fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", str(e))

def export_to_csv():
    try:
        # Fetch all expense data from the SQLite database
        rows = view()
        
        # Check if there are any expenses to export
        if rows:
            # Ask user for file name and location
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
            
            # Check if user canceled the save dialog
            if not file_path:
                return
            
            # Open the selected file in write mode
            with open(file_path, "w", newline='') as csvfile:
                # Create a CSV writer object
                csvwriter = csv.writer(csvfile)
                
                # Write the header row
                csvwriter.writerow(['ID', 'Item Name', 'Date', 'Cost'])
                
                # Write each row of expense data
                for row in rows:
                    csvwriter.writerow(row)
                    
            # Show a success message
            messagebox.showinfo('Success', f'Expenses exported to {file_path}')
        else:
            messagebox.showinfo('Info', 'No expenses to export')
            
    except Exception as e:
        messagebox.showerror("Error", f"Error exporting expenses: {e}")

def export_to_pdf():
    try:
        # Fetch all expense data from the SQLite database
        rows = view()
        
        # Check if there are any expenses to export
        if rows:
            # Ask user for file name and location
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
            
            # Check if user canceled the save dialog
            if not file_path:
                return
            
            # Create a PDF file
            pdf = SimpleDocTemplate(file_path, pagesize=letter)
            
            # Create a table for expense data
            data = [['ID', 'Item Name', 'Date', 'Cost']]
            for row in rows:
                data.append(row)
            
            # Create a table object and style it
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            # Add table to PDF
            elements = []
            elements.append(Paragraph("Expense Report", getSampleStyleSheet()['Heading1']))
            elements.append(table)
            
            # Generate PDF
            pdf.build(elements)
            
            # Show a success message
            messagebox.showinfo('Success', f'Expenses exported to {file_path}')
        else:
            messagebox.showinfo('Info', 'No expenses to export')
            
    except Exception as e:
        messagebox.showerror("Error", f"Error exporting expenses: {e}")


def user_expenses_graph():
    try:
        conn = sqlite3.connect("expenseapp.db")
        cur = conn.cursor()
        
        # Get expenses for the logged-in user
        cur.execute("SELECT cost FROM expensetable WHERE itemname=?", (profilename,))
        rows = cur.fetchall()
        
        # Close the connection
        conn.close()

        # Extract costs from the rows
        costs = [float(row[0]) for row in rows]

        # Create a pie chart
        plt.figure(figsize=(8, 8))
        plt.pie(costs, labels=costs, autopct='%1.1f%%')
        plt.title('Pie Chart of Expenses')
        plt.legend(costs, title='Costs', loc='upper right')
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        # Display the pie chart
        plt.show()

        # Create a bar chart
        plt.figure(figsize=(10, 6))
        plt.bar(range(len(costs)), costs, tick_label=[f'Item {i+1}' for i in range(len(costs))])
        plt.xlabel('Items')
        plt.ylabel('Cost')
        plt.title('Bar Chart of Expenses')

        # Display the bar chart
        plt.show()

    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Error displaying graphs: {e}")

def viewallusers():
    try:
        conn = sqlite3.connect("loginpage.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        return rows
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Error fetching data from database: {e}")
    finally:
        conn.close()

def is_valid_date(date_str):
    try:
        day, month, year = map(int, date_str.split('-'))
        if day < 1 or day > 31 or month < 1 or month > 12 or year < 1900:
            return False
        if month in [4, 6, 9, 11] and day > 30:
            return False
        if month == 2:
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                if day > 29:
                    return False
            elif day > 28:
                return False
        return True
    except ValueError:
        return False    

def adduser(name, username, password):
    try:
        conn = sqlite3.connect("loginpage.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO users VALUES(?,?,?)", (name, username, password))
        conn.commit()
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Error adding user to database: {e}")
    finally:
        conn.close()

def deleteallusers():
    try:
        conn = sqlite3.connect("loginpage.db")
        cur = conn.cursor()
        cur.execute("DELETE FROM users")
        conn.commit()
        messagebox.showinfo('Successful', 'All users deleted')
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Error deleting users from database: {e}")
    finally:
        conn.close()

def checkuser(username, password):
    try:
        conn = sqlite3.connect("loginpage.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        result = cur.fetchone()
        return result
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Error checking user in database: {e}")
    finally:
        conn.close()

def getusername(username,password):
    try:
        conn=sqlite3.connect("loginpage.db")
        cur=conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?",(username,password))
        result=cur.fetchone()
        global profilename
        if result!=None:
            profilename=result[0]
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Error getting username from database: {e}")
    finally:
        conn.close()

def viewwindow():
    try:
        gui = Toplevel(root)
        gui.title("VIEW ALL USERS")
        gui.geometry("800x700")
        Message(gui, font=("Castellar", 22, "bold"), text="NAME      USERNAME      PASSWORD", width=700).pack()
        
        users = viewallusers()
        
        if users:
            for row in users:
                a = row[0]
                b = row[1]
                c = "*" * len(row[2])
                d = f"{a}         {b}           {c}"
                Message(gui, fg='#6680ff', font=("adobe clean", 25, "bold"), text=d, width=700).pack()
        else:
            Message(gui, font=("adobe clean", 20), text="No users found", width=700).pack()

        Button(gui, text="Exit Window", font=("candara", 15, "bold"), activebackground="#fffa66", 
               activeforeground="red", width=10, command=gui.destroy).pack()
        
    except Exception as e:
        messagebox.showerror("Error", f"Error displaying users: {e}")

def validate_password(password):
    # Password should contain at least 6 characters, one uppercase, one lowercase, one digit, and one special character
    regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$"
    return bool(re.match(regex, password))

def validate_username(username):
    # Username should contain only alphanumeric characters and underscores, and be between 4-20 characters
    return bool(re.match("^[a-zA-Z0-9_]{4,20}$", username))

import re

def validate_password(password):
    # Regex for validating password
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{6,}$"
    return bool(re.match(pattern, password))

def validate_username(username):
    # Regex for validating username
    pattern = r"^[a-zA-Z0-9_]{4,20}$"
    return bool(re.match(pattern, username))

def open_register_window():
    try:
        # Create a new window for registration
        register_window = tk.Toplevel(root)
        register_window.title("Register")
        register_window.configure(bg="black")  # Set background color
        register_window.geometry("500x600")  # Set dimensions (width x height)
        register_window.resizable(False, False)
        
        window_width = 500
        window_height = 600
        label_width = 50
        label_height = 50
        x_center = (window_width - label_width) // 2
        y_center = (window_height - label_height) // 2

        # Create and place labels
        Label(register_window, font=("lucida fax", 30), bg="#B99470", text="Welcome!").place(x=x_center-50, y=y_center-200)
        l6=Label(register_window,font=("comic sans ms",14),bg="#B5C18E",text="Name").place(x=70,y=195)
        l3=Label(register_window,font=("comic sans ms",14),bg="#B5C18E",text="Username").place(x=70,y=243)
        l4=Label(register_window,font=("comic sans ms",14),bg="#B5C18E",text="Password").place(x=70,y=293)
        l5=Label(register_window,font=("comic sans ms",14),bg="#B5C18E",text="Confirm password").place(x=70,y=342)
        b3=Button(register_window,text="Back To Login",font=("candara",15,"bold"),activebackground="#B99470",activeforeground="red",width=12,command=register_window.destroy).place(x=x_center+60,y=450)
        b4=Button(register_window,text="Register",font=("candara",15,"bold"),activebackground="#B99470",activeforeground="red",width=12,command=register).place(x=x_center-100,y=450)
        
        global register_username
        global register_name
        global register_password
        global register_repassword
        global e5
        global e6
        global e3
        global e4

        register_name=StringVar()
        e6=Entry(register_window,font=("adobe clean",14),textvariable=register_name,background='#FFFBDA')
        e6.place(x=250,y=195,height=30,width=200)
        
        register_username=StringVar()
        e3=Entry(register_window,font=("adobe clean",14),textvariable=register_username,background='#FFFBDA')
        e3.place(x=250,y=243,height=30,width=200)
        
        register_password=StringVar()
        e4=Entry(register_window,font=("adobe clean",14),textvariable=register_password, show="*",background='#FFFBDA')
        e4.place(x=250,y=293,height=30,width=200)
        
        register_repassword=StringVar()
        e5=Entry(register_window,font=("adobe clean",14),textvariable=register_repassword, show="*",background='#FFFBDA')
        e5.place(x=250,y=342,height=30,width=200)
        
    except Exception as e:
        messagebox.showerror("Error", f"Error opening registration window: {e}")

def register():
    try:
        a = register_name.get()
        b = register_username.get()
        c = register_password.get()
        d = register_repassword.get()

        if c == d and c != "" and validate_password(c) and a != "" and validate_username(b):
            try:
                adduser(a, b, c)
                messagebox.showinfo(':)', 'Registration Successful')      
            except Exception as e:
                messagebox.showerror("Error", f"Error adding user to database: {e}")
        else:
            if not all([a, b, c, d]):
                messagebox.showinfo('oops something wrong', 'Field should not be empty')
            elif not validate_password(c):
                messagebox.showinfo('oops something wrong', 'Password should contain at least 6 characters, one uppercase, one lowercase, one digit, and one special character')
            elif c != d:
                messagebox.showinfo('oops something wrong', 'Both passwords should be same!')
            elif not validate_username(b):
                messagebox.showinfo('oops something wrong', 'Username should contain only alphanumeric characters and underscores, and be between 4-20 characters')

        e3.delete(0, END)
        e4.delete(0, END)
        e5.delete(0, END)
        e6.delete(0, END)
        
    except Exception as e:
        messagebox.showerror("Error", f"Error registering user: {e}")

        

def login():
    try:
        a = login_username.get()
        b = login_password.get()
        getusername(a, b)   
        if checkuser(a, b) is not None:
            root.destroy()
            appwindow()     
        else:
            e1.delete(0, tk.END)
            e2.delete(0, tk.END)
            messagebox.showinfo('oops something wrong', 'Invalid credentials')
    except Exception as e:
        messagebox.showerror('Error', str(e))


profilename=""
t = 11
def appwindow():
   
    def export_data(export_option):
        if export_option == "Export to CSV":
            export_to_csv()
        elif export_option == "Export to PDF":
            export_to_pdf()

    def on_export_button_click():
        export_option = export_option_var.get()
        export_data(export_option)

    def connect1():
        try:
            conn = sqlite3.connect("expenseapp.db")
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS expensetable(id INTEGER PRIMARY KEY,itemname TEXT,date TEXT,cost TEXT)")
            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()
            
    def plot_graph():
        graph_type = graph_type_var.get()
        if graph_type == "Bar Chart":
            plot_bar_graph(view()).place(x=50,y=380)
        elif graph_type == "Pie Chart":
            plot_pie_chart(view()).place(x=250,y=380)
        elif graph_type == "Line Graph":
            plot_line_graph(view()).place(x=450,y=380)

    def plot_bar_graph(data):
    # Aggregate costs by item name
        item_costs = defaultdict(float)
        
        for row in data:
            item = row[1]
            cost = float(row[3])
            item_costs[item] += cost
        
        # Extract items and aggregated costs
        items = list(item_costs.keys())
        costs = list(item_costs.values())
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(items, costs, alpha=0.8, color=plt.cm.RdYlBu(np.linspace(0.5, 1, len(items))))
        
        # Add data labels on top of bars
        for i, bar in enumerate(bars):
            plt.text(bar.get_x() + bar.get_width()/2 - 0.1, bar.get_height() + 5, f'{costs[i]:.2f}', fontsize=9, ha='center', color='black')
        
        total_cost = sum(costs)
        
        # Add total cost as text on the plot
        plt.text(0.5, 0.95, f'Total Cost: {total_cost:.2f}', fontsize=12, ha='center', transform=plt.gca().transAxes)
        
        plt.xlabel('Items')
        plt.ylabel('Cost')
        plt.title('Bar Graph of Expenses (Aggregated by Item)')
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

    def plot_pie_chart(data):
        # Aggregate costs by item name
        item_costs = defaultdict(float)
        
        for row in data:
            item = row[1]
            cost = float(row[3])
            item_costs[item] += cost
        
        # Extract items and aggregated costs
        items = list(item_costs.keys())
        costs = list(item_costs.values())
        
        # Calculate total cost
        total_cost = sum(costs)
        
        # Calculate percentages
        percentages = [(cost / total_cost) * 100 for cost in costs]
        
        plt.figure(figsize=(8, 8))
        
        # Plot pie chart
        patches, texts, autotexts = plt.pie(costs, labels=items, autopct='%1.1f%%', startangle=140, colors=plt.cm.tab20.colors)
        
        # Add data labels
        for i, (text, autotext) in enumerate(zip(texts, autotexts)):
            autotext.set_color('white')
            autotext.set_fontsize(10)
            text.set_fontsize(10)
            text.set_text(f"{items[i]}: ${costs[i]:.2f} ({percentages[i]:.1f}%)")
        
        plt.title('Pie Chart of Expenses (Aggregated by Item)')
        plt.axis('equal')
        plt.tight_layout()
        plt.show()


    def plot_line_graph(data):
        data.sort(key=lambda x: x[2])  # Sort by date
        
        dates = [row[2] for row in data]
        costs = [float(row[3]) for row in data]
        
        plt.figure(figsize=(12, 6))
        plt.plot(dates, costs, marker='o', linestyle='-')
        plt.xlabel('Date')
        plt.ylabel('Cost')
        plt.title('Line Graph of Expenses Over Time')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


    def insert(itemname, date, cost):
        try:
            conn = sqlite3.connect("expenseapp.db")
            cur = conn.cursor()
            cur.execute("INSERT INTO expensetable VALUES(NULL,?,?,?)", (itemname, date, cost))
            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()

    def view():
        conn=sqlite3.connect("expenseapp.db")
        cur=conn.cursor()
        cur.execute("SELECT * FROM expensetable")
        rows=cur.fetchall()
        conn.commit()
        conn.close()
        return rows
    
    def search(itemname="", date="", cost=""):
        try:
            conn = sqlite3.connect("expenseapp.db")
            cur = conn.cursor()
            cur.execute("SELECT * FROM expensetable WHERE itemname=? OR date=? OR cost=?", (itemname, date, cost))
            rows = cur.fetchall()
            conn.commit()
            return rows
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()

    def delete(id):
        try:
            conn = sqlite3.connect("expenseapp.db")
            cur = conn.cursor()
            cur.execute("DELETE FROM expensetable WHERE id=?", (id,))
            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()
    
    def deletealldata():
        try:
            conn = sqlite3.connect("expenseapp.db")
            cur = conn.cursor()
            cur.execute("DELETE FROM expensetable")
            conn.commit()
            list1.delete(0, tk.END)
            messagebox.showinfo('Successful', 'All data deleted')
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()

    def sumofitems():
        try:
            conn = sqlite3.connect("expenseapp.db")
            cur = conn.cursor()
            cur.execute("SELECT SUM(cost) FROM expensetable")
            sum_value = cur.fetchone()[0]
            list1.delete(0, tk.END)
            a = "YOU SPENT " + str(sum_value)
            messagebox.showinfo('TOTAL SPENT', a)
            conn.commit()
            return sum_value
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()
    
    def insertitems():
        a = exp_itemname.get()
        b = exp_date.get()
        c = exp_cost.get()
        d = c.replace('.', '', 1)
        e = b.count('-')      

        if a == "" or b == "" or c == "":
            messagebox.showinfo("oops something wrong", "Field should not be empty")
        elif len(b) != 10 or e != 2:
            messagebox.showinfo("oops something wrong", "DATE should be in format dd-mm-yyyy")
        elif not d.isdigit():
            messagebox.showinfo("oops something wrong", "Cost should be a number")
        elif not is_valid_date(b):
            messagebox.showinfo("oops something wrong", "Invalid date")
        else:
            insert(a, b, c)
            e1.delete(0, END)
            e2.delete(0, END)
            e3.delete(0, END)
        list1.delete(0, END)


    def viewallitems():
        list1.delete(0,END)
        list1.insert(END,"ID   NAME     DATE      COST")
        for row in view():
            a=str(row[0])
            b=str(row[1])
            c=str(row[2])
            d=str(row[3])
            f= a + "     " + b + "    " + c + "    " + d
            list1.insert(END,f)
    
    def deletewithid():
        list1.delete(0,END)
        a=exp_id.get()
        delete(a)

    def update(id, itemname, date, cost):
        try:
            conn = sqlite3.connect("expenseapp.db")
            cur = conn.cursor()
            cur.execute("UPDATE expensetable SET itemname=?, date=?, cost=? WHERE id=?", (itemname, date, cost, id))
            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()

    
    def search_item():
        list1.delete(0,END)
        list1.insert(END,"ID   NAME     DATE      COST")
        for row in search(exp_itemname.get(),exp_date.get(),exp_cost.get()):
            a=str(row[0])
            b=str(row[1])
            c=str(row[2])
            d=str(row[3])
            f= a + "     " + b + "    " + c + "    " + d
            list1.insert(END,f)
        e1.delete(0,END)
        e2.delete(0,END)
        e3.delete(0,END)
    
    def open_delete_window():
        # Create a new window for delete functionality
        delete_window = tk.Toplevel(gui)
        delete_window.title("Delete Items")
        delete_window.geometry("400x400")
        delete_window.configure(bg='black')
        delete_window.resizable(False , False)
        
        window_width = 400
        window_height = 400
        label_width = 50
        label_height = 50
        x_center = (window_width - label_width) // 2
        y_center = (window_height - label_height) // 2
        
        l4=Label(delete_window,font=("comic sans ms",20),bg="#FFEC9E",text="REMOVE PRODUCTS",height=1, bd=2, relief="solid").place(x=x_center-100,y=20)

        # Create and place widgets for delete functionality
        
        l4=Label(delete_window,font=("comic sans ms",17),bg="#FFCDEA",text="Select ID to delete", bd=2, relief="solid").place(x=50,y=120)
        
        button_delete_with_id = tk.Button(delete_window, text="Delete with ID", font=("georgia", 15), activebackground="#FFCDEA", activeforeground="red", width=12, command=deletewithid)
        button_delete_with_id.place(x=x_center-48, y=190)
        
        button_delete_all_items = tk.Button(delete_window, text="Delete All Items", font=("georgia", 15), activebackground="#FFCDEA", activeforeground="red", width=15, command=deletealldata)
        button_delete_all_items.place(x=x_center-70, y=260)
        
        b= tk.Button(delete_window, text="Back", font=("algerian",15), activebackground="#fffa66", activeforeground="red", width=6, command=delete_window.destroy)
        b.place(x=x_center-30, y=330)

        
        global exp_id
        exp_id=StringVar()
        sb=Spinbox(delete_window, font=("adobe clean",17),from_= 0, to_ = 200,textvariable=exp_id,justify=CENTER)  #justify=CENTER
        sb.place(x=300,y=120,height=35,width=50)
    
    def open_update_window():
        update_window = tk.Toplevel(gui)
        update_window.title("Update Item")
        update_window.geometry("400x450")
        update_window.configure(bg='black')
        update_window.resizable(False, False)
        
        window_width = 400
        window_height = 450
        label_width = 50
        label_height = 50
        x_center = (window_width - label_width) // 2
        y_center = (window_height - label_height) // 2
        
        l4=Label(update_window,font=("comic sans ms",20),bg="#FFEC9E",text="UPDATE LIST",height=1, bd=2, relief="solid").place(x=x_center-80,y=20)
        l1=Label(update_window,font=("comic sans ms",17),bg="#E8EFCF",text="ID").place(x=41,y=120)
        l2=Label(update_window,font=("comic sans ms",17),bg="#E8EFCF",text="Product name").place(x=41,y=170)
        l3=Label(update_window,font=("comic sans ms",17),bg="#E8EFCF",text="Date(dd-mm-yyyy)").place(x=41,y=220)
        l4=Label(update_window,font=("comic sans ms",17),bg="#E8EFCF",text="Cost of product").place(x=41,y=270)
        b6=Button(update_window,text="SAVE",font=("Algeria",15),activebackground="#fffa66",activeforeground="red",width=10,command=updateitem).place(x=75,y=350)
        b7=Button(update_window,text="CLOSE",font=("Algeria",15),activebackground="#fffa66",activeforeground="red",width=10,command=update_window.destroy).place(x=220,y=350)
        # b8 = Button(gui, text="Export to CSV", font=("georgia", 17), activebackground="#fffa66", activeforeground="red", width=15, command=export_to_csv).place(x=550, y=400)
        # b_export_pdf = Button(gui, text="Export to PDF", font=("georgia",17), activebackground="#fffa66", activeforeground="red", width=15, command=export_to_pdf)
        # b_export_pdf.place(x=730, y=650)

        global update_id
        global update_itemname
        global update_date
        global update_cost

        update_id = StringVar()
        update_itemname = StringVar()
        update_date = StringVar()
        update_cost = StringVar()

        e1=Entry(update_window,font=("adobe clean",15),textvariable=update_id,background='#FFFBDA')
        e1.place(x=259,y=120,height=30,width=110)
        e2=Entry(update_window,font=("adobe clean",15),textvariable=update_itemname,background='#FFFBDA')
        e2.place(x=259,y=170,height=30,width=110)
        e3=Entry(update_window,font=("adobe clean",15),textvariable=update_date,background='#FFFBDA')
        e3.place(x=259,y=220,height=30,width=110)
        e4=Entry(update_window,font=("adobe clean",15),textvariable=update_cost,background='#FFFBDA')
        e4.place(x=259,y=270,height=30,width=110)

        b1=Button(update_window,text="Update",font=("georgia",17),activebackground="#FFEC9E")

    def updateitem():
        id = update_id.get()
        itemname = update_itemname.get()
        date = update_date.get()
        cost = update_cost.get()
    
        if id == "" or itemname == "" or date == "" or cost == "":
            messagebox.showinfo("Oops", "All fields are required")
            return
    
        d=cost.replace('.', '', 1)
        e=date.count('-')      

        if len(date) != 10 or e != 2:
            messagebox.showinfo("Oops", "DATE should be in format dd-mm-yyyy")
            return
    
        if d.isdigit() == False:
            messagebox.showinfo("Oops", "Cost should be a number")
            return

        update(id, itemname, date, cost)
        messagebox.showinfo("Success", "Item updated successfully")
        viewallitems()
    

    def endpage():
    # Clear any existing labels
        for widget in gui.winfo_children():
            widget.destroy()

        # Calculate center coordinates for labels
        window_width = 800
        window_height = 700
        label_width = 400
        label_height = 100
        x_center = (window_width - label_width) // 2
        y_center = (window_height - label_height) // 2

        # Create and place labels
        Label(gui, font=("lucida fax", 40), bg="#ECCA9C", text="EXPENSE TRACKER").place(x=x_center, y=y_center-200)
        # Label(gui, font=("lucida fax", 40),height=0.2, bg="black", text="----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------").place(x=0, y=y_center-100)
        # Label(gui, font=("lucida fax", 40),height=0.2, bg="black", text="----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------").place(x=0, y=y_center+180)
        Label(gui, font=("gabriola", 40), bg="#ECCA9C", text="An application developed using : ").place(x=x_center, y=y_center )
        Label(gui, font=("gabriola", 30), bg="#ECCA9C", text="sqlite3 and tkinter").place(x=x_center + 160, y=y_center + 80)
        Label(gui, font=("ink free", 30), bg="#ECCA9C", text="EXPENSO").place(x=x_center +150 , y=50)

        h = Label(gui, font=("century", 25), bg="#ECCA9C", text="This window automatically closes after : ")
        h.place(x=53 ,y=550)
        ltime=Label(gui,font=("century",25),bg="#ECCA9C",fg="black")
        ltime.place(x=655,y=550) 
  
        def timer():
            global t
            a=str(t)+" seconds"
            text_input = a
            ltime.config(text=text_input)
            ltime.after(1000, timer)
            t=t-1
        timer()
        gui.after(11000,gui.destroy)

    gui = tk.Tk()
    gui.title("EXPENSE TRACKER")
    gui.configure(bg='#ECCA9C')
    gui.geometry("900x700")
    
    window_width = 900
    window_height = 700
    label_width = 50
    label_height = 50
    x_center = (window_width - label_width) // 2
    y_center = (window_height - label_height) // 2
    
    # l8=Label(gui,width=60,height=7,font=("century",35),bg="#FFEC9E",text="").place(x=450,y=60)     #spinbox frame
    l7=Label(gui,width=100,height=5,font=("century",35),bg="#0C0C0C",text="").place(x=-455,y=420)  #black
    
    l1=Label(gui,font=("comic sans ms",17),bg="#ECCA9C",text="Product name").place(x=x_center-150,y=150)
    exp_itemname=StringVar()
    e1=Entry(gui,font=("adobe clean",15),textvariable=exp_itemname)
    e1.place(x=x_center+55,y=155,height=32,width=165)
    
    l2=Label(gui,font=("comic sans ms",17),bg="#ECCA9C",text="Date(dd-mm-yyyy)").place(x=x_center-150,y=200)
    exp_date=StringVar()
    e2=Entry(gui,font=("adobe clean",15),textvariable=exp_date)
    e2.place(x=x_center+55,y=205,height=32,width=165)
    
    l3=Label(gui,font=("comic sans ms",17),bg="#ECCA9C",text="Cost of product").place(x=x_center-150,y=250)
    exp_cost=StringVar()
    e3=Entry(gui,font=("adobe clean",15),textvariable=exp_cost)
    e3.place(x=x_center+55,y=255,height=32,width=165)

    scroll_bar=Scrollbar(gui)
    scroll_bar.place(x=651,y=420,height=278,width=20)  
    list1=Listbox(gui,height=7,width=30,font=("comic sans ms",20),yscrollcommand = scroll_bar.set)
    list1.place(x=168,y=420)
    scroll_bar.config( command = list1.yview )
    
    b1=Button(gui,text="Add Item",font=("georgia",17),activebackground="#fffa66",activeforeground="red",width=10,command=insertitems).place(x=20,y=315)
    b2=Button(gui,text="View all items",font=("georgia",17),activebackground="#fffa66",activeforeground="red",width=12,command=viewallitems).place(x=190,y=315)
    b3=Button(gui,text="Delete",font=("georgia",17),activebackground="#fffa66",activeforeground="red",width=10,command=open_delete_window).place(x=385,y=315)
    b5=Button(gui,text="Search",font=("georgia",17),activebackground="#fffa66",activeforeground="red",width=10,command=search_item).place(x=550,y=315)
    b6=Button(gui,text="Total spent",font=("georgia",17),activebackground="#fffa66",activeforeground="red",width=8,command=sumofitems).place(x=15,y=650)
    b6=Button(gui,text="Update",font=("georgia",17),activebackground="#fffa66",activeforeground="red",width=10,command=open_update_window).place(x=720,y=315)
    b7=Button(gui,text="Close app",font=("georgia",17),activebackground="#fffa66",activeforeground="red",width=10,command=endpage).place(x=700,y=650)
    # b8 = Button(gui, text="Export to CSV", font=("georgia", 17), activebackground="#fffa66", activeforeground="red", width=15, command=export_to_csv).place(x=550, y=400)
    # b_export_pdf = Button(gui, text="Export to PDF", font=("georgia",17), activebackground="#fffa66", activeforeground="red", width=15, command=export_to_pdf)
    # b_export_pdf.place(x=730, y=650)

    global graph_type_var
    graph_type_var = tk.StringVar(gui)
    graph_type_var.set("Select Graph Type")

    graph_type_dropdown = ttk.Combobox(gui, textvariable = graph_type_var , values=["Bar Chart", "Pie Chart", "Line Graph"],font=("georgia",14),width=15)
    graph_type_dropdown.place(x=x_center+50, y=380)

    plot_button = tk.Button(gui, text="Plot Graph", command=plot_graph , font=("georgia",15))
    plot_button.place(x=x_center+270, y=375)
    
    export_option_var = tk.StringVar(gui)
    export_option_var.set("Select Export Option")

    export_option_label = tk.Label(gui, text="Select Export Option:")
    export_option_label.pack()

    export_option_dropdown = ttk.Combobox(gui, textvariable=export_option_var, values=["Export to CSV", "Export to PDF"],font=("georgia",14),width=15)
    export_option_dropdown.place(x=x_center-320, y=380)
    # export_option_dropdown.pack()

    export_button = tk.Button(gui, text="Export", command=on_export_button_click,font=("georgia",15))
    export_button.place(x=x_center-90, y=375)
    # export_button.pack()

    l6=Label(gui,width=60,font=("Century 10",35),bg="#AFD198",fg="#6C0345",text="EXPENSE  TRACKER").place(x=-323,y=0)
    name = "Welcome, " + profilename
    l9=Label(gui,width=60,font=("century",30),bg="#E8EFCF",fg="black",text=name).place(x=-480,y=60)
    ltime=Label(gui,font=("century",30),bg="#E8EFCF",fg="black")
    ltime.place(x=470,y=60)
    def digitalclock():
        text_input = time.strftime("%d-%m-%Y   %H:%M:%S")
        ltime.config(text=text_input)
        ltime.after(1000, digitalclock)
    digitalclock()
    gui.resizable(False, False)
    gui.mainloop()
   
window_width = 1000
window_height = 700
label_width = 50
label_height = 25
x_center = (window_width - label_width) // 2
y_center = (window_height - label_height) // 2

l1=Label(root,font=("comic sans ms",19),bg="#B5C18E",text="Username").place(x=x_center-150,y=y_center-(y_center/2))
l2=Label(root,font=("comic sans ms",19),bg="#B5C18E",text="Password").place(x=x_center-150,y=y_center-(y_center/2)+70)
b1=Button(root,text="Login",font=("algerian",19),activebackground="#fffa66",activeforeground="red",width=12,command=login).place(x=x_center-180,y=360)
b2=Button(root,text="New User",font=("algerian",19),activebackground="#fffa66",activeforeground="red",width=12,command=open_register_window).place(x=x_center+40,y=360)

login_username=StringVar()
e1=Entry(root,font=("adobe clean",15),textvariable=login_username)
e1.place(x=x_center+10,y=y_center-(y_center/2)+5,height=30,width=165)

login_password=StringVar()
e2=Entry(root,font=("adobe clean",15),textvariable=login_password,show="*")
e2.place(x=x_center+10,y=y_center-(y_center/2)+75,height=30,width=165)

Label(root,width=60,height=2,font=("Anton",35),bg="#B99470",fg="#cc2900",text="EXPENSE  TRACKER").place(x=-300,y=0)
#Label(root,font=("Ink Free",27),bg="#33cccc",fg="#0000ff",text="R HARSHA").place(x=750,y=590)
frame2 = Frame(bd=1, highlightthickness=0, background="#DEAC80").place(x=0, rely=0.78, relwidth=1, relheight=1)  # bottom
b3=Button(root,text="Exit Window",font=("candara",15,"bold"),activebackground="#F7DCB9",activeforeground="red",width=10,command=root.destroy).place(x=410,y=600)
b4=Button(root,text="Delete all users",font=("candara",15,"bold"),activebackground="#F7DCB9",activeforeground="red",width=12,command=deleteallusers).place(x=130,y=600)
b5=Button(root,text="View all users",font=("candara",15,"bold"),activebackground="#F7DCB9",activeforeground="red",width=12,command=viewwindow).place(x=690,y=600)


root.resizable(False, False)
root.mainloop()
