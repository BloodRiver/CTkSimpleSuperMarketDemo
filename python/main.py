import customtkinter as ctk
import tkinter.messagebox as msg
import models
from datetime import date
import os
from pathlib import Path
from validators import check_email_format, check_password_format
import functools

ADMIN_USER = models.User("Admin", "admin@system.com")
ADMIN_USER.set_password("Admin@1234")
ADMIN_USER.is_admin = True
try:
    ADMIN_USER.save_new()
except models.sql.IntegrityError:
    pass


'''
--------------------------------------------------------

                    Custom Exceptions

--------------------------------------------------------
'''


class ScreenNotFoundException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        

'''
--------------------------------------------------------

                       Screens

--------------------------------------------------------
'''


class LoginScreen(ctk.CTkFrame):
    ADMIN_USERNAME = "Sajeed"
    ADMIN_PASSWORD = "1234"

    def __init__(self, master, *args, **kwargs):
        global TITLE_FONT

        super().__init__(master, *args, **kwargs)
        
        self.master = master
        
        title_label = ctk.CTkLabel(self, text="Login", font=TITLE_FONT)
        title_label.pack(side=ctk.TOP, anchor=ctk.CENTER, pady=(200, 0))
        
        email_label = ctk.CTkLabel(self, text="Email")
        email_label.pack()
        
        self.__email_entry = ctk.CTkEntry(self)
        self.__email_entry.pack()
        
        password_label = ctk.CTkLabel(self, text="Password")
        password_label.pack()
        
        self.__password_entry = ctk.CTkEntry(self, show="*")
        self.__password_entry.pack()
        
        link_font = ctk.CTkFont(underline=True)
        create_account_label = ctk.CTkLabel(self, font=link_font, cursor="hand2", text="Don't have an account? Click here to create one!")
        create_account_label.pack()
        create_account_label.bind("<Button-1>", self.__show_register_screen)
        
        login_button = ctk.CTkButton(self, fg_color="green", hover_color="darkgreen", text="Login", text_color="white", command=self.__login_button_on_click)
        login_button.pack()
        
    def __show_register_screen(self, event):
        self.master.show_screen("register")
        
    def __login_button_on_click(self):
        try:
            email = check_email_format(self.__email_entry.get())
        except ValueError as e:
            msg.showerror("Invalid Input", "Invalid Email Format: " + str(e))
            self.__email_entry.configure(fg_color="red", text_color="white")
            return
        
        try:
            user: models.User = models.User.load_by_email(email)
        except models.User.DoesNotExist:
            msg.showerror("User not found", "User with that email does not exist in the database")
            self.__email_entry.configure(fg_color="red", text_color="white")
            return
            
        try:
            password = check_password_format(self.__password_entry.get())
        except ValueError as e:
            msg.showerror("Invalid Input", "Invalid Password format: " + str(e))
            self.__password_entry.configure(fg_color="red", text_color="white")
            return
        
        if user.check_password(password):
            user.set_last_logged_in(date.today())
            user.update()
            if user.is_admin:
                next_screen = self.master.show_screen("admin")
                next_screen.initialize(user)
            else:
                next_screen = self.master.show_screen("customer")
                next_screen.initialize(user)
        else:
            msg.showerror("Incorrect Password", "Password is incorrect")
            self.__password_entry.configure(fg_color="red", text_color="white")
        
        
