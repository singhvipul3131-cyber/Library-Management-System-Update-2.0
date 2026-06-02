import sqlite3
import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from matplotlib.pylab import qr
import qrcode
from PIL import ImageTk, Image
import os
from tkinter import filedialog

# =================================================================
# MAIN WINDOW INITIALIZATION
# =================================================================
root = tk.Tk()
root.title("Library Management System")

class LibraryManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("1540x800+250+100")
        
        # 1. Variables (Jo Image 3 ke top par hain)
        self.book_name = StringVar()
        self.author_name = StringVar()
        self.category = StringVar()
        self.publisher = StringVar()
        self.year = StringVar()
        self.isbn = StringVar()
        self.search_text = StringVar()
        
        # 2. Database connection call
        self.connect_db()
        
        # 3. Main Title (Image 3)
        title = Label(self.root, text="Library Management System", font=("times new roman", 32, "bold"), bd=10, relief=GROOVE)
        title.pack(side=TOP, fill=X)
        
        # 4. Manage Frame (Left Panel - Image 3)
        Manage_Frame = Frame(self.root, bd=4, relief=RIDGE, bg="crimson")
        Manage_Frame.place(x=20, y=80, width=550, height=700)
        
        m_title = Label(Manage_Frame, text="Manage Books", bg="crimson", fg="white", font=("times new roman", 25, "bold"))
        m_title.grid(row=0, columnspan=2, pady=20)
        
        # Labels and Entries Loop (Image 3 & 4)
        labels = ["Book Name", "Author", "Category", "Publisher", "Year", "ISBN"]
        variables = [self.book_name, self.author_name, self.category, self.publisher, self.year, self.isbn]
        
        for i in range(len(labels)):
            lbl = Label(Manage_Frame, text=labels[i], bg="crimson", fg="white", font=("times new roman", 18, "bold"))
            lbl.grid(row=i+1, column=0, pady=10, padx=20, sticky="w")
            ent = Entry(Manage_Frame, font=("times new roman", 15), textvariable=variables[i])
            ent.grid(row=i+1, column=1, pady=10, padx=20)
            
        btn_Frame = Frame(Manage_Frame, bd=4, relief=RIDGE, bg="crimson")
        btn_Frame.place(x=15, y=480, width=500, height=180)

# Row 0 buttons
        Button(btn_Frame, text="Add", width=10, command=self.add_book).grid(row=0, column=0, pady=5)
        Button(btn_Frame, text="Update", width=10, command=self.update_book).grid(row=0, column=1, pady=5)
        Button(btn_Frame, text="Delete", width=10, command=self.delete_book).grid(row=0, column=2, pady=5)
        Button(btn_Frame, text="Clear", width=10, command=self.clear_fields).grid(row=0, column=3, pady=5)

# Row 1 (QR)
        Button(btn_Frame, text="Generate QR", width=20, command=self.generate_qr).grid(row=1, column=0, columnspan=4, pady=10)

# Row 2 (NEW ADVANCED BUTTONS)
        Button(btn_Frame, text="Issue", width=10, command=self.issue_book).grid(row=2, column=0, pady=5)
        Button(btn_Frame, text="Return", width=10, command=self.return_book).grid(row=2, column=1, pady=5)
        Button(btn_Frame, text="QR Pay", width=10, command=self.generate_qr).grid(row=2, column=2, pady=5)
        
