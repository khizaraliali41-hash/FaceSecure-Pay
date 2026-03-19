import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import cv2
import os
from database import get_all_users, get_monthly_revenue

class AdminDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Configuration ---
        self.title("FaceSecure Pay | Enterprise Admin Suite")
        self.geometry("1200x900") 
        ctk.set_appearance_mode("Dark")

        # --- Theme Configuration ---
        self.bg_color = "#121212"
        self.card_color = "#1e1e1e"
        self.accent_color = "#3a7ebf"

        # Layout configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR NAVIGATION ---
        self.sidebar_frame = ctk.CTkFrame(self, width=240, fg_color="#181818", corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="FACSECURE PAY", 
                                       font=ctk.CTkFont(size=20, weight="bold"), text_color=self.accent_color)
        self.logo_label.pack(pady=30)

        # User Enrollment Section
        self.reg_label = ctk.CTkLabel(self.sidebar_frame, text="USER ENROLLMENT", font=ctk.CTkFont(size=12, weight="bold"))
        self.reg_label.pack(pady=(20, 5))
        
        self.id_entry = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Enter Unique User ID")
        self.id_entry.pack(pady=10, padx=20)
        
        self.reg_button = ctk.CTkButton(self.sidebar_frame, text="Initialize Camera", 
                                        fg_color=self.accent_color, command=self.start_registration)
        self.reg_button.pack(pady=10, padx=20)

        # --- MAIN ANALYTICS CONTAINER ---
        # Scrollable container to ensure responsiveness for large datasets
        self.main_container = ctk.CTkScrollableFrame(self, fg_color=self.bg_color) 
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.header = ctk.CTkLabel(self.main_container, text="System Intelligence Dashboard", 
                                   font=ctk.CTkFont(size=26, weight="bold"))
        self.header.pack(pady=(10, 20), anchor="w")

        # --- TELEMETRY CARDS ---
        self.stats_row = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.stats_row.pack(fill="x", pady=10)

        users_list = get_all_users()
        self.create_stat_card(self.stats_row, "TOTAL REGISTERED USERS", f"{len(users_list)}")
        self.create_stat_card(self.stats_row, "CORE SYSTEM STATUS", "OPERATIONAL")

        # --- REVENUE DATA VISUALIZATION ---
        self.graph_frame = ctk.CTkFrame(self.main_container, fg_color=self.card_color, corner_radius=15)
        self.graph_frame.pack(fill="x", pady=20)
        self.show_revenue_graph()

        # --- USER MANAGEMENT DATA GRID ---
        self.table_header = ctk.CTkLabel(self.main_container, text="Financial Integrity & Balances", 
                                         font=ctk.CTkFont(size=20, weight="bold"))
        self.table_header.pack(pady=(20, 10), anchor="w")

        self.table_frame = ctk.CTkFrame(self.main_container, fg_color=self.card_color, corner_radius=15)
        self.table_frame.pack(fill="both", expand=True, pady=10)

        self.create_user_table(users_list)

    def create_stat_card(self, parent, title, value):
        """Generates a high-level telemetry card."""
        card = ctk.CTkFrame(parent, width=220, height=100, fg_color=self.card_color, corner_radius=12)
        card.pack(side="left", padx=10)
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(15, 0))
        ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=28, weight="bold"), text_color=self.accent_color).pack()

    def create_user_table(self, users):
        """Builds a dynamic data grid for user account management."""
        headers = ["Identity ID", "Account Holder", "Credit Limit", "Current Balance"]
        for i, head in enumerate(headers):
            lbl = ctk.CTkLabel(self.table_frame, text=head, font=ctk.CTkFont(weight="bold"), text_color="gray")
            lbl.grid(row=0, column=i, padx=20, pady=10, sticky="w")

        # Populate rows with live database records
        for index, user in enumerate(users):
            u_id, name, limit, spent, _ = user
            balance = limit - spent
            
            # Row index incremented to account for header
            ctk.CTkLabel(self.table_frame, text=f"#{u_id}").grid(row=index+1, column=0, padx=20, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=name).grid(row=index+1, column=1, padx=20, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=f"${limit}").grid(row=index+1, column=2, padx=20, pady=5, sticky="w")
            
            # Dynamic color coding for low balance alerts
            bal_color = "#2ecc71" if balance > 10 else "#e74c3c" 
            ctk.CTkLabel(self.table_frame, text=f"${balance}", text_color=bal_color, font=ctk.CTkFont(weight="bold")).grid(row=index+1, column=3, padx=20, pady=5, sticky="w")

    def start_registration(self):
        """Triggers the biometric capture sequence for new identity enrollment."""
        u_id = self.id_entry.get()
        if not u_id: return
        
        if not os.path.exists("photos"): 
            os.makedirs("photos")
            
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            cv2.putText(frame, f"System ID: {u_id} | 'S' to Commit | 'Q' to Cancel", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
            cv2.imshow("Identity Capture Mode", frame)
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('s'):
                cv2.imwrite(f"photos/{u_id}.jpg", frame)
                # Flush representation cache to force re-indexing
                if os.path.exists("photos/representations_vgg_face.pkl"):
                    os.remove("photos/representations_vgg_face.pkl")
                break
            elif key == ord('q'): 
                break
                
        cap.release()
        cv2.destroyAllWindows()

    def show_revenue_graph(self):
        """Renders the monthly revenue analytics chart using Matplotlib."""
        months, revenue = get_monthly_revenue()
        fig, ax = plt.subplots(figsize=(5, 2.5), dpi=100)
        fig.patch.set_facecolor(self.card_color)
        ax.set_facecolor(self.card_color)
        ax.plot(months, revenue, marker='o', color=self.accent_color, linewidth=2)
        ax.tick_params(colors='white', which='both', labelsize=8)
        
        # Style chart spines for high-contrast visibility
        for spine in ax.spines.values(): 
            spine.set_color('white')
            
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10, padx=10, fill="x")