class RegisterScreen(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        global TITLE_FONT

        super().__init__(master, *args, **kwargs)
        
        self.master = master
        
        title_label = ctk.CTkLabel(self, text="Register", font=TITLE_FONT)
        title_label.pack(side=ctk.TOP, anchor=ctk.CENTER, pady=(200, 0))
        
        username_label = ctk.CTkLabel(self, text="Username")
        username_label.pack()
        
        
        self.__username_entry = ctk.CTkEntry(self)
        self.__username_entry.pack()
        
        email_label = ctk.CTkLabel(self, text="Email")
        email_label.pack()
        
        self.__email_entry = ctk.CTkEntry(self)
        self.__email_entry.pack()
        
        new_password_label = ctk.CTkLabel(self, text="New Password")
        new_password_label.pack()
        
        self.__new_password_entry = ctk.CTkEntry(self, show="*")
        self.__new_password_entry.pack()
        
        retype_password_label = ctk.CTkLabel(self, text="Re-type Password")
        retype_password_label.pack()
        
        self.__retype_password_entry = ctk.CTkEntry(self, show="*")
        self.__retype_password_entry.pack()
        
        link_font = ctk.CTkFont(underline=True)
        login_label = ctk.CTkLabel(self, font=link_font, cursor="hand2", text="Already have an account? Click here to login")
        login_label.pack()
        login_label.bind("<Button-1>", self.__show_login_screen)
        
        register_button = ctk.CTkButton(self, fg_color="green", hover_color="darkgreen", text="Register", text_color="white", command=self.__register_button_on_click)
        register_button.pack()
        
    def __show_login_screen(self, event):
        self.master.show_screen("login")
        
    def __register_button_on_click(self):
        # Input validation
        username = self.__username_entry.get()

        if len(username) < 4:
            msg.showerror("Invalid Input", "Username must be at least 4 characters long")
            self.__username_entry.configure(fg_color="red", text_color="white")
            return
        
        try:
            email = check_email_format(self.__email_entry.get())
        except ValueError as e:
            msg.showerror("Invalid Input", "Invalid Email format: " + str(e))
            self.__email_entry.configure(fg_color="red", text_color="white")
            return
        
        
        try:
            password = check_password_format(self.__new_password_entry.get())
        except ValueError as e:
            msg.showerror("Invalid Input", "Invalid Password format: " + str(e))
            self.__new_password_entry.configure(fg_color="red", text_color="white")
            return
        
        retype_password = self.__retype_password_entry.get()
        
        if retype_password != password:
            msg.showerror("Invalid Input", "Passwords do not match")
            self.__new_password_entry.configure(fg_color="red", text_color="white")
            self.__retype_password_entry.configure(fg_color="red", text_color="white")
            return
        
        new_user = models.User(username, email)
        new_user.set_password(password)

        try:
            new_user.save_new()
        except models.sql.IntegrityError:
            msg.showerror("Already Exists", "A user with the given email already exists")
            return
        
        msg.showinfo("Success", "New User created successfully. Please Log in to continue")
        self.master.show_screen("login")


class AdminDashboardScreen(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        global TITLE_FONT

        super().__init__(master, *args, **kwargs)

        self.master = master

        title_label = ctk.CTkLabel(self, text="Admin Dashboard", font=TITLE_FONT)
        title_label.pack(side=ctk.TOP, anchor=ctk.CENTER, pady=(20, 0))

        # view items database
        view_items_database_button = ctk.CTkButton(self, text="View Items Database", command=self.__view_items_database_button_on_click)
        view_items_database_button.pack()

        # view accounts database
        view_accounts_button = ctk.CTkButton(self, text="View Accounts Database", command=self.__view_accounts_button_on_click)
        view_accounts_button.pack()

        # view pending orders
        view_pending_orders_button = ctk.CTkButton(self, text="View Pending Orders", command=self.__view_pending_orders_button_on_click)
        view_pending_orders_button.pack()

        # logout
        logout_button = ctk.CTkButton(self, text="Logout", fg_color="red", command=self.__logout_button_on_click)
        logout_button.pack()

    def __view_items_database_button_on_click(self):
        next_screen = self.master.show_screen("itemsdb")
        next_screen.initialize(user=self.__user)

    def __view_accounts_button_on_click(self):
        next_screen = self.master.show_screen("accountsdb")
        next_screen.initialize(user=self.__user)

    def __view_pending_orders_button_on_click(self):
        next_screen = self.master.show_screen("pendingorders")
        next_screen.initialize(user=self.__user)

    def __logout_button_on_click(self):
        self.master.show_screen("login")

    def initialize(self, user: models.User):
        self.__user = user
     

class AdminViewItemsDatabaseScreen(ctk.CTkFrame):
    __table_frame_num_rows: int
    
    class __ItemTableRow:
        __item: models.Item
        __selected_checkbox: ctk.CTkCheckBox
        __item_name_entry: ctk.CTkEntry
        __unit_price_entry: ctk.CTkEntry
        __items_in_stock_entry: ctk.CTkEntry
        
        def __init__(self, item: models.Item, selected_checkbox: ctk.CTkCheckBox, item_name_entry: ctk.CTkEntry, unit_price_entry: ctk.CTkEntry, items_in_stock_entry: ctk.CTkEntry):
            self.__item = item
            self.__selected_checkbox = selected_checkbox
            self.__item_name_entry = item_name_entry
            self.__unit_price_entry = unit_price_entry
            self.__items_in_stock_entry = items_in_stock_entry
        
        def get_item(self) -> models.Item:
            return self.__item
        
        def is_selected(self) -> bool:
            return bool(self.__selected_checkbox.get())
        
        def set_selected(self, selected: bool):
            if selected:
                self.__selected_checkbox.select()
            else:
                self.__selected_checkbox.deselect()

        def update(self) -> bool:
            item_name = self.__item_name_entry.get()
        
            if len(item_name) < 4:
                msg.showerror("Invalid Input", "Item Name must be at least 4 characters long")
                self.__item_name_entry.configure(fg_color="red", text_color="white")
                return False
            
            unit_price = self.__unit_price_entry.get()
                
            if len(unit_price) < 1:
                msg.showerror("Invalid input", "Please enter unit price")
                self.__unit_price_entry.configure(fg_color="red", text_color="white")
                return False
                
            try:
                unit_price = float(unit_price)
            except ValueError:
                msg.showerror("Invalid Input", "Unit price must be a valid REAL number")
                self.__unit_price_entry.configure(fg_color="red", text_color="white")
                return False
                
            if unit_price < 1.0:
                msg.showerror("Invalid Input", "Unit price must be a positive number and greater than 0.0")
                self.__unit_price_entry.configure(fg_color="red", text_color="white")
                return False
                
            items_in_stock = self.__items_in_stock_entry.get()
            
            if len(items_in_stock) < 1:
                msg.showerror("Invalid Input", "Please enter items in stock")
                self.__items_in_stock_entry.configure(fg_color="red", text_color="white")
                return False
            
            try:
                items_in_stock = int(items_in_stock)
            except ValueError:
                msg.showerror("Invalid Input", "Items in stock must be a valid whole number (integer)")
                self.__items_in_stock_entry.configure(fg_color="red", text_color="white")
                return False
            
            if items_in_stock < 1:
                msg.showerror("Invalid Input", "Items in stock must be at least 1")
                self.__items_in_stock_entry.configure(fg_color="red", text_color="white")
                return False
            
            self.__item.set_item_name(item_name)
            self.__item.set_unit_price(unit_price)
            self.__item.set_items_in_stock(items_in_stock)
            
            self.__item.update()
            
            self.__item_name_entry.configure(fg_color=ctk.ThemeManager.theme["CTkEntry"]["fg_color"], text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"])
            self.__items_in_stock_entry.configure(fg_color=ctk.ThemeManager.theme["CTkEntry"]["fg_color"], text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"])
            self.__unit_price_entry.configure(fg_color=ctk.ThemeManager.theme["CTkEntry"]["fg_color"], text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"])
            
            return True

        def delete(self):
            self.__selected_checkbox.destroy()
            self.__item_name_entry.destroy()
            self.__unit_price_entry.destroy()
            self.__items_in_stock_entry.destroy()
            self.__item.delete()
            
    __table_rows: list[__ItemTableRow] = list()
    
    def __init__(self, master, *args, **kwargs):
        global TITLE_FONT, TABLE_HEADER_FONT
        
        super().__init__(master, *args, **kwargs)
        
        self.__table_frame_num_rows = 1

        self.master = master
        
        title_label = ctk.CTkLabel(self, text="Items Database", font=TITLE_FONT)
        title_label.pack(side=ctk.TOP, anchor=ctk.CENTER, pady=(20, 0))
        
        new_item_frame = ctk.CTkFrame(self)
        new_item_frame.pack(side=ctk.TOP, expand=True, fill=ctk.X)
        
        new_item_data_frame = ctk.CTkFrame(new_item_frame)
        new_item_data_frame.pack(side=ctk.LEFT, expand=True, fill=ctk.X)
        
        new_item_button_frame = ctk.CTkFrame(new_item_frame)
        new_item_button_frame.pack(side=ctk.RIGHT)
        
        new_item_name_label = ctk.CTkLabel(new_item_data_frame, text="New Item Name: ")
        new_item_name_label.pack(side=ctk.LEFT, padx=5)
        
        self.__new_item_name_entry = ctk.CTkEntry(new_item_data_frame)
        self.__new_item_name_entry.pack(side=ctk.LEFT, padx=5)
        
        new_item_unit_price_label = ctk.CTkLabel(new_item_data_frame, text="New Item Unit Price: ")
        new_item_unit_price_label.pack(side=ctk.LEFT, padx=5)
        
        self.__new_item_unit_price_entry = ctk.CTkEntry(new_item_data_frame)
        self.__new_item_unit_price_entry.pack(side=ctk.LEFT, padx=5)
        
        new_item_items_in_stock_label = ctk.CTkLabel(new_item_data_frame, text="Items in Stock: ")
        new_item_items_in_stock_label.pack(side=ctk.LEFT, padx=5)
        
        self.__new_item_items_in_stock_entry = ctk.CTkEntry(new_item_data_frame)
        self.__new_item_items_in_stock_entry.pack(side=ctk.LEFT, padx=5)
        
        new_item_add_button = ctk.CTkButton(new_item_button_frame, text="Add Item", command=self.__new_item_add_button_on_click)
        new_item_add_button.pack(side=ctk.RIGHT)
        
        self.__table_frame = ctk.CTkScrollableFrame(self)
        self.__table_frame.pack(side=ctk.TOP, expand=True, fill=ctk.BOTH)
        
        self.__select_all_checkbox = ctk.CTkCheckBox(self.__table_frame, text="Select All", font=TABLE_HEADER_FONT, command=self.__select_all)
        self.__select_all_checkbox.grid(row=0, column=0, ipadx=50)
        
        fruit_name_table_header_label = ctk.CTkLabel(self.__table_frame, text="Item Name", font=TABLE_HEADER_FONT)
        fruit_name_table_header_label.grid(row=0, column=1, ipadx=50, sticky=ctk.NSEW)
        
        unit_price_table_header_label = ctk.CTkLabel(self.__table_frame, text="Unit Price", font=TABLE_HEADER_FONT)
        unit_price_table_header_label.grid(row=0, column=2, ipadx=50, sticky=ctk.NSEW)
        
        items_in_stock_table_header_label = ctk.CTkLabel(self.__table_frame, text="Items in Stock", font=TABLE_HEADER_FONT)
        items_in_stock_table_header_label.grid(row=0, column=3, ipadx=50, sticky=ctk.NSEW)
        
            
        button_group_frame = ctk.CTkFrame(self)
        button_group_frame.pack(side=ctk.TOP, anchor=ctk.NW, expand=True, fill=ctk.X)
        
        left_button_group_frame = ctk.CTkFrame(button_group_frame)
        left_button_group_frame.pack(side=ctk.LEFT, anchor=ctk.NW, expand=True, fill=ctk.X)
        
        right_button_group_frame = ctk.CTkFrame(button_group_frame)
        right_button_group_frame.pack(side=ctk.LEFT, anchor=ctk.NW, expand=True, fill=ctk.X)
        
        go_back_button = ctk.CTkButton(left_button_group_frame, text="Go Back", fg_color="blue", hover_color="lightblue", command=self.__go_back_button_on_click)
        go_back_button.pack(side=ctk.LEFT)
        
        delete_button = ctk.CTkButton(right_button_group_frame, text="Delete Selected", fg_color="red", hover_color="maroon", command=self.__delete_selected)
        delete_button.pack(side=ctk.RIGHT, padx=5)
        
        save_button = ctk.CTkButton(right_button_group_frame, text="Save", fg_color="green", command=self.__save_all)
        save_button.pack(side=ctk.RIGHT)
        
        for each_item in models.Item.load_all():
            self.__add_new_row(each_item)
        
    def initialize(self, user: models.User):
        self.__user = user
        
    def __delete_selected(self):
        count = 0
        
        while count < len(self.__table_rows):
            if self.__table_rows[count].is_selected():
                item = self.__table_rows.pop(count)
                item.delete()
                continue
                
            count += 1
        
    def __select_all(self):
        for each_row in self.__table_rows:
            each_row.set_selected(bool(self.__select_all_checkbox.get()))
            
    def __save_all(self):
        success = True
        for each_row in self.__table_rows:
            success = success and each_row.update()
        
        if success:
            msg.showinfo("Success", "All Items Updated in Database")
        
    def __go_back_button_on_click(self):
        next_screen = self.master.show_screen("admin")
        next_screen.initialize(user=self.__user)
    
    def __add_new_row(self, new_item: models.Item):
        new_item_checkbox = ctk.CTkCheckBox(self.__table_frame, text="")
        new_item_checkbox.grid(row=self.__table_frame_num_rows, column=0, padx=(0, 30), sticky=ctk.W)
        
        item_name_entry = ctk.CTkEntry(self.__table_frame)
        item_name_entry.grid(row=self.__table_frame_num_rows, column=1, padx=30, sticky=ctk.NSEW)
        item_name_entry.insert(0, new_item.get_item_name())
        
        unit_price_entry = ctk.CTkEntry(self.__table_frame)
        unit_price_entry.grid(row=self.__table_frame_num_rows, column=2, padx=30, sticky=ctk.NSEW)
        unit_price_entry.insert(0, str(new_item.get_unit_price()))
        
        items_in_stock_entry = ctk.CTkEntry(self.__table_frame)
        items_in_stock_entry.grid(row=self.__table_frame_num_rows, column=3, padx=30, sticky=ctk.NSEW)
        items_in_stock_entry.insert(0, str(new_item.get_items_in_stock()))
        
        new_row = AdminViewItemsDatabaseScreen.__ItemTableRow(new_item, new_item_checkbox, item_name_entry, unit_price_entry, items_in_stock_entry)
        
        self.__table_rows.append(new_row)
        
        self.__table_frame_num_rows += 1
        
    def __new_item_add_button_on_click(self):
        new_item_name = self.__new_item_name_entry.get()
        
        if len(new_item_name) < 4:
            msg.showerror("Invalid Input", "Item Name must be at least 4 characters long")
            self.__new_item_name_entry.configure(fg_color="red", text_color="white")
            return
        
        try:
            models.Item.load_by_item_name(new_item_name)
        except models.Item.DoesNotExist:
            new_item_unit_price = self.__new_item_unit_price_entry.get()
            
            if len(new_item_unit_price) < 1:
                msg.showerror("Invalid input", "Please enter unit price")
                self.__new_item_unit_price_entry.configure(fg_color="red", text_color="white")
                return
            
            try:
                new_item_unit_price = float(new_item_unit_price)
            except ValueError:
                msg.showerror("Invalid Input", "Unit price must be a valid REAL number")
                self.__new_item_unit_price_entry.configure(fg_color="red", text_color="white")
                return
            
            if new_item_unit_price < 1.0:
                msg.showerror("Invalid Input", "Unit price must be a positive number and greater than 0.0")
                self.__new_item_unit_price_entry.configure(fg_color="red", text_color="white")
                return
            
            new_item_items_in_stock = self.__new_item_items_in_stock_entry.get()
            
            if len(new_item_items_in_stock) < 1:
                msg.showerror("Invalid Input", "Please enter items in stock")
                self.__new_item_items_in_stock_entry.configure(fg_color="red", text_color="white")
                return
            
            try:
                new_item_items_in_stock = int(new_item_items_in_stock)
            except ValueError:
                msg.showerror("Invalid Input", "Items in stock must be a valid whole number (integer)")
                self.__new_item_items_in_stock_entry.configure(fg_color="red", text_color="white")
                return
            
            if new_item_items_in_stock < 1:
                msg.showerror("Invalid Input", "Items in stock must be at least 1")
                self.__new_item_items_in_stock_entry.configure(fg_color="red", text_color="white")
                return
            
            new_item = models.Item(new_item_name, new_item_unit_price, new_item_items_in_stock)
            new_item.save_new()
            
            self.__add_new_row(new_item)
        else:
            msg.showerror("Already Exists", "This item already exists in the database")
            self.__new_item_name_entry.configure(fg_color="red", text_color="white")
        
class AdminViewAccountsDatabaseScreen(ctk.CTkFrame):
    __table_frame_num_rows: int

    def __init__(self, master, *args, **kwargs):
        global TITLE_FONT, TABLE_HEADER_FONT
        
        super().__init__(master, *args, **kwargs)
        
        self.__table_frame_num_rows = 1
        
        self.master = master
        
        title_label = ctk.CTkLabel(self, text="Accounts Database", font=TITLE_FONT)
        title_label.pack(side=ctk.TOP, anchor=ctk.CENTER, pady=(20, 0))
        
        self.__table_frame = ctk.CTkScrollableFrame(self)
        self.__table_frame.pack(side=ctk.TOP, expand=True, fill=ctk.BOTH)
        
        # Username, Email, Date Joined, Last Logged In, Is Admin
        
        username_table_header_label = ctk.CTkLabel(self.__table_frame, text="Username", font=TABLE_HEADER_FONT)
        username_table_header_label.grid(row=0, column=0, ipadx=5)
        
        email_table_header_label = ctk.CTkLabel(self.__table_frame, text="Email", font=TABLE_HEADER_FONT)
        email_table_header_label.grid(row=0, column=1, ipadx=5)
        
        date_joined_table_header_label = ctk.CTkLabel(self.__table_frame, text="Date Joined", font=TABLE_HEADER_FONT)
        date_joined_table_header_label.grid(row=0, column=2, ipadx=5)
        
        last_logged_in_table_header_label = ctk.CTkLabel(self.__table_frame, text="Last Logged In", font=TABLE_HEADER_FONT)
        last_logged_in_table_header_label.grid(row=0, column=3, ipadx=5)
        
        is_admin_table_header_label = ctk.CTkLabel(self.__table_frame, text="Is Admin?", font=TABLE_HEADER_FONT)
        is_admin_table_header_label.grid(row=0, column=4, ipadx=5)
        
        for each_user in models.User.load_all():
            username_label = ctk.CTkLabel(self.__table_frame, text=each_user.get_username())
            username_label.grid(row=self.__table_frame_num_rows, column=0, ipadx=5)
            
            email_label = ctk.CTkLabel(self.__table_frame, text=each_user.get_email())
            email_label.grid(row=self.__table_frame_num_rows, column=1, ipadx=5)
            
            date_joined = ctk.CTkLabel(self.__table_frame, text=str(each_user.get_date_joined()))
            date_joined.grid(row=self.__table_frame_num_rows, column=2, ipadx=5)
            
            last_logged_in_label = ctk.CTkLabel(self.__table_frame, text=str(each_user.get_last_logged_in()))
            last_logged_in_label.grid(row=self.__table_frame_num_rows, column=3, ipadx=5)
            
            is_admin_label = ctk.CTkLabel(self.__table_frame, text=("Yes" if each_user.is_admin else "No"))
            is_admin_label.grid(row=self.__table_frame_num_rows, column=4, ipadx=5)
            
            self.__table_frame_num_rows += 1
            
        go_back_button = ctk.CTkButton(self, text="Go Back", fg_color="blue", hover_color="darkblue", command=self.__go_back_button_on_click)
        go_back_button.pack(side=ctk.TOP, anchor=ctk.NW, padx=10, pady=10)

            
    def initialize(self, user: models.User):
        self.__user = user
        
    def __go_back_button_on_click(self):
        next_screen = self.master.show_screen("admin")
        next_screen.initialize(user=self.__user)


class AdminViewPendingOrdersScreen(ctk.CTkFrame):
    __table_frame_num_rows: int
    
    def __init__(self, master, *args, **kwargs):
        global TITLE_FONT, TABLE_HEADER_FONT
        
        self.master = master
        
        super().__init__(master, *args, **kwargs)
        
        self.__table_frame_num_rows = 1

        title_label = ctk.CTkLabel(self, text="Order History", font=TITLE_FONT)
        title_label.pack(side=ctk.TOP, anchor=ctk.CENTER, pady=(20, 0))
        
        # Date Time, Username
        
        self.__table_frame = ctk.CTkScrollableFrame(self)
        self.__table_frame.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)
        
        order_date_table_header_label = ctk.CTkLabel(self.__table_frame, text="Order Date", font=TABLE_HEADER_FONT)
        order_date_table_header_label.grid(row=0, column=0, ipadx=5)
        
        username_table_header_label = ctk.CTkLabel(self.__table_frame, text="Username", font=TABLE_HEADER_FONT)
        username_table_header_label.grid(row=0, column=1, ipadx=5)
        
        date_completed_table_header_label = ctk.CTkLabel(self.__table_frame, text="Date Completed", font=TABLE_HEADER_FONT)
        date_completed_table_header_label.grid(row=0, column=2, ipadx=5)
        
        for each_order in models.Order.load_orders():
            order_date_label = ctk.CTkLabel(self.__table_frame, text=str(each_order.get_date_ordered()))
            order_date_label.grid(row=self.__table_frame_num_rows, column=0)
            
            username_label = ctk.CTkLabel(self.__table_frame, cursor="hand2", text=str(each_order.get_user().get_username()), text_color="blue", font=ctk.CTkFont(underline=True))
            username_label.grid(row=self.__table_frame_num_rows, column=1)
            username_label.bind("<Button-1>", functools.partial(self.view_order, each_order.get_date_ordered(), each_order.get_user(), (not bool(each_order.get_date_completed()))))
            
            date_completed_label = ctk.CTkLabel(
                self.__table_frame,
                text=(
                    str(each_order.get_date_completed()) if each_order.get_date_completed() else "Pending")
            )
            
            date_completed_label.grid(row=self.__table_frame_num_rows, column=2)

            self.__table_frame_num_rows += 1
        
    def initialize(self, user: models.User):
        self.__user = user
        
    def view_order(self, date_ordered: date, ordered_by: models.User, pending: bool, event):
        next_screen = self.master.show_screen('vieworderdetails')
        orders = models.Order.get_orders(date_ordered, ordered_by, pending)
        next_screen.initialize(user=self.__user, orders=orders)


class AdminViewOrderDetailsScreen(ctk.CTkFrame):
    __user: models.User
    __orders: list[models.Order]
    __table_frame_num_rows: int

    def __init__(self, master, *args, **kwargs):
        global TITLE_FONT, TABLE_HEADER_FONT
        
        super().__init__(master, *args, **kwargs)
        
        title_label = ctk.CTkLabel(self, text="Order Details", font=TITLE_FONT)
        title_label.pack(side=ctk.TOP, anchor=ctk.CENTER, pady=20)
        
        self.__table_frame_num_rows = 1
        
        
    def initialize(self, user: models.User, orders: list[models.Order]):
        print("initialize orders:", orders)
        self.__user = user
        self.__orders = orders
        
        customer_name_label = ctk.CTkLabel(self, text=f"Customer Name: {orders[0].get_user().get_username()}")
        customer_name_label.pack(side=ctk.TOP, anchor=ctk.NW, pady=(0, 20), padx=10)
        
        date_ordered_label = ctk.CTkLabel(self, text=f"Date Ordered: {str(orders[0].get_date_ordered())}")
        date_ordered_label.pack(side=ctk.TOP, anchor=ctk.NW, pady=(0, 20), padx=10)
        
        self.__table_frame = ctk.CTkScrollableFrame(self)
        self.__table_frame.pack(side=ctk.TOP, anchor=ctk.NW, expand=True, fill=ctk.BOTH)
        
        item_name_table_header = ctk.CTkLabel(self.__table_frame, text="Item Name", font=TABLE_HEADER_FONT)
        item_name_table_header.grid(row=0, column=0, padx=20)
        
        unit_price_table_header = ctk.CTkLabel(self.__table_frame, text="Unit Price", font=TABLE_HEADER_FONT)
        unit_price_table_header.grid(row=0, column=1, padx=20)
        
        number_of_items_table_header = ctk.CTkLabel(self.__table_frame, text="Number of Items", font=TABLE_HEADER_FONT)
        number_of_items_table_header.grid(row=0, column=2, padx=20)
        
        total_price_table_header = ctk.CTkLabel(self.__table_frame, text="Total Price", font=TABLE_HEADER_FONT)
        total_price_table_header.grid(row=0, column=3, padx=20)
        
        total_price = 0.0
        
        for each_order in orders:
            item_name_label = ctk.CTkLabel(self.__table_frame, text=each_order.get_item().get_item_name())
            item_name_label.grid(row=self.__table_frame_num_rows, column=0, padx=20)
            
            unit_price_label = ctk.CTkLabel(self.__table_frame, text=str(each_order.get_item().get_unit_price()))
            unit_price_label.grid(row=self.__table_frame_num_rows, column=1, padx=20)
            
            number_of_items_label = ctk.CTkLabel(self.__table_frame, text=str(each_order.get_number_ordered()))
            number_of_items_label.grid(row=self.__table_frame_num_rows, column=2, padx=20)
            
            total = each_order.get_item().get_unit_price() * each_order.get_number_ordered()

            total_price_label = ctk.CTkLabel(self.__table_frame, text=str(total))
            total_price_label.grid(row=self.__table_frame_num_rows, column=3, padx=20)
            
            self.__table_frame_num_rows += 1
            
            total_price += total
            
        total_price_footer = ctk.CTkLabel(self, text=f"Total Price: {total_price}", font=TABLE_HEADER_FONT)
        total_price_footer.pack(side=ctk.TOP, anchor=ctk.NE, padx=20, pady=(20))
        
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(side=ctk.TOP, anchor=ctk.NW, expand=True, fill=ctk.X)
        
        left_button_frame = ctk.CTkFrame(button_frame)
        left_button_frame.pack(side=ctk.LEFT, expand=True, fill=ctk.X)
        
        right_button_frame = ctk.CTkFrame(button_frame)
        right_button_frame.pack(side=ctk.RIGHT, expand=True, fill=ctk.X)
        
        go_back_button = ctk.CTkButton(left_button_frame, text="Go Back", fg_color="blue", hover_color="darkblue", command=self.__go_back_button_on_click)
        go_back_button.pack(padx=10)
        
        cancel_order_button = ctk.CTkButton(right_button_frame, text="Cancel Order", fg_color="red", hover_color="maroon", command=self.__cancel_order_button_on_click)
        cancel_order_button.pack(side=ctk.RIGHT, anchor=ctk.NE, padx=10)
        
        complete_order_button = ctk.CTkButton(right_button_frame, text="Complete Order", fg_color="green", hover_color="darkgreen", command=self.__complete_order_button_on_click)
        complete_order_button.pack(side=ctk.RIGHT, anchor=ctk.NE, padx=10)
        
    
    def __go_back_button_on_click(self):
        next_screen = self.master.show_screen("pendingorders")
        next_screen.initialize(user=self.__user)
        
    def __cancel_order_button_on_click(self):
        for each_order in self.__orders:
            each_order.delete()
        msg.showinfo("Cancelled", "Order has been cancelled")
        
    def __complete_order_button_on_click(self):
        for each_order in self.__orders:
            each_order.set_date_completed(date.today())
            each_order.update()

        msg.showinfo("Completed", "Order successfully completed")


class CustomerDashboardScreen(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        global TITLE_FONT
        
        super().__init__(*args, **kwargs)
        
        title_label = ctk.CTkLabel(self, text="Customer Dashboard", font=TITLE_FONT)
        title_label.pack(side=ctk.TOP, anchor=ctk.CENTER)
        
        # Browse Items
        browse_items_button = ctk.CTkButton(self, text="Browse Items", command=self.__browse_items_button_on_click)
        browse_items_button.pack(pady=20)
        
        # Logout
        logout_button = ctk.CTkButton(self, text="Logout", command=self.__logout_button_on_click)
        logout_button.pack(pady=20)
        
    def initialize(self, user: models.User):
        self.__user = user
        
    def __browse_items_button_on_click(self):
        next_screen = self.master.show_screen("customerbrowse")
        next_screen.initialize(self.__user)
        
    def __logout_button_on_click(self):
        self.master.show_screen("login")
        
        
class CustomerBrowseItemsScreen(ctk.CTkFrame):
    __shopping_cart: models.ShoppingCart
    __table_frame_num_rows: int
 
    class __ItemTableRow:
        __item: models.Item
        __selected_checkbox: ctk.CTkCheckBox
        __items_to_purchase_entry: ctk.CTkEntry
        
        def __init__(self, selected_checkbox: ctk.CTkCheckBox, item: models.Item, items_to_purchase_entry: ctk.CTkEntry):
            self.__item = item
            self.__selected_checkbox = selected_checkbox
            self.__items_to_purchase_entry = items_to_purchase_entry
        
        def get_item(self) -> models.Item:
            return self.__item
        
        def get_items_to_purchase(self) -> int:
            try:
                items_to_purchase = int(self.__items_to_purchase_entry.get())
            except ValueError:
                msg.showerror("Invalid Input", "Items to purchase must be a valid integer")
                self.__items_to_purchase_entry.configure(fg_color="red", text_color="white")
                return -1
            else:
                if items_to_purchase < 1:
                    msg.showerror("Invalid Input", "Items to purchase must be a positive integer (greater than 0)")
                    self.__items_to_purchase_entry.configure(fg_color="red", text_color="white")
                    return -1

                self.__items_to_purchase_entry.configure(fg_color=ctk.ThemeManager.theme['CTkEntry']['fg_color'], text_color=ctk.ThemeManager.theme['CTkEntry']['text_color'])
                
                return items_to_purchase
            
        def set_items_to_purchase(self, items_to_purchase: int):
            self.__items_to_purchase_entry.delete(0, ctk.END)
            self.__items_to_purchase_entry.insert(0, str(items_to_purchase))
        
        def is_selected(self) -> bool:
            return bool(self.__selected_checkbox.get())
        
        def set_selected(self, selected: bool):
            if selected:
                self.__selected_checkbox.select()
            else:
                self.__selected_checkbox.deselect()

    __table_rows: list[__ItemTableRow] = list()
    
    def __init__(self, *args, **kwargs):
        global TITLE_FONT, TABLE_HEADER_FONT
        
        super().__init__(*args, **kwargs)
        
        
        title_label = ctk.CTkLabel(self, text="All Items", font=TITLE_FONT)
        title_label.pack(side=ctk.TOP, anchor=ctk.CENTER)
        
        
    def initialize(self, user: models.User, shopping_cart: models.ShoppingCart = None):
        self.__user = user
        
        if shopping_cart is None:
            self.__shopping_cart = models.ShoppingCart(self.__user)
        else:
            self.__shopping_cart = shopping_cart
        
        # checkbox, item_name, unit_price, items_in_stock, quantity to purchase
        self.__table_frame_num_rows = 1
        
        self.__table_frame = ctk.CTkScrollableFrame(self)
        self.__table_frame.pack(side=ctk.TOP, expand=True, fill=ctk.BOTH)
        
        self.__select_all_checkbox = ctk.CTkCheckBox(self.__table_frame, text="Select All", font=TABLE_HEADER_FONT, command=self.__select_all)
        self.__select_all_checkbox.grid(row=0, column=0, ipadx=25)
        
        fruit_name_table_header_label = ctk.CTkLabel(self.__table_frame, text="Item Name", font=TABLE_HEADER_FONT)
        fruit_name_table_header_label.grid(row=0, column=1, ipadx=25, sticky=ctk.NSEW)
        
        unit_price_table_header_label = ctk.CTkLabel(self.__table_frame, text="Unit Price", font=TABLE_HEADER_FONT)
        unit_price_table_header_label.grid(row=0, column=2, ipadx=25, sticky=ctk.NSEW)
        
        items_in_stock_table_header_label = ctk.CTkLabel(self.__table_frame, text="Items in Stock", font=TABLE_HEADER_FONT)
        items_in_stock_table_header_label.grid(row=0, column=3, ipadx=25, sticky=ctk.NSEW)
        
        items_to_purchase_table_header_label = ctk.CTkLabel(self.__table_frame, text="Items to Purchase", font=TABLE_HEADER_FONT)
        items_to_purchase_table_header_label.grid(row=0, column=4, ipadx=25, sticky=ctk.NSEW)
        
            
        button_group_frame = ctk.CTkFrame(self)
        button_group_frame.pack(side=ctk.TOP, anchor=ctk.NW, expand=True, fill=ctk.X)
        
        left_button_group_frame = ctk.CTkFrame(button_group_frame)
        left_button_group_frame.pack(side=ctk.LEFT, anchor=ctk.NW, expand=True, fill=ctk.X)
        
        right_button_group_frame = ctk.CTkFrame(button_group_frame)
        right_button_group_frame.pack(side=ctk.LEFT, anchor=ctk.NW, expand=True, fill=ctk.X)
        
        # buttons: go back, add to cart
        go_back_button = ctk.CTkButton(left_button_group_frame, text="Go Back", fg_color="blue", hover_color="lightblue", command=self.__go_back_button_on_click)
        go_back_button.pack(side=ctk.LEFT)
        
        remove_from_cart_button = ctk.CTkButton(right_button_group_frame, text="Remove Selected From Cart", fg_color="red", hover_color="maroon", command=self.__remove_all_from_cart)
        remove_from_cart_button.pack(side=ctk.RIGHT, padx=(20, 0))
        
        add_to_cart_button = ctk.CTkButton(right_button_group_frame, text="Add Selected to Cart", fg_color="green", command=self.__add_all_to_cart)
        add_to_cart_button.pack(side=ctk.RIGHT)
        
        for each_item in models.Item.load_all():
            selected = False
            items_to_purchase = 0
            
            for each_cart_item in self.__shopping_cart.get_cart_items():
                if each_cart_item.get_item().get_id() == each_item.get_id():
                    selected = True
                    items_to_purchase = each_cart_item.get_quantity()
            
            selected_checkbox = ctk.CTkCheckBox(self.__table_frame, text="")
            selected_checkbox.grid(row=self.__table_frame_num_rows, column=0, padx=(0, 25), sticky=ctk.W)
            if selected:
                selected_checkbox.select()
            else:
                selected_checkbox.deselect()
            
            item_name_label = ctk.CTkLabel(self.__table_frame, text=each_item.get_item_name())
            item_name_label.grid(row=self.__table_frame_num_rows, column=1, sticky=ctk.NSEW, padx=25)
            
            unit_price_label = ctk.CTkLabel(self.__table_frame, text=str(each_item.get_unit_price()))
            unit_price_label.grid(row=self.__table_frame_num_rows, column=2, sticky=ctk.NSEW, padx=25)
            
            items_in_stock_label = ctk.CTkLabel(self.__table_frame, text=str(each_item.get_items_in_stock()))
            items_in_stock_label.grid(row=self.__table_frame_num_rows, column=3, sticky=ctk.NSEW, padx=25)
            
            items_to_purchase_entry = ctk.CTkEntry(self.__table_frame)
            items_to_purchase_entry.insert(0, str(items_to_purchase))
            items_to_purchase_entry.grid(row=self.__table_frame_num_rows, column=4, sticky=ctk.NSEW, padx=25)

            new_row = CustomerBrowseItemsScreen.__ItemTableRow(selected_checkbox, each_item, items_to_purchase_entry)
            
            self.__table_rows.append(new_row)
            self.__table_frame_num_rows += 1
        
        
        # bottom button: view cart
        self.__view_cart_button = ctk.CTkButton(self, text=f"View Cart ({self.__shopping_cart.count_items()})", command=self.__view_cart_button_on_click, height=50, fg_color="orange", hover_color="#c98506", text_color="white", font=TABLE_HEADER_FONT)
        self.__view_cart_button.pack(side=ctk.BOTTOM, fill=ctk.X, expand=True)
        
    def __view_cart_button_on_click(self):
        next_screen = self.master.show_screen("shoppingcart")
        next_screen.initialize(self.__user, self.__shopping_cart)
        
    def __go_back_button_on_click(self):
        if self.__shopping_cart.count_items():
            if not msg.askyesno("Confirm", "Are you sure you wish to return to dashboard? WARNING: Your shopping cart will become empty!"):
                return
        
        next_screen = self.master.show_screen("customer")
        next_screen.initialize(self.__user)
    
    def __add_all_to_cart(self):
        for each_item in self.__table_rows:
            if each_item.is_selected():
                items_to_purchase = each_item.get_items_to_purchase()
                
                if items_to_purchase == -1:
                    break
                
                self.__shopping_cart.update_item(each_item.get_item(), items_to_purchase)
                    
        self.__view_cart_button.configure(text=f"View Cart ({self.__shopping_cart.count_items()})")
    
    def __remove_all_from_cart(self):
        for each_item in self.__table_rows:
            if each_item.is_selected():
                self.__shopping_cart.remove_item(each_item.get_item())
                each_item.set_selected(False)
                each_item.set_items_to_purchase(0)
        self.__view_cart_button.configure(text=f"View Cart ({self.__shopping_cart.count_items()})")
        print(self.__shopping_cart)
    
    def __select_all(self):
        for each_row in self.__table_rows:
            each_row.set_selected(bool(self.__select_all_checkbox.get()))
        
        
class CustomerViewCartScreen(ctk.CTkFrame):
    __table_frame_num_rows: int
    
    class __CartItemTableRow:
        __cart_item: models.ShoppingCartItem
        __selected_checkbox: ctk.CTkCheckBox
        __item_name_label: ctk.CTkLabel
        __unit_price_label: ctk.CTkLabel
        __quantity_entry: ctk.CTkEntry
        __total_price_label: ctk.CTkLabel
        
        def __init__(self, cart_item: models.ShoppingCartItem, selected_checkbox: ctk.CTkCheckBox, item_name_label: ctk.CTkLabel, unit_price_label: ctk.CTkLabel, quantity_entry: ctk.CTkEntry, total_price_label: ctk.CTkLabel):
            self.__cart_item = cart_item
            self.__selected_checkbox = selected_checkbox
            self.__item_name_label = item_name_label
            self.__unit_price_label = unit_price_label
            self.__quantity_entry = quantity_entry
            self.__total_price_label = total_price_label
            
        def get_cart_item(self) -> models.ShoppingCartItem:
            return self.__cart_item
            
        def is_selected(self) -> bool:
            return bool(self.__selected_checkbox.get())
        
        def set_selected(self, selected: bool):
            if selected:
                self.__selected_checkbox.select()
            else:
                self.__selected_checkbox.deselect()
                
        def update(self) -> bool:
            if (len(self.__quantity_entry.get()) < 1):
                self.__quantity_entry.configure(fg_color="red", text_color="white")
                msg.showinfo("Invalid Input", "Quantity must not be empty")
                return False
            
            try:
                quantity = int(self.__quantity_entry.get())
            except ValueError:
                self.__quantity_entry.configure(fg_color="red", text_color="white")
                msg.showinfo("Invalid input", "Quantity must be a valid whole number (integer)")
                return False

            if quantity < 1:
                self.__quantity_entry.configure(fg_color="red", text_color="white")
                msg.showinfo("Invalid input", "Quantity must be at least 1")
                return False
            
            self.__quantity_entry.configure(fg_color=ctk.ThemeManager.theme['CTkEntry']['fg_color'], text_color=ctk.ThemeManager.theme['CTkEntry']['text_color'])
            
            self.__cart_item.set_quantity(quantity)
            return True
            
        def destroy(self):
            self.__selected_checkbox.destroy()
            self.__item_name_label.destroy()
            self.__unit_price_label.destroy()
            self.__quantity_entry.destroy()
            self.__total_price_label.destroy()
    
    
    __table_rows: list[__CartItemTableRow]

    def __init__(self, *args, **kwargs):
        global TITLE_FONT, TABLE_HEADER_FONT
        
        super().__init__(*args, **kwargs)
        
        self.__table_frame_num_rows = 1
        
        title_label = ctk.CTkLabel(self, text="Shopping Cart", font=TITLE_FONT)
        title_label.pack(side=ctk.TOP, anchor=ctk.CENTER, pady=20)
        
        self.__table_frame = ctk.CTkScrollableFrame(self)
        self.__table_frame.pack(fill=ctk.BOTH, expand=True)
        
        # checkbox, item_name, unit_price, quantity in cart (auto update price calculation), total_price
        self.__select_all_checkbox = ctk.CTkCheckBox(self.__table_frame, text="Select All", command=self.__select_all)
        self.__select_all_checkbox.grid(row=0, column=0, ipadx=20)
        
        item_name_table_header_label = ctk.CTkLabel(self.__table_frame, text="Item Name", font=TABLE_HEADER_FONT)
        item_name_table_header_label.grid(row=0, column=1, sticky=ctk.NSEW, ipadx=20)
        
        unit_price_header_label = ctk.CTkLabel(self.__table_frame, text="Unit Price", font=TABLE_HEADER_FONT)
        unit_price_header_label.grid(row=0, column=2, sticky=ctk.NSEW, ipadx=20)
        
        quantity_header_label = ctk.CTkLabel(self.__table_frame, text="Quantity", font=TABLE_HEADER_FONT)
        quantity_header_label.grid(row=0, column=3, sticky=ctk.NSEW, ipadx=20)
        
        total_price_header_label = ctk.CTkLabel(self.__table_frame, text="Total Price", font=TABLE_HEADER_FONT)
        total_price_header_label.grid(row=0, column=4, sticky=ctk.NSEW, ipadx=20)
        
        # overall total price at the bottom right
        self.__overall_price_label = ctk.CTkLabel(self, text="Total Price:", font=TABLE_HEADER_FONT)
        self.__overall_price_label.pack(side=ctk.TOP, anchor=ctk.E)
        
        button_group_frame = ctk.CTkFrame(self)
        button_group_frame.pack(side=ctk.TOP, anchor=ctk.NW, expand=True, fill=ctk.X)
        
        left_button_group_frame = ctk.CTkFrame(button_group_frame)
        left_button_group_frame.pack(side=ctk.LEFT, anchor=ctk.NW, expand=True, fill=ctk.X)
        
        right_button_group_frame = ctk.CTkFrame(button_group_frame)
        right_button_group_frame.pack(side=ctk.LEFT, anchor=ctk.NW, expand=True, fill=ctk.X)
        
        # buttons: go back (to browse screen), remove items from cart
        go_back_button = ctk.CTkButton(left_button_group_frame, text="Go Back", fg_color="blue", hover_color="lightblue", command=self.__go_back_button_on_click)
        go_back_button.pack(side=ctk.LEFT)
        
        remove_from_cart_button = ctk.CTkButton(right_button_group_frame, text="Remove Selected From Cart", fg_color="red", hover_color="maroon", command=self.__remove_selected_from_cart)
        remove_from_cart_button.pack(side=ctk.RIGHT, padx=(20, 0))
        
        place_order_button = ctk.CTkButton(right_button_group_frame, text="Place Order for all items in cart", fg_color="green", command=self.__place_order_button_on_click)
        place_order_button.pack(side=ctk.RIGHT)
        
    def __go_back_button_on_click(self):
        next_screen = self.master.show_screen("customerbrowse")
        next_screen.initialize(user=self.__user, shopping_cart=self.__shopping_cart)
    
    def __place_order_button_on_click(self):
        for each_item in self.__table_rows:
            if not each_item.update():
                break
            
            new_order = models.Order.from_cart_item(each_item.get_cart_item(), self.__user)
            new_order.save_new()
        else:
            msg.showinfo("Success", "Your Order has successfully been placed!")
            print(self.__shopping_cart)
    
    def __remove_selected_from_cart(self):
        i = 0
        while i < len(self.__table_rows):
            each_item = self.__table_rows[i]
            if each_item.is_selected():
                each_item.destroy()
                self.__shopping_cart.remove_item(each_item.get_cart_item())
                self.__table_rows.remove(each_item)
                continue

            i += 1
        
        self.__select_all_checkbox.deselect()
        self.__overall_price_label.configure(text=f"Total Price: {self.__shopping_cart.calculate_overall_total()}")
        print(self.__shopping_cart)
        
        
    def initialize(self, user: models.User, shopping_cart: models.ShoppingCart):
        self.__user = user
        self.__shopping_cart = shopping_cart
        
        self.__table_rows = list()
        
        # checkbox, item_name, unit_price, quantity in cart (auto update price calculation), total_price
        for each_item in self.__shopping_cart.get_cart_items():
            new_checkbox = ctk.CTkCheckBox(self.__table_frame, text="")
            new_checkbox.grid(row=self.__table_frame_num_rows, column=0, sticky=ctk.W, padx=(0, 20))
            
            new_item_name_label = ctk.CTkLabel(self.__table_frame, text=each_item.get_item().get_item_name())
            new_item_name_label.grid(row=self.__table_frame_num_rows, column=1, sticky=ctk.NSEW, padx=20)
            
            new_unit_price_label = ctk.CTkLabel(self.__table_frame, text=str(each_item.get_item().get_unit_price()))
            new_unit_price_label.grid(row=self.__table_frame_num_rows, column=2, sticky=ctk.NSEW, padx=20)
            
            new_quantity_entry = ctk.CTkEntry(self.__table_frame)
            new_quantity_entry.grid(row=self.__table_frame_num_rows, column=3, sticky=ctk.NSEW, padx=20)
            new_quantity_entry.insert(0, str(each_item.get_quantity()))
            
            new_total_price_label = ctk.CTkLabel(self.__table_frame, text=str(each_item.calculate_total_price()))
            new_total_price_label.grid(row=self.__table_frame_num_rows, column=4, sticky=ctk.NSEW, padx=20)
            
            new_row = CustomerViewCartScreen.__CartItemTableRow(each_item, new_checkbox, new_item_name_label, new_unit_price_label, new_quantity_entry, new_total_price_label)
            
            self.__table_rows.append(new_row)
            
            self.__table_frame_num_rows += 1
            
        self.__overall_price_label.configure(text="Total Price: {:,}".format(self.__shopping_cart.calculate_overall_total()),)
        
    def __select_all(self):
        for each_item in self.__table_rows:
            each_item.set_selected(bool(self.__select_all_checkbox.get()))


class MainWindow(ctk.CTk):
    '''
    The main window to display all GUI Widgets on screen
    '''
    __screens: dict[str, ctk.CTkFrame] = dict()  # stores reference to different screens for screen switching

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def add_screen(self, name: str, screen: ctk.CTkFrame):
        '''
        Adds a screen to the main window for screen switching
        '''
        self.__screens.update({name: screen})
        
    def show_screen(self, name: str) -> ctk.CTkFrame:
        '''
        Searches the screens dictionary of added strings and displays that screen if it exists in the dictionary
        otherwise throws and error
        
        Returns
        -------
        customtkinter.CTkFrame instance
        '''
        
        new_screen_class = self.__screens.get(name)
        
        if new_screen_class is None:
            raise ScreenNotFoundException(f"Screen \"{name}\" does not exist. Try adding it using add_screen()")
        
        # Delete all children in the main window
        for each_child in self.winfo_children():
            each_child.destroy()
        
        # Call the class to instantiate
        new_screen = new_screen_class(self)
        
        # Place the screen in the main window
        new_screen.pack(anchor=ctk.NW, fill=ctk.BOTH, expand=True)
        
        return new_screen


if __name__ == "__main__":
    BASE_DIR = Path(os.path.abspath(os.path.dirname(__file__)))
    
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    models.create_tables()

    main_window = MainWindow()

    main_window.geometry("840x640")
    main_window.title("Simple Super Market")

    main_window.add_screen("login", LoginScreen)
    main_window.add_screen("register", RegisterScreen)
    main_window.add_screen("admin", AdminDashboardScreen)
    main_window.add_screen("itemsdb", AdminViewItemsDatabaseScreen)
    main_window.add_screen("accountsdb", AdminViewAccountsDatabaseScreen)
    main_window.add_screen("pendingorders", AdminViewPendingOrdersScreen)
    main_window.add_screen('vieworderdetails', AdminViewOrderDetailsScreen)
    
    main_window.add_screen("customer", CustomerDashboardScreen)
    main_window.add_screen("customerbrowse", CustomerBrowseItemsScreen)
    main_window.add_screen("shoppingcart", CustomerViewCartScreen)


    '''
    --------------------------------------------------------

                            Fonts

    --------------------------------------------------------
    '''
        
    TITLE_FONT = ctk.CTkFont(family="Arial", size=32, weight="bold")
    LINK_FONT = ctk.CTkFont(underline=True)

    TABLE_HEADER_FONT = ctk.CTkFont(weight="bold")


    main_window.show_screen("login")

    main_window.mainloop()