# ROW 3 (Receipt)
        Button(
            btn_Frame,
            text="Receipt",
            width=20,
            command=self.generate_receipt
        ).grid(row=3, column=0, columnspan=4, pady=10)

        # 7. Detail Frame (Right Panel - Image 4)
        Detail_Frame = Frame(self.root, bd=4, relief=RIDGE, bg="crimson")
        Detail_Frame.place(x=600, y=80, width=900, height=700)
        
        lbl_search = Label(Detail_Frame, text="Search Book", bg="crimson", fg="white", font=("times new roman", 20, "bold"))
        lbl_search.grid(row=0, column=0, padx=20, pady=10)
        
        txt_search = Entry(Detail_Frame, width=20, textvariable=self.search_text, font=("times new roman", 15))
        txt_search.grid(row=0, column=1, pady=10, padx=20)
        
        Button(Detail_Frame, text="Search", width=10, command=self.search_book).grid(row=0, column=2, padx=10, pady=10)
        Button(Detail_Frame, text="Show All", width=10, command=self.fetch_data).grid(row=0, column=3, padx=10, pady=10)
        
        # 7. Table Frame & Treeview Setup (Image 5)
        Table_Frame = Frame(Detail_Frame, bd=4, relief=RIDGE, bg="crimson")
        Table_Frame.place(x=10, y=70, width=870, height=350) # Height thodi kam ki hai taaki niche Fine Calculator aa sake
        
        scroll_x = Scrollbar(Table_Frame, orient=HORIZONTAL)
        scroll_y = Scrollbar(Table_Frame, orient=VERTICAL)
        
        self.library_table = ttk.Treeview(Table_Frame, columns=("book", "author", "category", "publisher", "year", "isbn"), xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        
        scroll_x.pack(side=BOTTOM, fill=X)
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.config(command=self.library_table.xview)
        scroll_y.config(command=self.library_table.yview)
        
        headings = ["Book Name", "Author", "Category", "Publisher", "Year", "ISBN"]
        for i, h in enumerate(headings):
            self.library_table.heading(i, text=h)
            
        self.library_table["show"] = "headings"
        widths = [150, 130, 120, 140, 80, 120]
        for i, w in enumerate(widths):
            self.library_table.column(i, width=w)
            
        self.library_table.pack(fill=BOTH, expand=1)
        self.library_table.bind("<ButtonRelease-1>", self.get_cursor)
        
        # 8. Fine Calculator Section Setup (Image 6 se uthaya)
        # Isko Detail_Frame ke andar table ke niche grid kar rahe hain
        self.setup_fine_calculation(Detail_Frame)
        
        # Data load load karne ke liye
        self.fetch_data()

    # =================================================================
    # CORE FUNCTIONS (Sabhi bilkul same indentation level par honge)
    # =================================================================
    
    def connect_db(self):
        self.con = sqlite3.connect("library.db")
        self.cur = self.con.cursor()   # ⭐ YE LINE MUST HAI

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS books(
        book TEXT,
        author TEXT,
        category TEXT,
        publisher TEXT,
        year TEXT,
        isbn TEXT,
        status TEXT DEFAULT 'AVAILABLE',
        issue_date TEXT,
        due_date TEXT
)
""")
        self.con.commit()

    def setup_fine_calculation(self, parent_frame):
        # Yahan parent_frame (jo ki Detail_Frame hai) ka use karenge
        fine_frame = tk.LabelFrame(parent_frame, text="Late Fee Calculator", font=("Arial", 12, "bold"), bg="crimson", fg="white")
        fine_frame.place(x=10, y=440, width=870, height=200) # Grid ki jagah place use kiya taaki layout set rahe
        
        tk.Label(fine_frame, text="Due Date (YYYY-MM-DD):", bg="#4A1E1E", fg="white", font=("Arial", 10)).grid(row=0, column=0, pady=5, padx=10)
        self.due_date_entry = tk.Entry(fine_frame, font=("Arial", 10), width=15)
        self.due_date_entry.insert(0, "2026-05-20")
        self.due_date_entry.grid(row=0, column=1, pady=5, padx=10)
        
        tk.Label(fine_frame, text="Return Date (YYYY-MM-DD):", bg="#4A1E1E", fg="white", font=("Arial", 10)).grid(row=1, column=0, pady=5, padx=10)
        self.return_date_entry = tk.Entry(fine_frame, font=("Arial", 10), width=15)
        self.return_date_entry.insert(0, "2026-05-25")
        self.return_date_entry.grid(row=1, column=1, pady=5, padx=10)
        
        tk.Button(fine_frame, text="Calculate Fine", font=("Arial", 10, "bold"), bg="green", fg="white", command=self.calculate_late_fee).grid(row=2, column=0, columnspan=2, pady=10)
        
        self.fee_label = tk.Label(fine_frame, text="Late Fine: ₹0", font=("Arial", 14, "bold"), bg="crimson", fg="white")
        self.fee_label.grid(row=2, column=2, padx=20)

    def calculate_late_fee(self):
       try:
           due_dt = datetime.strptime(
            self.due_date_entry.get().strip(),
            "%Y-%m-%d"
        )

           return_dt = datetime.strptime(
            self.return_date_entry.get().strip(),
            "%Y-%m-%d"
        )

           if return_dt <= due_dt:
            self.fine_amount = 0

            self.fee_label.config(
                text="Late Fine: ₹0 (In Time)",
                fg="green"
            )

           else:
               days_late = (return_dt - due_dt).days

               self.fine_amount = days_late * 1

               self.fee_label.config(
                text=f"Late Fine: ₹{self.fine_amount} ({days_late} Days Late)",
                fg="yellow"
            )

       except ValueError:
             messagebox.showerror(
            "Error",
            "Invalid date format. Please use YYYY-MM-DD."
        ) 
    def generate_qr(self):

        if not self.book_name.get() or not self.isbn.get():
           messagebox.showerror("Error", "Book Name & ISBN required")
           return

        # agar return ke baad fine hai to use karo
        fine = getattr(self, "fine_amount", 0)

        if not messagebox.askyesno(
            "Pay Fine",
            f"Do you want to pay the late fine of ₹{fine}?"
        ):
            return

        upi_id = "7379373809@ptyes"

        upi_link = f"upi://pay?pa={upi_id}&pn=Library&am={fine}&cu=INR"

        qr = qrcode.make(upi_link)

        file_name = f"FINE_QR_{self.isbn.get()}.png"
        qr.save(file_name)

        messagebox.showinfo("Success", f"QR Created: {file_name}\nAmount: ₹{fine}")
        
    def generate_receipt(self):

       fine = getattr(self, "fine_amount", 0)

       receipt_text = f"""
================================
      LIBRARY PAYMENT RECEIPT
================================

Book Name : {self.book_name.get()}
ISBN      : {self.isbn.get()}

Fine Paid : ₹{fine}

Date : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Payment Mode : UPI QR

================================
      THANK YOU
================================
"""

       file_name = f"Receipt_{self.isbn.get()}.txt"

       with open(file_name, "w", encoding="utf-8") as f:
        f.write(receipt_text)

       messagebox.showinfo(
        "Receipt Generated",
        f"Receipt Saved:\n{file_name}"
    )

    def issue_book(self):
        print("Issue button clicked")

        from datetime import datetime, timedelta

        issue_date = datetime.today().date()
        due_date = issue_date + timedelta(days=7)

        self.cur.execute("""
        UPDATE books SET
        status='ISSUED',
        issue_date=?,
        due_date=?
        WHERE isbn=?
        """, (
              str(issue_date),
              str(due_date),
              self.isbn.get()
    ))

        self.con.commit()
        self.fetch_data()
        messagebox.showinfo("Success", "Book Issued Successfully!")
    def return_book(self):
       print("Return button clicked")
       from datetime import datetime

       self.cur.execute("SELECT due_date FROM books WHERE isbn=?", (self.isbn.get(),))
       row = self.cur.fetchone()

       if not row or not row[0]:
          messagebox.showerror("Error", "Book not issued!")
          return

       due_date = datetime.strptime(row[0], "%Y-%m-%d").date()
       return_date = datetime.today().date()

       days_late = (return_date - due_date).days

       if days_late > 0:
          self.fine_amount = days_late * 1
       else:
          self.fine_amount = 0

       self.cur.execute("""
       UPDATE books SET
       status='AVAILABLE',
       issue_date=NULL,
       due_date=NULL
       WHERE isbn=?
       """, (self.isbn.get(),))

       self.con.commit()
       self.fetch_data()

       messagebox.showinfo("Returned", f"Fine: ₹{self.fine_amount}")   
    def add_book(self):
        if self.book_name.get() == "" or self.isbn.get() == "":
            messagebox.showerror("Error", "Sabh fields bharna zaroori hai!")
            return
        self.cur.execute("""
        INSERT INTO books
        (book,author,category,publisher,year,isbn,status,issue_date,due_date)
        VALUES(?,?,?,?,?,?,?,?,?)
        """,(
            self.book_name.get(),
            self.author_name.get(),
            self.category.get(),
            self.publisher.get(),
            self.year.get(),
            self.isbn.get(),
            "AVAILABLE",
            None,
            None
      ))
        self.con.commit()
        self.fetch_data()
        self.clear_fields()
        messagebox.showinfo("Success", "Book successfully add ho gayi!")

    def fetch_data(self):
        self.cur.execute("SELECT * FROM books")
        rows = self.cur.fetchall()
        self.library_table.delete(*self.library_table.get_children())
        for row in rows:
            self.library_table.insert('', END, values=row)

    def clear_fields(self):
        self.book_name.set("")
        self.author_name.set("")
        self.category.set("")
        self.publisher.set("")
        self.year.set("")
        self.isbn.set("")

    def get_cursor(self, event):
        cursor_row = self.library_table.focus()
        data = self.library_table.item(cursor_row)
        row = data["values"]
        if row:
            self.book_name.set(row[0])
            self.author_name.set(row[1])
            self.category.set(row[2])
            self.publisher.set(row[3])
            self.year.set(row[4])
            self.isbn.set(row[5])
    
    def update_book(self):
        self.cur.execute("""
        UPDATE books SET
        book=?,
        author=?,
        category=?,
        publisher=?,
        year=?
        WHERE isbn=?
        """, (
            self.book_name.get(),
            self.author_name.get(),
            self.category.get(),
            self.publisher.get(),
            self.year.get(),
            self.isbn.get()
    ))

        self.con.commit()
        self.fetch_data()
        messagebox.showinfo("Success", "Book Updated Successfully")

    def delete_book(self):
        self.cur.execute(
        "DELETE FROM books WHERE isbn=?",
        (self.isbn.get(),)
    )

        self.con.commit()
        self.fetch_data()
        self.clear_fields()

        messagebox.showinfo("Success", "Book Deleted Successfully")

    def search_book(self):
        search = self.search_text.get()

        self.cur.execute("""
        SELECT * FROM books
        WHERE book LIKE ?
        OR author LIKE ?
        OR isbn LIKE ?
        """, (
        f"%{search}%",
        f"%{search}%",
        f"%{search}%"
    ))

        rows = self.cur.fetchall()

        self.library_table.delete(
            *self.library_table.get_children()
    )

        for row in rows:
            self.library_table.insert(
            '',
            END,
            values=row
        )
            
# =================================================================
# EXECUTION BLOCK (Bilkul end mein bina kisi space/indentation ke)
# =================================================================
obj = LibraryManagementSystem(root)
root.mainloop()