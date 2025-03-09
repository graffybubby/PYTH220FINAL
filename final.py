import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import datetime

# ---------- Paths to the plant data and supplier data jsons. ----------
data_file = 'data/plants.json'
supplier_file = 'data/suppliers.json'

# ---------- Classes ----------
# This class represents a plant in the inventory system
class Plant:
    def __init__(self, plant_id, name, description, quantity, greenhouse_required, supplier):
        self.plant_id = plant_id 
        self.name = name 
        self.description = description  
        self.quantity = quantity  
        self.greenhouse_required = greenhouse_required 
        self.supplier = supplier 

# This class represents a supplier in the inventory system
class Supplier:
    def __init__(self, name, phone_number, address):
        self.name = name  
        self.phone_number = phone_number  
        self.address = address  
        self.plants_served = []  

# This class initializes the GUI, manages plant and supplier data, and handles alerts
class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Set the application title
        self.title("Root 31 Inventory System")
    
        # Set default window size
        self.geometry("1000x600") 

        self.tabs = ttk.Notebook(self)

        # Inventory tab
        self.inventory_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.inventory_tab, text="Inventory")

        # Supplier tab
        self.suppliers_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.suppliers_tab, text="Suppliers")

        # Expand the tabs to fit the window
        self.tabs.pack(expand=1, fill="both")

        # ---------- Plant Inventory Tab with scrollbars ----------
        # Frame the inventory tab and its scroll bars
        inventory_frame = ttk.Frame(self.inventory_tab)
        inventory_frame.pack(fill=tk.BOTH, expand=True)

        # Build the table to display the plants
        self.inventory_tree = ttk.Treeview(inventory_frame, columns=("ID", "Name", "Description", "Quantity", "Greenhouse Required", "Supplier"), show="headings")
        
        # Set the column names
        for col in self.inventory_tree["columns"]:
            self.inventory_tree.heading(col, text=col)

        # Place the table in frame and add scroll bars for vertical and horizontal scroll
        self.inventory_tree.grid(row=0, column=0, sticky="nsew")
        inv_scrollbar_y = ttk.Scrollbar(inventory_frame, orient="vertical", command=self.inventory_tree.yview)
        inv_scrollbar_y.grid(row=0, column=1, sticky="ns")
        inv_scrollbar_x = ttk.Scrollbar(inventory_frame, orient="horizontal", command=self.inventory_tree.xview)
        inv_scrollbar_x.grid(row=1, column=0, sticky="ew")

        # Ensure the scroll bars remain visible when resizing the window
        inventory_frame.grid_rowconfigure(0, weight=1)
        inventory_frame.grid_columnconfigure(0, weight=1)
        self.inventory_tree.config(yscrollcommand=inv_scrollbar_y.set, xscrollcommand=inv_scrollbar_x.set)

        # ---------- Plant Inventory Tab Buttons ----------
        inventory_buttons = ttk.Frame(self.inventory_tab)
        inventory_buttons.pack(side=tk.TOP, fill=tk.X)

        # Buttons to add, update, and delete plants
        ttk.Button(inventory_buttons, text="Add Plant", command=self.add_plant).pack(side='left')
        ttk.Button(inventory_buttons, text="Update Plant", command=self.update_plant).pack(side='left')
        ttk.Button(inventory_buttons, text="Delete Plant", command=self.delete_plant).pack(side='left')

        # ---------- Supplier Tab with scrollbars ----------
        # Frame the supplier tab and its scroll bars
        supplier_frame = ttk.Frame(self.suppliers_tab)
        supplier_frame.pack(fill=tk.BOTH, expand=True)

        # Build the table to display the suppliers
        self.supplier_tree = ttk.Treeview(supplier_frame, columns=("Name", "Phone Number", "Address"), show="headings")
        
        # Set the column names
        for col in self.supplier_tree["columns"]:
            self.supplier_tree.heading(col, text=col)
        
        # Place the table in frame and add scroll bars for vertical and horizontal scroll
        self.supplier_tree.grid(row=0, column=0, sticky="nsew")
        sup_scrollbar_y = ttk.Scrollbar(supplier_frame, orient="vertical", command=self.supplier_tree.yview)
        sup_scrollbar_y.grid(row=0, column=1, sticky="ns")
        sup_scrollbar_x = ttk.Scrollbar(supplier_frame, orient="horizontal", command=self.supplier_tree.xview)
        sup_scrollbar_x.grid(row=1, column=0, sticky="ew")

        # Ensure the scroll bars remain visible when resizing the window
        supplier_frame.grid_rowconfigure(0, weight=1)
        supplier_frame.grid_columnconfigure(0, weight=1)
        self.supplier_tree.config(yscrollcommand=sup_scrollbar_y.set, xscrollcommand=sup_scrollbar_x.set)

        # ---------- Supplier Tab Buttons ----------
        supplier_buttons = ttk.Frame(self.suppliers_tab)
        supplier_buttons.pack()

        # Buttons to add, update, and remove suppliers
        ttk.Button(supplier_buttons, text="Add Supplier", command=self.add_supplier).pack(side='left', padx=5, pady=5)
        ttk.Button(supplier_buttons, text="Remove Supplier", command=self.remove_supplier).pack(side='left', padx=5, pady=5)
        ttk.Button(supplier_buttons, text="Update Supplier", command=self.update_supplier).pack(side='left', padx=5, pady=5)

        # ---------- Alerts Frame ----------
        # Frame that contains the alerts listbox and scrollbars
        self.alerts_frame = ttk.Frame(self)
        self.alerts_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
 
        # Listbox to display system alerts (low stock, greenhouse needs, etc.)
        self.alerts_listbox = tk.Listbox(self.alerts_frame, height=20, width=50)
        self.alerts_listbox.grid(row=0, column=0, sticky="nsew")
 
        # Vertical scrollbar for the alerts listbox
        self.alerts_scrollbar = ttk.Scrollbar(self.alerts_frame, orient="vertical", command=self.alerts_listbox.yview)
        self.alerts_scrollbar.grid(row=0, column=1, sticky="ns")
 
        # Horizontal scrollbar for the alerts listbox
        self.alerts_h_scrollbar = ttk.Scrollbar(self.alerts_frame, orient="horizontal", command=self.alerts_listbox.xview)
        self.alerts_h_scrollbar.grid(row=1, column=0, sticky="ew")
 
        # Link the scrollbars to the listbox for proper scrolling 
        self.alerts_listbox.config(yscrollcommand=self.alerts_scrollbar.set, xscrollcommand=self.alerts_h_scrollbar.set)
 
        # Configure the alert frame to resize properly with the main window
        self.alerts_frame.grid_rowconfigure(0, weight=1)
        self.alerts_frame.grid_columnconfigure(0, weight=1)

        # Load data from JSON files into the program on startup
        self.load_data()
        
        # Ensure data is saved properly when the window is closed
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Display the current date in the bottom left corner of the window
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        self.date_label = tk.Label(self, text=current_date)
        self.date_label.pack(side=tk.BOTTOM, anchor="w")


    # Method for loading the program data
    def load_data(self):
        
        # Check if the plant data file exists and is not empty, otherwise create an empty file
        if not os.path.exists(data_file) or os.path.getsize(data_file) == 0:
            with open(data_file, 'w') as f:
                json.dump([], f)

        try:
            # Open and read the plant data file
            with open(data_file, 'r') as f:
                plants = json.load(f)
                for plant in plants:
                    # Insert plant data into the inventory table
                    self.inventory_tree.insert('', tk.END, values=(
                        plant["id"], plant["name"], plant["description"],
                        plant["quantity"], plant["greenhouse_required"],
                        plant["supplier"]
                    ))
                    # Check if any plants need a low stock alert
                    self.check_low_stock_alert(plant)
        except Exception as e:
            # Display an error message if the file fails to load
            messagebox.showerror("Error", f"Failed to load plants: {e}")

        # Run the greenhouse alert check after loading plants
        self.check_greenhouse_alert()

        # Check if the supplier data file exists and is not empty, otherwise create an empty file
        if not os.path.exists(supplier_file) or os.path.getsize(supplier_file) == 0:
            with open(supplier_file, 'w') as f:
                json.dump([], f)

        try:
            # Open and read the supplier data file
            with open(supplier_file, 'r') as f:
                suppliers = json.load(f)
                for supplier in suppliers:
                    # Insert supplier data into the supplier table
                    self.supplier_tree.insert('', tk.END, values=(
                        supplier["name"], supplier["phone_number"], supplier["address"]
                    ))
        except Exception as e:
            # Display an error message if the file fails to load
            messagebox.showerror("Error", f"Failed to load suppliers: {e}")

    # Method that checks the quantity of a plant and generates an alert
    def check_low_stock_alert(self, plant):
        quantity = int(plant["quantity"])
        
        # If the plant is out of stock, generate a critical alert
        if quantity == 0:
            self.alerts_listbox.insert(tk.END, f"CRITICAL ALERT: Plant '{plant['name']}' is out of stock (Quantity: {plant['quantity']})")
        
        # If the plant has low stock (less than 5), generate a low stock alert
        elif quantity < 5:
            self.alerts_listbox.insert(tk.END, f"Alert: Plant '{plant['name']}' is low on stock (Quantity: {plant['quantity']})")
        
        # If the plant stock is sufficient, remove any previous low stock alerts
        else:
            self.remove_alert(plant["name"])

    # Method that removes greenhouse alerts when conditions are resolved
    def remove_alert(self, plant_name):
        alerts = self.alerts_listbox.get(0, tk.END)  # Retrieve all alerts
        
        # Iterate through alerts in reverse order to avoid index shifting issues
        for i in range(len(alerts) - 1, -1, -1):
            if alerts[i].startswith("GREENHOUSE ALERT:") and f"Plant '{plant_name}'" in alerts[i]:
                self.alerts_listbox.delete(i)  # Remove the greenhouse alert

    # Method that saves the current inventory and supplier data to JSON files
    def save_data(self):
        
        # ---------- Save plant data ----------
        plants = []
        for child in self.inventory_tree.get_children():
            values = self.inventory_tree.item(child, 'values')
            plants.append({
                "id": values[0],  
                "name": values[1], 
                "description": values[2], 
                "quantity": values[3],  
                "greenhouse_required": values[4], 
                "supplier": values[5]  
            })
        
        # Write plant data to JSON file
        with open(data_file, 'w') as f:
            json.dump(plants, f)
        
        # ---------- Save supplier data ----------
        suppliers = []
        for child in self.supplier_tree.get_children():
            values = self.supplier_tree.item(child, 'values')
            suppliers.append({
                "name": values[0],  
                "phone_number": values[1],  
                "address": values[2],  
                "plants_served": [] 
            })
        
        # Write supplier data to JSON file
        with open(supplier_file, 'w') as f:
            json.dump(suppliers, f, indent=4)

    # Method that handles window closing and ensures that data is saved before the program exits
    def on_closing(self):
        # Save data before exiting
        self.save_data()  
        # Close the application
        self.destroy() 


    # Method that adds a plant to the json db
    # method includes functionality to check that there are suppliers 
    # avaliable to add to the plant, to create a new supplier if none are 
    # avaliable and also to ensure that the correct data types are entered for the different plant values
    def add_plant(self):
        while True:
            # Dialog box for plant id that expects an integer
            plant_id = simpledialog.askinteger("Plant ID", "Enter plant ID:")
            # if the user doesnt enter a value, display error
            if plant_id is None:
                messagebox.showerror("Error", "Plant ID is required.")
            # if the plant id is not greater than 0, display error
            elif plant_id <= 0:
                messagebox.showerror("Error", "Plant ID must be a positive integer.")
            else:
                break
        # Dialog box for plant name that expects a string
        name = simpledialog.askstring("Plant Name", "Enter plant name:")
        # Dialog box for plant description that expects a string
        description = simpledialog.askstring("Description", "Enter description:")
        while True:
            # Dialog box for plant inventory quantity that expects a string
            quantity = simpledialog.askinteger("Quantity", "Enter quantity:")
            # If user doenst enter a value, display error
            if quantity is None:
                messagebox.showerror("Error", "Quantity is required.")
            # If the user enters a negative quantity, display error
            elif quantity < 0:
                messagebox.showerror("Error", "Quantity cannot be negative. Please enter a non-negative integer.")
            else:
                break
        # Initialize empty string for greenhouse required dialog
        greenhouse_required = ""
        while greenhouse_required not in ("yes", "no"):
            # Dialog box for plant green house needs that expects a string of 'yes' or 'no'
            greenhouse_required = simpledialog.askstring("Greenhouse Required", "Is greenhouse required? (yes/no):")
            # If the user enters something else other than 'yes' or 'no', display error
            if greenhouse_required not in ("yes", "no"):
                messagebox.showerror("Error", "Please enter 'yes' or 'no'.")

        # Get the list of suppliers
        suppliers = [self.supplier_tree.item(child)['values'][0] for child in self.supplier_tree.get_children()]
        
        # If there are no suppliers to get, prompt user to create a new supplier
        if not suppliers:
            # Display message box with a yes or no response option
            response = messagebox.askyesno("No Suppliers", "No suppliers available. Would you like to create a new supplier now?")
            if response:
                # Open the dialogbox to add a supplier 
                self.add_supplier()
                # Re-read the suppliers list after adding a new supplier
                suppliers = [self.supplier_tree.item(child)['values'][0] for child in self.supplier_tree.get_children()]
                # If a supplier was added, allow the user to select from a drop down
                if suppliers:
                    supplier_selection_window = tk.Toplevel(self)
                    supplier_selection_window.title("Select Supplier")
                    supplier_selection_window.geometry("300x100")
                    
                    # Create the dropdown box for supplier choices
                    supplier_selection = ttk.Combobox(supplier_selection_window, values=suppliers)
                    supplier_selection.set(suppliers[0])
                    supplier_selection.pack(pady=10)

                    supplier = "No Supplier Assigned"

                    # Function that confirmss the supplier selection and closes window
                    def confirm_selection():
                        nonlocal supplier
                        supplier = supplier_selection.get()
                        supplier_selection_window.destroy()

                    ttk.Button(supplier_selection_window, text="OK", command=confirm_selection).pack(pady=10)
                    self.wait_window(supplier_selection_window)
                    
                    # If the user did not create a supplier create an alert for that item 
                    if supplier == "No Supplier Assigned":
                        self.alerts_listbox.insert(tk.END, f"Alert: Plant '{name}' has no supplier assigned.")
                else:
                    # If no supplier was created, assign "No Supplier Assigned" and alert the user
                    supplier = "No Supplier Assigned"
                    self.alerts_listbox.insert(tk.END, f"Alert: Plant '{name}' has no supplier assigned.")
            else:
                # If the user chose not to add a supplier at all, alert them that the plant is missing one
                supplier = "No Supplier Assigned"
                self.alerts_listbox.insert(tk.END, f"Alert: Plant '{name}' has no supplier assigned.")
        else:
            # ---------- Supplier Selectoin Window ----------
            # If there are suppliers avaliable, allow the user to select one
            supplier_selection_window = tk.Toplevel(self)
            supplier_selection_window.title("Select Supplier")
            supplier_selection_window.geometry("300x100")
            
            # Display dropdown menu with the avaliable suppliers
            supplier_selection = ttk.Combobox(supplier_selection_window, values=suppliers)
            supplier_selection.set(suppliers[0])
            supplier_selection.pack(pady=10)

            supplier = ""

            # Function confirming supplier selection and closing window
            def confirm_selection():
                nonlocal supplier
                supplier = supplier_selection.get()
                supplier_selection_window.destroy()

            ttk.Button(supplier_selection_window, text="OK", command=confirm_selection).pack(pady=10)
            self.wait_window(supplier_selection_window)

        # If one of the plant fields is left empty display a message box with an error and stop the execution
        if None in (plant_id, name, description, quantity, greenhouse_required, supplier):
            messagebox.showerror("Error", "All fields are required.")
            return
        self.inventory_tree.insert('', tk.END, values=(plant_id, name, description, quantity, greenhouse_required, supplier))
        # Create low stock alert for plants with less than 5 in the inventory
        if quantity < 5:
            self.alerts_listbox.insert(tk.END, f"Alert: Plant '{name}' is low on stock (Quantity: {quantity})")
        # Save the data
        self.save_data()

    # Method that updates plant details
    def update_plant(self):
        # Get the selected item from the inventory
        selected_item = self.inventory_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No plant selected.")
            return
        
        # Retrieve current values of the selected plant
        current_values = list(self.inventory_tree.item(selected_item[0], 'values'))
        fields = ["ID", "Name", "Description", "Quantity", "Greenhouse Required", "Supplier"]
        old_name = current_values[1]  # Store old name for updating alerts
        
        # Create a new window for selecting which field to update
        field_selection_window = tk.Toplevel(self)
        field_selection_window.title("Select Field to Update")
        field_selection_window.geometry("300x200")
        
        # Dropdown to select which field to update
        field_selection = ttk.Combobox(field_selection_window, values=fields)
        field_selection.pack(pady=20)

        def confirm_field_selection():
            selected_field = field_selection.get()
            new_value = None
            
            # Updating the ID field (must be a positive integer)
            if selected_field == "ID":
                while True:
                    try:
                        initial_val = int(current_values[0])
                    except (ValueError, TypeError):
                        initial_val = None
                    new_value = simpledialog.askinteger("Plant ID", "Enter new plant ID:", initialvalue=initial_val)
                    if new_value is None:
                        messagebox.showerror("Error", "Plant ID is required.")
                    elif new_value <= 0:
                        messagebox.showerror("Error", "Plant ID must be a positive integer.")
                    else:
                        break
            
            # Updating Name, Description fields
            elif selected_field == "Name":
                new_value = simpledialog.askstring("Plant Name", "Enter new plant name:", initialvalue=current_values[1])
            elif selected_field == "Description":
                new_value = simpledialog.askstring("Description", "Enter new description:", initialvalue=current_values[2])
            
            # Updating Quantity (must be non-negative)
            elif selected_field == "Quantity":
                while True:
                    new_value = simpledialog.askinteger("Quantity", "Enter new quantity:", initialvalue=current_values[3])
                    if new_value is None:
                        messagebox.showerror("Error", "Quantity is required.")
                    elif new_value < 0:
                        messagebox.showerror("Error", "Quantity cannot be negative. Please enter a non-negative integer.")
                    else:
                        break
                # Remove existing alert and check if a new low stock alert should be added
                self.remove_alert(current_values[1])  
                self.check_low_stock_alert({"name": current_values[1], "quantity": new_value})
            
            # Updating Greenhouse Required field (must be 'yes' or 'no')
            elif selected_field == "Greenhouse Required":
                new_value = ""
                while new_value not in ("yes", "no"):
                    new_value = simpledialog.askstring("Greenhouse Required", "Is greenhouse required? (yes/no):", initialvalue=current_values[4])
                    if new_value not in ("yes", "no"):
                        messagebox.showerror("Error", "Please enter 'yes' or 'no'.")

                # If the greenhouse requirement was changed from "yes" to "no", remove greenhouse alert
                if current_values[4].lower() == "yes" and new_value.lower() == "no":
                    # Remove existing greenhouse alert
                    self.remove_alert(current_values[1])  

                # If the greenhouse requirement was changed from "no" to "yes", check if we need to add an alert
                elif current_values[4].lower() == "no" and new_value.lower() == "yes":
                    current_month = datetime.datetime.now().month
                    if current_month >= 10 or current_month <= 5:
                        self.alerts_listbox.insert(tk.END, f"GREENHOUSE ALERT: Plant '{current_values[1]}' now requires a greenhouse. Consider moving it in.")            
                        
            # Updating Supplier field (User must select from dropdown)
            elif selected_field == "Supplier":
                suppliers = [self.supplier_tree.item(child)['values'][0] for child in self.supplier_tree.get_children()]
                supplier_selection_window = tk.Toplevel(self)
                supplier_selection_window.title("Select Supplier")
                supplier_selection_window.geometry("300x100")
                
                supplier_selection = ttk.Combobox(supplier_selection_window, values=suppliers)
                supplier_selection.set(current_values[5])
                supplier_selection.pack(pady=10)

                def confirm_supplier_selection():
                    nonlocal new_value
                    new_value = supplier_selection.get()
                    supplier_selection_window.destroy()
                    field_selection_window.destroy()
                    self.inventory_tree.item(selected_item[0], values=(*current_values[:fields.index(selected_field)], new_value, *current_values[fields.index(selected_field)+1:]))

                ttk.Button(supplier_selection_window, text="OK", command=confirm_supplier_selection).pack(pady=10)
                self.wait_window(supplier_selection_window)
                return
            
            # Apply updates to the plant entry
            if new_value is not None:
                index = fields.index(selected_field)
                current_values[index] = new_value
                self.inventory_tree.item(selected_item[0], values=current_values)
                
                # Update alerts if the name has changed
                if selected_field == "Name":
                    # Remove alerts for the old name
                    self.remove_alert(old_name)  
                    self.check_low_stock_alert({"name": new_value, "quantity": current_values[3]})

            field_selection_window.destroy()
            self.save_data()

        ttk.Button(field_selection_window, text="OK", command=confirm_field_selection).pack(pady=10)

        ttk.Button(field_selection_window, text="OK", command=confirm_field_selection).pack(pady=10)

    def delete_plant(self):
        selected_item = self.inventory_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No plant selected.")
            return
        self.inventory_tree.delete(selected_item[0])
        self.save_data()

    def add_supplier(self):
        name = simpledialog.askstring("Supplier Name", "Enter supplier name:")
        phone_number = simpledialog.askstring("Supplier Phone Number", "Enter phone number:")
        address = simpledialog.askstring("Supplier Address", "Enter address:")
        new_supplier = (name, phone_number, address)
        self.supplier_tree.insert('', tk.END, values=new_supplier)
        self.save_data()

    def check_greenhouse_alert(self):
        current_month = datetime.datetime.now().month
        greenhouse_plants_exist = False  # Track if any greenhouse-required plants exist

        # Check if any plants require a greenhouse
        if current_month >= 10 or current_month <= 5:
            for child in self.inventory_tree.get_children():
                values = self.inventory_tree.item(child, 'values')
                if values[4].lower() == "yes":
                    greenhouse_plants_exist = True
                    break

        # Remove the alert if it exists and there are no greenhouse plants
        alerts = self.alerts_listbox.get(0, tk.END)
        greenhouse_alert_text = "GREENHOUSE ALERT: Some plants require greenhouse. Consider moving them in."

        if greenhouse_alert_text in alerts and not greenhouse_plants_exist:
            self.alerts_listbox.delete(alerts.index(greenhouse_alert_text))

        # Add the alert if there are greenhouse plants and it is the right season
        elif greenhouse_plants_exist and greenhouse_alert_text not in alerts:
            self.alerts_listbox.insert(tk.END, greenhouse_alert_text)

    # Method that removes a supplier from the supplier table and updates the data file
    def remove_supplier(self):
        selected_item = self.supplier_tree.selection()
        if selected_item:
            self.supplier_tree.delete(selected_item[0])  # Remove the selected supplier
            self.save_data()  # Save updated data after deletion

    # Method that allows users to update suppluer information
    def update_supplier(self):
        selected_item = self.supplier_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No supplier selected.")
            return

        # Retrieve the current details of the selected supplier
        current_values = list(self.supplier_tree.item(selected_item[0], 'values'))
        # current_values: [name, phone_number, address]

        # Prompt user for updated supplier details
        new_name = simpledialog.askstring("Update Supplier", "Enter new supplier name:", initialvalue=current_values[0])
        if new_name is None or new_name.strip() == "":
            messagebox.showerror("Error", "Supplier name is required.")
            return

        new_phone = simpledialog.askstring("Update Supplier", "Enter new phone number:", initialvalue=current_values[1])
        if new_phone is None or new_phone.strip() == "":
            messagebox.showerror("Error", "Phone number is required.")
            return

        new_address = simpledialog.askstring("Update Supplier", "Enter new address:", initialvalue=current_values[2])
        if new_address is None or new_address.strip() == "":
            messagebox.showerror("Error", "Address is required.")
            return

        # Store the old supplier name for updating associated plants
        old_supplier_name = current_values[0]

        # Update the supplier record in the treeview
        self.supplier_tree.item(selected_item[0], values=(new_name, new_phone, new_address))

        # Loop through all plants and update supplier name if they were linked to the old supplier
        for child in self.inventory_tree.get_children():
            plant_values = list(self.inventory_tree.item(child, 'values'))
            if plant_values[5] == old_supplier_name:
                # Update supplier name in plant records
                plant_values[5] = new_name  
                self.inventory_tree.item(child, values=plant_values)
        
        # Save the updated supplier and plant data
        self.save_data()
if __name__ == '__main__':
    app = InventoryApp()
    app.mainloop()
