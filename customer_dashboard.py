import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime

class CustomerDashboard:
    def __init__(self, root, db, user_data, logout_callback):
        self.root = root
        self.db = db
        self.user = user_data
        self.logout_callback = logout_callback
        
        self.root.title(f"Khách Hàng: {self.user['full_name']}")
        self.root.geometry("900x650") # Tăng chiều cao để chứa biểu đồ
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        self.setup_header()
        self.setup_tabs()

    def setup_header(self):
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.pack(fill=tk.X)
        
        self.lbl_welcome = ttk.Label(header_frame, text=f"Xin chào, {self.user['full_name']}", font=("Arial", 14, "bold"))
        self.lbl_welcome.pack(side=tk.LEFT)
        ttk.Button(header_frame, text="Đăng xuất", command=self.logout_callback).pack(side=tk.RIGHT)

    def setup_tabs(self):
        tab_control = ttk.Notebook(self.root)
        
        self.tab_booking = ttk.Frame(tab_control)
        self.tab_history = ttk.Frame(tab_control)
        self.tab_profile = ttk.Frame(tab_control)
        
        tab_control.add(self.tab_booking, text='Đặt Sân Mới & Xem Lịch')
        tab_control.add(self.tab_history, text='Lịch Sử Đặt Sân')
        tab_control.add(self.tab_profile, text='Thông Tin Cá Nhân')
        
        tab_control.pack(expand=1, fill="both")
        
        self.build_booking_tab()
        self.build_history_tab()
        self.build_profile_tab()

    def build_booking_tab(self):
        frame = ttk.Frame(self.tab_booking, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # --- KHU VỰC CHỌN THÔNG TIN ---
        grid_frame = ttk.LabelFrame(frame, text="1. Chọn thông tin", padding="15")
        grid_frame.pack(fill=tk.X, pady=5)
        
        # Chọn ngày
        ttk.Label(grid_frame, text="Ngày:").grid(row=0, column=0, padx=5, sticky="e")
        self.date_entry = DateEntry(grid_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=0, column=1, padx=5, sticky="w")
        # Bind sự kiện thay đổi ngày
        self.date_entry.bind("<<DateEntrySelected>>", self.update_visual_schedule)
        
        # Chọn sân
        ttk.Label(grid_frame, text="Sân:").grid(row=0, column=2, padx=5, sticky="e")
        self.courts = self.db.get_active_courts()
        court_names = [f"{c['id']} - {c['name']}" for c in self.courts]
        self.cbo_court = ttk.Combobox(grid_frame, values=court_names, state="readonly")
        self.cbo_court.grid(row=0, column=3, padx=5, sticky="w")
        if court_names: self.cbo_court.current(0)
        # Bind sự kiện thay đổi sân
        self.cbo_court.bind("<<ComboboxSelected>>", self.update_visual_schedule)

        # --- KHU VỰC BIỂU ĐỒ TRỰC QUAN (TIMELINE) ---
        viz_frame = ttk.LabelFrame(frame, text="2. Tình trạng sân (05:00 - 22:00)", padding="10")
        viz_frame.pack(fill=tk.X, pady=10)
        
        # Canvas vẽ lịch
        self.canvas_width = 800
        self.canvas_height = 80
        self.schedule_canvas = tk.Canvas(viz_frame, width=self.canvas_width, height=self.canvas_height, bg="white", highlightthickness=1, highlightbackground="#ccc")
        self.schedule_canvas.pack(pady=5)
        
        # Chú thích màu
        legend_frame = ttk.Frame(viz_frame)
        legend_frame.pack(fill=tk.X)
        tk.Label(legend_frame, text="🟩 Trống", fg="green").pack(side=tk.LEFT, padx=10)
        tk.Label(legend_frame, text="🟨 Chờ duyệt", fg="#d4ac0d").pack(side=tk.LEFT, padx=10)
        tk.Label(legend_frame, text="🟥 Đã đặt/Kín", fg="red").pack(side=tk.LEFT, padx=10)

        # --- KHU VỰC CHỌN GIỜ & ĐẶT ---
        action_frame = ttk.LabelFrame(frame, text="3. Chọn giờ đặt", padding="15")
        action_frame.pack(fill=tk.X, pady=5)
        
        time_values = [f"{h:02d}:00" for h in range(5, 23)] + [f"{h:02d}:30" for h in range(5, 23)]
        time_values.sort()
        
        ttk.Label(action_frame, text="Bắt đầu:").grid(row=0, column=0, padx=5)
        self.cbo_start = ttk.Combobox(action_frame, values=time_values, state="readonly", width=10)
        self.cbo_start.grid(row=0, column=1, padx=5)
        
        ttk.Label(action_frame, text="Kết thúc:").grid(row=0, column=2, padx=5)
        self.cbo_end = ttk.Combobox(action_frame, values=time_values, state="readonly", width=10)
        self.cbo_end.grid(row=0, column=3, padx=5)
        
        ttk.Button(action_frame, text="Kiểm tra giá & Đặt", command=self.check_price_availability).grid(row=0, column=4, padx=20)
        
        self.lbl_price_result = ttk.Label(frame, text="", font=("Arial", 12), foreground="blue")
        self.lbl_price_result.pack(pady=5)
        
        self.btn_confirm = ttk.Button(frame, text="XÁC NHẬN ĐẶT SÂN", command=self.confirm_booking, state=tk.DISABLED)
        self.btn_confirm.pack(pady=5)

        # Vẽ lịch lần đầu
        self.update_visual_schedule()

    def update_visual_schedule(self, event=None):
        """Vẽ lại biểu đồ lịch dựa trên ngày và sân đã chọn"""
        self.schedule_canvas.delete("all") # Xóa cũ
        
        if not self.cbo_court.get(): return

        court_id = int(self.cbo_court.get().split(" - ")[0])
        date_str = str(self.date_entry.get_date())
        
        # Lấy dữ liệu từ DB
        bookings = self.db.get_court_schedule(court_id, date_str)
        
        # Thông số vẽ
        start_hour = 5.0
        end_hour = 22.0
        total_hours = end_hour - start_hour
        w = self.canvas_width
        h = self.canvas_height
        px_per_hour = w / total_hours
        
        # Vẽ khung giờ (Grid lines)
        for i in range(int(start_hour), int(end_hour) + 1):
            x = (i - start_hour) * px_per_hour
            self.schedule_canvas.create_line(x, 0, x, h, fill="#eee")
            self.schedule_canvas.create_text(x + 2, h - 10, text=str(i), anchor="w", font=("Arial", 8), fill="#555")

        # Vẽ các booking
        for b in bookings:
            # Tính tọa độ x bắt đầu và x kết thúc
            x1 = (b['start'] - start_hour) * px_per_hour
            x2 = (b['end'] - start_hour) * px_per_hour
            
            # Chọn màu dựa trên trạng thái
            color = "red" # Mặc định là đã đặt
            status_text = "Đã đặt"
            
            if b['status'] == 'Chờ xác nhận':
                color = "#f1c40f" # Vàng đậm
                status_text = "Chờ duyệt"
            elif b['status'] in ['Hoàn thành', 'Đã xác nhận', 'Đã check-in']:
                color = "#e74c3c" # Đỏ
            
            # Vẽ hình chữ nhật
            # Giới hạn không vẽ ra ngoài canvas
            x1 = max(0, x1)
            x2 = min(w, x2)
            
            self.schedule_canvas.create_rectangle(x1, 10, x2, h-20, fill=color, outline="white")
            
            # Hiển thị text ở giữa block nếu đủ rộng
            if x2 - x1 > 30:
                mid_x = (x1 + x2) / 2
                self.schedule_canvas.create_text(mid_x, h/2 - 5, text=status_text, font=("Arial", 8), fill="white")

    def check_price_availability(self):
        if not self.cbo_court.get() or not self.cbo_start.get() or not self.cbo_end.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn đầy đủ thông tin")
            return

        start_str = self.cbo_start.get()
        end_str = self.cbo_end.get()
        
        if start_str >= end_str:
            messagebox.showerror("Lỗi", "Giờ kết thúc phải lớn hơn giờ bắt đầu")
            return

        court_id = int(self.cbo_court.get().split(" - ")[0])
        date_obj = self.date_entry.get_date()
        date_str = str(date_obj)

        # DB check conflict (Validation tầng dữ liệu)
        if self.db.check_conflict(court_id, date_str, start_str, end_str):
            self.lbl_price_result.config(text="❌ Sân đã có người đặt trong khung giờ này!", foreground="red")
            self.btn_confirm.config(state=tk.DISABLED)
        else:
            price = self.db.calculate_price(court_id, start_str, end_str, date_obj)
            self.current_price = price
            self.lbl_price_result.config(text=f"✅ Sân trống! Tổng tiền tạm tính: {int(price):,} VND", foreground="green")
            self.btn_confirm.config(state=tk.NORMAL)

    def confirm_booking(self):
        confirm = messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn đặt sân với giá {int(self.current_price):,} VND?")
        if confirm:
            court_id = int(self.cbo_court.get().split(" - ")[0])
            date_str = str(self.date_entry.get_date())
            start = self.cbo_start.get()
            end = self.cbo_end.get()
            
            success, msg = self.db.create_booking(self.user['id'], court_id, date_str, start, end, self.current_price)
            if success:
                messagebox.showinfo("Thành công", msg)
                self.update_visual_schedule() # Cập nhật lại biểu đồ ngay lập tức
                self.refresh_history()
                self.btn_confirm.config(state=tk.DISABLED)
                self.lbl_price_result.config(text="")
            else:
                messagebox.showerror("Lỗi", msg)

    def build_history_tab(self):
        frame = ttk.Frame(self.tab_history, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("id", "court", "date", "time", "price", "status")
        self.tree_hist = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        self.tree_hist.heading("id", text="ID")
        self.tree_hist.heading("court", text="Sân")
        self.tree_hist.heading("date", text="Ngày")
        self.tree_hist.heading("time", text="Giờ chơi")
        self.tree_hist.heading("price", text="Tổng tiền")
        self.tree_hist.heading("status", text="Trạng thái")
        
        self.tree_hist.column("id", width=50)
        self.tree_hist.column("court", width=150)
        self.tree_hist.column("status", width=100)
        
        self.tree_hist.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree_hist.yview)
        self.tree_hist.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        # Logic Hủy Booking (Theo yêu cầu: Chỉ hủy khi chưa duyệt)
        ttk.Button(btn_frame, text="Hủy Booking (Chỉ Chờ xác nhận)", command=self.cancel_booking_action).pack(side=tk.RIGHT)
        ttk.Button(btn_frame, text="Làm mới", command=self.refresh_history).pack(side=tk.LEFT)
        
        self.refresh_history()

    def refresh_history(self):
        for item in self.tree_hist.get_children():
            self.tree_hist.delete(item)
            
        bookings = self.db.get_user_bookings(self.user['id'])
        for b in bookings:
            time_range = f"{b['start_time']} - {b['end_time']}"
            price = f"{int(b['total_price']):,}"
            self.tree_hist.insert("", tk.END, values=(b['id'], b['court_name'], b['booking_date'], time_range, price, b['status']))

    def cancel_booking_action(self):
        selected = self.tree_hist.selection()
        if not selected:
            messagebox.showwarning("Chú ý", "Vui lòng chọn một dòng để hủy")
            return
        
        item = self.tree_hist.item(selected[0])
        b_id = item['values'][0]
        status = item['values'][5]
        
        # Kiểm tra đúng logic yêu cầu: "Khách hàng được phép Hủy lịch nếu Admin chưa duyệt"
        if status != 'Chờ xác nhận':
            messagebox.showerror("Lỗi", "Bạn chỉ có thể hủy đơn khi trạng thái là 'Chờ xác nhận'.\nNếu đã duyệt, vui lòng liên hệ Admin.")
            return
            
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn hủy booking này?"):
            if self.db.cancel_booking(b_id):
                messagebox.showinfo("Thành công", "Đã hủy booking.")
                self.refresh_history()
                self.update_visual_schedule() # Cập nhật lại biểu đồ nếu đang xem ngày đó
            else:
                messagebox.showerror("Lỗi", "Không thể hủy.")

    def build_profile_tab(self):
        frame = ttk.Frame(self.tab_profile, padding="30")
        frame.pack(fill=tk.BOTH, expand=True)

        # Thông tin cơ bản
        info_frame = ttk.LabelFrame(frame, text="Cập nhật thông tin", padding="20")
        info_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(info_frame, text="Họ và Tên:").grid(row=0, column=0, sticky="e", pady=5)
        self.entry_name = ttk.Entry(info_frame, width=30)
        self.entry_name.grid(row=0, column=1, sticky="w", pady=5, padx=10)
        self.entry_name.insert(0, self.user['full_name'])
        
        ttk.Label(info_frame, text="Số điện thoại:").grid(row=1, column=0, sticky="e", pady=5)
        self.entry_phone = ttk.Entry(info_frame, width=30)
        self.entry_phone.grid(row=1, column=1, sticky="w", pady=5, padx=10)
        self.entry_phone.insert(0, self.user['phone_number'])
        
        ttk.Button(info_frame, text="Lưu thay đổi", command=self.update_info).grid(row=2, column=1, sticky="w", pady=15)
        
        # Đổi mật khẩu
        pwd_frame = ttk.LabelFrame(frame, text="Đổi mật khẩu", padding="20")
        pwd_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(pwd_frame, text="Mật khẩu cũ:").grid(row=0, column=0, sticky="e", pady=5)
        self.entry_old_pass = ttk.Entry(pwd_frame, width=30, show="*")
        self.entry_old_pass.grid(row=0, column=1, sticky="w", pady=5, padx=10)
        
        ttk.Label(pwd_frame, text="Mật khẩu mới:").grid(row=1, column=0, sticky="e", pady=5)
        self.entry_new_pass = ttk.Entry(pwd_frame, width=30, show="*")
        self.entry_new_pass.grid(row=1, column=1, sticky="w", pady=5, padx=10)
        
        ttk.Label(pwd_frame, text="Xác nhận MK:").grid(row=2, column=0, sticky="e", pady=5)
        self.entry_confirm_pass = ttk.Entry(pwd_frame, width=30, show="*")
        self.entry_confirm_pass.grid(row=2, column=1, sticky="w", pady=5, padx=10)
        
        ttk.Button(pwd_frame, text="Đổi mật khẩu", command=self.update_password).grid(row=3, column=1, sticky="w", pady=15)

    def update_info(self):
        new_name = self.entry_name.get()
        new_phone = self.entry_phone.get()
        if not new_name or not new_phone:
            messagebox.showerror("Lỗi", "Không được để trống")
            return
            
        success, msg = self.db.update_user_profile(self.user['id'], new_name, new_phone)
        if success:
            messagebox.showinfo("Thành công", msg)
            self.user['full_name'] = new_name
            self.user['phone_number'] = new_phone
            self.lbl_welcome.config(text=f"Xin chào, {new_name}")
        else:
            messagebox.showerror("Lỗi", msg)

    def update_password(self):
        old = self.entry_old_pass.get()
        new = self.entry_new_pass.get()
        confirm = self.entry_confirm_pass.get()
        
        if not old or not new:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ")
            return
        if new != confirm:
            messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp")
            return
            
        success, msg = self.db.change_password(self.user['id'], old, new)
        if success:
            messagebox.showinfo("Thành công", msg)
            self.entry_old_pass.delete(0, tk.END)
            self.entry_new_pass.delete(0, tk.END)
            self.entry_confirm_pass.delete(0, tk.END)
        else:
            messagebox.showerror("Lỗi", msg)