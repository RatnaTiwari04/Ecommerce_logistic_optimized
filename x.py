import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import math
import random
from datetime import datetime, timedelta

# ----------------------
# Core Data Models
# ----------------------

class Package:
    def __init__(self, id, destination, priority, weight):
        self.id = id
        self.destination = destination  # (x, y) coordinates
        self.priority = priority  # 1 (highest) to 3 (lowest)
        self.weight = weight
        self.status = "sorting"  # sorting, processed, in-transit, delivered
        self.assigned_vehicle = None
        self.pickup_time = None
        self.estimated_delivery = None
        self.actual_delivery = None
    
    def __repr__(self):
        return f"Package({self.id}, priority={self.priority}, status={self.status})"


class Vehicle:
    def __init__(self, id, capacity=100, speed=50):
        self.id = id
        self.capacity = capacity  # Maximum weight capacity
        self.speed = speed  # Movement speed
        self.location = (0, 0)  # Start at depot
        self.status = "available"  # available, loading, in-transit, returning
        self.packages = []
    
    def __repr__(self):
        return f"Vehicle({self.id}, {self.status}, packages={len(self.packages)})"
    
    def calculate_travel_time(self, destination):
        """Calculate travel time to destination in hours"""
        distance = calculate_distance(self.location, destination)
        return distance / self.speed  # Time = distance / speed


# ----------------------
# Logistics System
# ----------------------

class LogisticsSystem:
    def __init__(self):
        self.packages = []
        self.vehicles = []
        self.delivered_packages = []
    
    def add_package(self, package):
        self.packages.append(package)
    
    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)


# ----------------------
# Helper Functions
# ----------------------

def calculate_distance(point1, point2):
    """Calculate Euclidean distance between two points"""
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    return math.sqrt(dx*dx + dy*dy)


# ----------------------
# GUI Application
# ----------------------

class LogisticsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("E-Commerce Logistics System")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Initialize the logistics system
        self.system = LogisticsSystem()
        
        # Initialize variables
        self.vehicle_count = tk.IntVar(value=5)
        self.package_count = tk.IntVar(value=100)
        
        # Setup the user interface
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the main UI framework"""
        # Setup the styles
        self.setup_styles()
        
        # Create main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create tab control
        self.tab_control = ttk.Notebook(main_frame)
        self.tab_control.pack(expand=1, fill="both")
        
        # Create tabs
        self.setup_tab = ttk.Frame(self.tab_control)
        self.packages_tab = ttk.Frame(self.tab_control)
        self.vehicles_tab = ttk.Frame(self.tab_control)
        self.tracking_tab = ttk.Frame(self.tab_control)
        
        # Add tabs to notebook
        self.tab_control.add(self.setup_tab, text="System Setup")
        self.tab_control.add(self.packages_tab, text="Packages")
        self.tab_control.add(self.vehicles_tab, text="Vehicles")
        self.tab_control.add(self.tracking_tab, text="Package Tracking")
        
        # Initialize each tab
        self.init_setup_tab()
        self.init_packages_tab()
        self.init_vehicles_tab()
        self.init_tracking_tab()
    
    def setup_styles(self):
        """Set up the TTK styles for consistent UI appearance"""
        style = ttk.Style()
        style.configure("TLabel", font=("Arial", 11))
        style.configure("TButton", font=("Arial", 11))
        style.configure("Bold.TLabel", font=("Arial", 11, "bold"))
        style.configure("Header.TLabel", font=("Arial", 14, "bold"))
        style.configure("Success.TLabel", foreground="green", font=("Arial", 11))
        style.configure("Error.TLabel", foreground="red", font=("Arial", 11))
    
    # ----------------------
    # Setup Tab
    # ----------------------
    
    def init_setup_tab(self):
        """Initialize the system setup tab"""
        frame = ttk.Frame(self.setup_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(frame, text="System Configuration", style="Header.TLabel").pack(pady=(0, 20))
        
        # Vehicle setup
        vehicle_frame = ttk.LabelFrame(frame, text="Vehicles", padding="10")
        vehicle_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(vehicle_frame, text="Number of Vehicles:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Spinbox(vehicle_frame, from_=1, to=20, textvariable=self.vehicle_count, width=5).grid(
            row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Package setup
        package_frame = ttk.LabelFrame(frame, text="Packages", padding="10")
        package_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(package_frame, text="Number of Packages:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Spinbox(package_frame, from_=1, to=500, textvariable=self.package_count, width=5).grid(
            row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Action buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="Initialize System", command=self.initialize_system).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear System", command=self.clear_system).pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.setup_status_label = ttk.Label(frame, text="")
        self.setup_status_label.pack(fill=tk.X, pady=10)
    
    # ----------------------
    # Packages Tab
    # ----------------------
    
    def init_packages_tab(self):
        """Initialize the packages management tab"""
        frame = ttk.Frame(self.packages_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(frame, text="Package Management", style="Header.TLabel").pack(pady=(0, 20))
        
        # Filter controls
        filter_frame = ttk.Frame(frame)
        filter_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(filter_frame, text="Filter by Status:").pack(side=tk.LEFT, padx=5)
        
        self.status_filter = ttk.Combobox(filter_frame, values=["All", "sorting", "processed", "in-transit", "delivered"])
        self.status_filter.pack(side=tk.LEFT, padx=5)
        self.status_filter.current(0)
        self.status_filter.bind("<<ComboboxSelected>>", self.filter_packages)
        
        ttk.Button(filter_frame, text="Refresh", command=self.refresh_packages).pack(side=tk.RIGHT, padx=5)
        
        # Packages table
        table_frame = ttk.Frame(frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create treeview
        columns = ("ID", "Destination", "Priority", "Weight", "Status", "Vehicle", "Delivery Time")
        self.packages_tree = ttk.Treeview(table_frame, columns=columns, yscrollcommand=scrollbar.set, selectmode="browse")
        
        # Configure columns
        self.packages_tree.column("#0", width=0, stretch=tk.NO)
        self.packages_tree.column("ID", anchor=tk.W, width=80)
        self.packages_tree.column("Destination", anchor=tk.W, width=120)
        self.packages_tree.column("Priority", anchor=tk.CENTER, width=80)
        self.packages_tree.column("Weight", anchor=tk.CENTER, width=80)
        self.packages_tree.column("Status", anchor=tk.W, width=100)
        self.packages_tree.column("Vehicle", anchor=tk.W, width=80)
        self.packages_tree.column("Delivery Time", anchor=tk.W, width=150)
        
        # Configure headings
        for col in columns:
            self.packages_tree.heading(col, text=col, anchor=tk.W if col != "Priority" and col != "Weight" else tk.CENTER)
        
        scrollbar.config(command=self.packages_tree.yview)
        self.packages_tree.pack(fill=tk.BOTH, expand=True)
    
    # ----------------------
    # Vehicles Tab
    # ----------------------
    
    def init_vehicles_tab(self):
        """Initialize the vehicles management tab"""
        frame = ttk.Frame(self.vehicles_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(frame, text="Vehicle Management", style="Header.TLabel").pack(pady=(0, 20))
        
        # Filter controls
        filter_frame = ttk.Frame(frame)
        filter_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(filter_frame, text="Filter by Status:").pack(side=tk.LEFT, padx=5)
        
        self.vehicle_status_filter = ttk.Combobox(filter_frame, values=["All", "available", "loading", "in-transit", "returning"])
        self.vehicle_status_filter.pack(side=tk.LEFT, padx=5)
        self.vehicle_status_filter.current(0)
        self.vehicle_status_filter.bind("<<ComboboxSelected>>", self.filter_vehicles)
        
        ttk.Button(filter_frame, text="Refresh", command=self.refresh_vehicles).pack(side=tk.RIGHT, padx=5)
        
        # Vehicles table
        table_frame = ttk.Frame(frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create treeview
        columns = ("ID", "Capacity", "Speed", "Location", "Status", "Packages")
        self.vehicles_tree = ttk.Treeview(table_frame, columns=columns, yscrollcommand=scrollbar.set, selectmode="browse")
        
        # Configure columns
        self.vehicles_tree.column("#0", width=0, stretch=tk.NO)
        self.vehicles_tree.column("ID", anchor=tk.W, width=80)
        self.vehicles_tree.column("Capacity", anchor=tk.CENTER, width=80)
        self.vehicles_tree.column("Speed", anchor=tk.CENTER, width=80)
        self.vehicles_tree.column("Location", anchor=tk.W, width=120)
        self.vehicles_tree.column("Status", anchor=tk.W, width=100)
        self.vehicles_tree.column("Packages", anchor=tk.CENTER, width=80)
        
        # Configure headings
        for col in columns:
            self.vehicles_tree.heading(col, text=col, anchor=tk.W if col not in ["Capacity", "Speed", "Packages"] else tk.CENTER)
        
        scrollbar.config(command=self.vehicles_tree.yview)
        self.vehicles_tree.pack(fill=tk.BOTH, expand=True)
        
        # Vehicle details section
        details_frame = ttk.LabelFrame(frame, text="Vehicle Details", padding="10")
        details_frame.pack(fill=tk.X, pady=10)
        
        # Add selection event
        self.vehicles_tree.bind("<<TreeviewSelect>>", self.show_vehicle_details)
        
        # Details text area
        self.vehicle_details_area = scrolledtext.ScrolledText(details_frame, wrap=tk.WORD, height=5)
        self.vehicle_details_area.pack(fill=tk.BOTH, expand=True)
    
    # ----------------------
    # Tracking Tab
    # ----------------------
    
    def init_tracking_tab(self):
        """Initialize the package tracking tab"""
        frame = ttk.Frame(self.tracking_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(frame, text="Package Tracking", style="Header.TLabel").pack(pady=(0, 20))
        
        # Search section
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(search_frame, text="Package ID:").pack(side=tk.LEFT, padx=5)
        
        self.package_id_entry = ttk.Entry(search_frame, width=20)
        self.package_id_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_frame, text="Track Package", command=self.track_package).pack(side=tk.LEFT, padx=5)
        
        # Tracking result section
        result_frame = ttk.LabelFrame(frame, text="Tracking Information", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.tracking_info_area = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, height=10)
        self.tracking_info_area.pack(fill=tk.BOTH, expand=True)
        
        # Map visualization section
        map_frame = ttk.LabelFrame(frame, text="Package Location", padding="10")
        map_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.map_canvas = tk.Canvas(map_frame, bg="white")
        self.map_canvas.pack(fill=tk.BOTH, expand=True)
    
    # ----------------------
    # System Operations
    # ----------------------
    
    def initialize_system(self):
        """Initialize the logistics system with vehicles and packages"""
        try:
            # Clear existing system
            self.clear_system()
            
            # Create new system
            self.system = LogisticsSystem()
            
            # Add vehicles with increasing capacity and speed
            for i in range(self.vehicle_count.get()):
                capacity = 100 + i * 20  # Base capacity + increment
                speed = 50 + i * 5       # Base speed + increment
                self.system.add_vehicle(Vehicle(f"V{i+1}", capacity=capacity, speed=speed))
            
            # Generate random packages
            for i in range(self.package_count.get()):
                # Random coordinates within range
                x = random.uniform(-50, 50)
                y = random.uniform(-50, 50)
                
                # Random priority (1-3) and weight
                priority = random.randint(1, 3)  # 1=highest, 3=lowest
                weight = random.uniform(0.5, 10)
                
                # Create package
                package = Package(f"P{i+1}", (x, y), priority, weight)
                
                # Set estimated delivery time (random for demo)
                package.estimated_delivery = datetime.now() + timedelta(hours=random.uniform(1, 5))
                
                # Add to system
                self.system.add_package(package)
            
            # Update status
            self.setup_status_label.config(
                text=f"System initialized with {self.vehicle_count.get()} vehicles and {self.package_count.get()} packages", 
                style="Success.TLabel"
            )
            
            # Refresh displays
            self.refresh_packages()
            self.refresh_vehicles()
            
            # Update tab labels with counts
            self.tab_control.tab(1, text=f"Packages ({len(self.system.packages)})")
            self.tab_control.tab(2, text=f"Vehicles ({len(self.system.vehicles)})")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize system: {str(e)}")
            self.setup_status_label.config(text=f"Error: {str(e)}", style="Error.TLabel")
    
    def clear_system(self):
        """Clear the logistics system"""
        self.system = LogisticsSystem()
        self.setup_status_label.config(text="System cleared", style="Success.TLabel")
        
        # Refresh displays
        self.refresh_packages()
        self.refresh_vehicles()
        
        # Update tab labels
        self.tab_control.tab(1, text="Packages (0)")
        self.tab_control.tab(2, text="Vehicles (0)")
        
        # Clear tracking display
        self.tracking_info_area.delete(1.0, tk.END)
        self.map_canvas.delete("all")
    
    # ----------------------
    # Package Management
    # ----------------------
    
    def refresh_packages(self):
        """Refresh the packages table display"""
        # Clear existing items
        for item in self.packages_tree.get_children():
            self.packages_tree.delete(item)
        
        # Get selected filter
        filter_status = self.status_filter.get()
        
        # Add active packages
        for package in self.system.packages:
            if filter_status == "All" or package.status == filter_status:
                self.packages_tree.insert("", tk.END, values=(
                    package.id, 
                    f"({package.destination[0]:.1f}, {package.destination[1]:.1f})",
                    package.priority,
                    f"{package.weight:.1f}",
                    package.status,
                    package.assigned_vehicle or "-",
                    "-"
                ))
        
        # Add delivered packages
        for package in self.system.delivered_packages:
            if filter_status == "All" or package.status == filter_status:
                delivery_time = package.actual_delivery.strftime("%Y-%m-%d %H:%M:%S") if package.actual_delivery else "-"
                self.packages_tree.insert("", tk.END, values=(
                    package.id, 
                    f"({package.destination[0]:.1f}, {package.destination[1]:.1f})",
                    package.priority,
                    f"{package.weight:.1f}",
                    package.status,
                    package.assigned_vehicle or "-",
                    delivery_time
                ))
    
    def filter_packages(self, event=None):
        """Filter packages based on selected status"""
        self.refresh_packages()
    
    # ----------------------
    # Vehicle Management
    # ----------------------
    
    def refresh_vehicles(self):
        """Refresh the vehicles table display"""
        # Clear existing items
        for item in self.vehicles_tree.get_children():
            self.vehicles_tree.delete(item)
        
        # Get selected filter
        filter_status = self.vehicle_status_filter.get()
        
        # Add vehicles matching filter
        for vehicle in self.system.vehicles:
            if filter_status == "All" or vehicle.status == filter_status:
                self.vehicles_tree.insert("", tk.END, values=(
                    vehicle.id, 
                    vehicle.capacity,
                    vehicle.speed,
                    f"({vehicle.location[0]:.1f}, {vehicle.location[1]:.1f})",
                    vehicle.status,
                    len(vehicle.packages)
                ))
    
    def filter_vehicles(self, event=None):
        """Filter vehicles based on selected status"""
        self.refresh_vehicles()
    
    def show_vehicle_details(self, event=None):
        """Show details for the selected vehicle"""
        # Get selected item
        selection = self.vehicles_tree.selection()
        if not selection:
            return
        
        # Get vehicle ID 
        vehicle_id = self.vehicles_tree.item(selection[0])["values"][0]
        
        # Find the vehicle object
        vehicle = next((v for v in self.system.vehicles if v.id == vehicle_id), None)
        if not vehicle:
            return
        
        # Clear details area
        self.vehicle_details_area.delete(1.0, tk.END)
        
        # Format vehicle details
        details = f"ID: {vehicle.id}\n"
        details += f"Status: {vehicle.status}\n"
        details += f"Capacity: {vehicle.capacity}\n"
        details += f"Speed: {vehicle.speed}\n"
        details += f"Location: ({vehicle.location[0]:.1f}, {vehicle.location[1]:.1f})\n\n"
        
        details += f"Assigned Packages ({len(vehicle.packages)}):\n"
        for package in vehicle.packages:
            details += f"  - {package.id}: Priority {package.priority}, Weight {package.weight:.1f}\n"
        
        self.vehicle_details_area.insert(tk.END, details)
    
    # ----------------------
    # Package Tracking
    # ----------------------
    
    def track_package(self):
        """Track a package by ID"""
        package_id = self.package_id_entry.get().strip()
        if not package_id:
            messagebox.showinfo("Info", "Please enter a package ID")
            return
        
        # Search for the package in active and delivered packages
        package = next((p for p in self.system.packages if p.id == package_id), None)
        if not package:
            package = next((p for p in self.system.delivered_packages if p.id == package_id), None)
        
        if not package:
            messagebox.showinfo("Info", f"Package {package_id} not found")
            return
        
        # Clear tracking info area
        self.tracking_info_area.delete(1.0, tk.END)
        
        # Format package tracking information
        info = f"Package ID: {package.id}\n"
        info += f"Status: {package.status}\n"
        info += f"Destination: ({package.destination[0]:.1f}, {package.destination[1]:.1f})\n"
        info += f"Priority: {package.priority}\n"
        info += f"Weight: {package.weight:.1f}\n"
        
        if package.assigned_vehicle:
            info += f"Assigned Vehicle: {package.assigned_vehicle}\n"
        
        if package.pickup_time:
            info += f"Pickup Time: {package.pickup_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        if package.estimated_delivery:
            info += f"Estimated Delivery: {package.estimated_delivery.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        if package.actual_delivery:
            info += f"Actual Delivery: {package.actual_delivery.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            # Determine if delivered on time
            if package.estimated_delivery:
                if package.actual_delivery <= package.estimated_delivery:
                    info += "Delivery Status: On Time ✓\n"
                else:
                    delta = package.actual_delivery - package.estimated_delivery
                    minutes_late = delta.total_seconds() / 60
                    info += f"Delivery Status: {minutes_late:.0f} minutes late ✗\n"
        
        self.tracking_info_area.insert(tk.END, info)
        
        # Update the map visualization
        self.update_package_map(package)
    
    def update_package_map(self, package):
        """Update the package map visualization"""
        # Clear canvas
        self.map_canvas.delete("all")
        
        # Get canvas dimensions
        width = self.map_canvas.winfo_width()
        height = self.map_canvas.winfo_height()
        
        # Set origin at center
        origin_x = width / 2
        origin_y = height / 2
        
        # Draw coordinate axes
        self.map_canvas.create_line(0, origin_y, width, origin_y, fill="gray", dash=(4, 4))
        self.map_canvas.create_line(origin_x, 0, origin_x, height, fill="gray", dash=(4, 4))
        
        # Scale factor for visualization
        scale = min(width, height) / 150
        
        # Draw depot
        depot_x = origin_x
        depot_y = origin_y
        self.map_canvas.create_rectangle(depot_x-5, depot_y-5, depot_x+5, depot_y+5, fill="blue")
        self.map_canvas.create_text(depot_x, depot_y-15, text="Depot", fill="blue")
        
        # Draw package destination
        dest_x = origin_x + package.destination[0] * scale
        dest_y = origin_y - package.destination[1] * scale  # Y is inverted in canvas
        
        self.map_canvas.create_oval(dest_x-5, dest_y-5, dest_x+5, dest_y+5, fill="red")
        self.map_canvas.create_text(dest_x, dest_y-15, text=f"{package.id}", fill="red")
        
        # Draw route line from depot to destination
        self.map_canvas.create_line(depot_x, depot_y, dest_x, dest_y, fill="green", arrow=tk.LAST)
        
        # Draw coordinates
        self.map_canvas.create_text(
            dest_x, dest_y+15, 
            text=f"({package.destination[0]:.1f}, {package.destination[1]:.1f})", 
            fill="black"
        )


# ----------------------
# Application Entry Point
# ----------------------

def main():
    root = tk.Tk()
    app = LogisticsApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()