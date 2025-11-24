import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from tkcalendar import DateEntry
from datetime import datetime, timedelta

class ManagerDashboard:
    def __init__(self, root, db, user_data, logout_callback):
        self.root = root
        self.db = db
        self.user = user_data
        self.logout_callback = logout_callback
        
        self.root.title(f"Quản Lý Sân: {self.user['full_name']}")
        self.root.geometry("1100x750")
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        self.setup_header()
        self.setup_tabs()

    def setup_header(self):
        header_frame = ttk.Frame(self.root, padding="15")
        header_frame.pack(fill=tk.X)
        ttk.Label(header_frame, text="HỆ THỐNG QUẢN LÝ SÂN CẦU LÔNG", font=("Arial", 18, "bold"), foreground="#2c3e50").pack(side=tk.LEFT)
        ttk.Button(header_frame, text="Đăng xuất", command=self.logout_callback).pack(side=tk.RIGHT)

    def setup_tabs(self):
        tab_control = ttk.Notebook(self.root)
        
        self.tab_overview = ttk.Frame(tab_control)
        self.tab_bookings = ttk.Frame(tab_control)
        self.tab_courts = ttk.Frame(tab_control)
        self.tab_users = ttk.Frame(tab_control)
        self.tab_stats = ttk.Frame(tab_control)
        
        tab_control.add(self.tab_overview, text='📊 Tổng Quan')
        tab_control.add(self.tab_bookings, text='📅 Booking')
        tab_control.add(self.tab_courts, text='🏟️ Thiết Lập Sân')
        tab_control.add(self.tab_users, text='👥 Khách Hàng')
        tab_control.add(self.tab_stats, text='📈 Doanh Thu')
        
        tab_control.pack(expand=1, fill="both")
        
        self.build_overview_tab()
        self.build_booking_manager()
        self.build_court_manager()
        self.build_user_manager()
        self.build_stats_manager()

    # --- HÀM SẮP XẾP CHUNG CHO MỌI BẢNG (NÂNG CẤP) ---
    def treeview_sort_column(self, tv, col, reverse):
        """
        Hàm sắp xếp bảng chung.
        tv: Treeview widget cần sắp xếp
        col: Cột cần sắp xếp
        reverse: True (Giảm dần) / False (Tăng dần)
        """
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        
        # Xử lý sort số cho cột ID
        if col == 'id':
            try:
                l.sort(key=lambda t: int(t[0]), reverse=reverse)
            except ValueError:
                l.sort(reverse=reverse)
        else:
            l.sort(reverse=reverse)

        # Di chuyển dữ liệu
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        # Đảo chiều cho lần click tiếp theo
        tv.heading(col, command=lambda: self.treeview_sort_column(tv, col, not reverse))

    # --- TAB 1: TỔNG QUAN ---
    def build_overview_tab(self):
        frame = ttk.Frame(self.tab_overview, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill=tk.X, pady=5)
        
        ttk.Label(toolbar, text="Xem lịch ngày:").pack(side=tk.LEFT, padx=5)
        self.date_overview = DateEntry(toolbar, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_overview.pack(side=tk.LEFT, padx=5)
        self.date_overview.bind("<<DateEntrySelected>>", self.load_overview_timeline)
        
        ttk.Button(toolbar, text="🔄 Làm mới", command=self.load_overview_timeline).pack(side=tk.LEFT, padx=10)
        
        legend = ttk.Frame(frame)
        legend.pack(fill=tk.X, pady=5)
        tk.Label(legend, text="Chú thích:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        tk.Label(legend, text="🟨 Chờ xác nhận", fg="#d4ac0d").pack(side=tk.LEFT, padx=10)
        tk.Label(legend, text="🟥 Đã đặt / Check-in", fg="#c0392b").pack(side=tk.LEFT, padx=10)
        tk.Label(legend, text="⬜ Trống", fg="black").pack(side=tk.LEFT, padx=10)

        canvas_frame = ttk.Frame(frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        self.timeline_canvas = tk.Canvas(canvas_frame, bg="white", yscrollcommand=v_scroll.set)
        
        v_scroll.config(command=self.timeline_canvas.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.timeline_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.start_hour = 5
        self.end_hour = 22
        self.hour_width = 60
        self.row_height = 80
        self.header_height = 40
        self.label_width = 120
        
        self.load_overview_timeline()

    def load_overview_timeline(self, event=None):
        self.timeline_canvas.delete("all")
        date_str = str(self.date_overview.get_date())
        courts = self.db.get_active_courts()
        
        if not courts:
            self.timeline_canvas.create_text(400, 50, text="Không có sân nào đang hoạt động", font=("Arial", 12))
            return

        total_hours = self.end_hour - self.start_hour + 1
        canvas_width = self.label_width + (total_hours * self.hour_width) + 50
        canvas_height = self.header_height + (len(courts) * self.row_height) + 50
        
        self.timeline_canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))
        
        # Header
        self.timeline_canvas.create_rectangle(0, 0, canvas_width, self.header_height, fill="#ecf0f1", outline="")
        self.timeline_canvas.create_line(0, self.header_height, canvas_width, self.header_height, fill="#bdc3c7", width=2)
        
        for i in range(total_hours):
            h = self.start_hour + i
            x = self.label_width + (i * self.hour_width)
            self.timeline_canvas.create_line(x, 0, x, canvas_height, fill="#ecf0f1", dash=(2, 4))
            self.timeline_canvas.create_text(x, self.header_height/2, text=f"{h}:00", font=("Arial", 9, "bold"), fill="#2c3e50", anchor="w")

        # Rows
        for idx, court in enumerate(courts):
            y_base = self.header_height + (idx * self.row_height)
            
            self.timeline_canvas.create_rectangle(0, y_base, self.label_width, y_base + self.row_height, fill="#34495e", outline="white")
            self.timeline_canvas.create_text(60, y_base + self.row_height/2, text=court['name'], font=("Arial", 10, "bold"), fill="white", width=100, justify=tk.CENTER)
            self.timeline_canvas.create_line(0, y_base + self.row_height, canvas_width, y_base + self.row_height, fill="#bdc3c7", width=1)

            bookings = self.db.get_court_schedule(court['id'], date_str)
            
            for b in bookings:
                x1 = self.label_width + (b['start'] - self.start_hour) * self.hour_width
                x2 = self.label_width + (b['end'] - self.start_hour) * self.hour_width
                
                bg_color = "#c0392b"
                border_color = "#922b21"
                
                if b['status'] == 'Chờ xác nhận':
                    bg_color = "#f1c40f"
                    border_color = "#d4ac0d"
                
                rect_y1 = y_base + 15
                rect_y2 = y_base + self.row_height - 15
                x1 = max(self.label_width, x1)
                
                self.timeline_canvas.create_rectangle(x1, rect_y1, x2, rect_y2, fill=bg_color, outline=border_color, width=1)
                
                if x2 - x1 > 20:
                    display_name = b['customer_name']
                    self.timeline_canvas.create_text((x1+x2)/2, (rect_y1+rect_y2)/2 - 8, text=display_name, font=("Arial", 8, "bold"), fill="white")
                    status_short = "Chờ duyệt" if b['status'] == 'Chờ xác nhận' else "Đã đặt"
                    self.timeline_canvas.create_text((x1+x2)/2, (rect_y1+rect_y2)/2 + 8, text=status_short, font=("Arial", 7), fill="white")

    # --- TAB 2: QUẢN LÝ BOOKING ---
    def build_booking_manager(self):
        frame = ttk.Frame(self.tab_bookings, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        filter_frame = ttk.Frame(frame)
        filter_frame.pack(fill=tk.X, pady=5)
        ttk.Label(filter_frame, text="Lọc trạng thái:").pack(side=tk.LEFT, padx=5)
        self.cbo_status = ttk.Combobox(filter_frame, values=["Tất cả", "Chờ xác nhận", "Đã xác nhận", "Đã check-in", "Hoàn thành", "Đã hủy"], state="readonly")
        self.cbo_status.current(0)
        self.cbo_status.pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Lọc", command=self.load_bookings).pack(side=tk.LEFT, padx=5)
        
        # Định nghĩa cột
        columns = ("id", "customer", "court", "date", "time", "code", "status")
        headers = {
            "id": "ID", "customer": "Khách hàng", "court": "Sân",
            "date": "Ngày", "time": "Giờ", "code": "Check-in Code", "status": "Trạng thái"
        }
        
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        # Gắn sort cho Booking Tree
        for col in columns:
            self.tree.heading(col, text=headers[col], command=lambda _col=col: self.treeview_sort_column(self.tree, _col, False))
        
        self.tree.column("id", width=40)
        self.tree.column("time", width=100)
        self.tree.column("status", width=80)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        action_frame = ttk.LabelFrame(frame, text="Thao tác", padding="10")
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="✅ Xác nhận", command=lambda: self.change_status("Đã xác nhận")).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="🎫 Check-in", command=lambda: self.change_status("Đã check-in")).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="🏁 Hoàn thành", command=lambda: self.change_status("Hoàn thành")).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="🚫 Hủy bỏ", command=lambda: self.change_status("Đã hủy")).pack(side=tk.LEFT, padx=5)
        
        self.load_bookings()

    def load_bookings(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        status = self.cbo_status.get()
        data = self.db.get_all_bookings(status)
        for b in data:
            time_range = f"{b['start_time']} - {b['end_time']}"
            self.tree.insert("", tk.END, values=(b['id'], b['full_name'], b['court_name'], b['booking_date'], time_range, b['check_in_code'], b['status']))

    def change_status(self, new_status):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chọn dòng", "Vui lòng chọn booking để thao tác")
            return
        item = self.tree.item(selected[0])
        b_id = item['values'][0]
        current_status = item['values'][6]
        if current_status == 'Đã hủy' and new_status != 'Đã hủy':
             messagebox.showerror("Lỗi", "Không thể khôi phục đơn đã hủy")
             return
        if self.db.update_booking_status(b_id, new_status):
            messagebox.showinfo("Thành công", f"Đã cập nhật sang {new_status}")
            self.load_bookings()
            self.load_overview_timeline()
        else:
            messagebox.showerror("Lỗi", "Cập nhật thất bại")

    # --- TAB 3: THIẾT LẬP SÂN ---
    def build_court_manager(self):
        frame = ttk.Frame(self.tab_courts, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        btn_frame = ttk.Frame(frame, padding="5")
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="➕ Thêm Sân Mới", command=self.add_court_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✏️ Sửa / Đổi Trạng Thái", command=self.edit_court_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💲 Bảng Giá", command=self.manage_price_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Xóa Sân", command=self.delete_court_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 Làm mới", command=self.load_courts_list).pack(side=tk.RIGHT, padx=5)

        # Áp dụng Sort cho Court
        columns = ("id", "name", "status", "desc")
        headers = {"id": "ID", "name": "Tên Sân", "status": "Trạng Thái", "desc": "Mô Tả"}
        
        self.tree_courts = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree_courts.heading(col, text=headers[col], command=lambda _col=col: self.treeview_sort_column(self.tree_courts, _col, False))
        
        self.tree_courts.column("id", width=50)
        self.tree_courts.column("name", width=150)
        self.tree_courts.column("status", width=120)
        self.tree_courts.column("desc", width=300)
        
        self.tree_courts.pack(fill=tk.BOTH, expand=True, pady=10)
        self.load_courts_list()

    def manage_price_action(self):
        selected = self.tree_courts.selection()
        if not selected:
            messagebox.showwarning("Lỗi", "Vui lòng chọn sân để chỉnh giá")
            return
        item = self.tree_courts.item(selected[0])
        c_id = item['values'][0]
        c_name = item['values'][1]
        
        price_win = Toplevel(self.root)
        price_win.title(f"Quản Lý Giá: {c_name}")
        price_win.geometry("600x450")
        
        tree_frame = ttk.LabelFrame(price_win, text="Các khung giá hiện tại", padding="10")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        cols = ("id", "time", "price", "type")
        tree_price = ttk.Treeview(tree_frame, columns=cols, show="headings", height=8)
        tree_price.heading("id", text="ID")
        tree_price.heading("time", text="Khung Giờ")
        tree_price.heading("price", text="Giá/Giờ (VND)")
        tree_price.heading("type", text="Áp dụng")
        tree_price.column("id", width=40)
        tree_price.column("time", width=150)
        tree_price.column("price", width=120)
        tree_price.pack(fill=tk.BOTH, expand=True)
        
        def load_prices():
            for i in tree_price.get_children():
                tree_price.delete(i)
            prices = self.db.get_court_prices(c_id)
            for p in prices:
                t_range = f"{p['start']} - {p['end']}"
                type_str = "Cuối tuần (T7-CN)" if p['is_weekend'] else "Ngày thường (T2-T6)"
                price_str = f"{int(p['price']):,}"
                tree_price.insert("", tk.END, values=(p['id'], t_range, price_str, type_str))
        load_prices()
        
        add_frame = ttk.LabelFrame(price_win, text="Thêm khung giá mới", padding="10")
        add_frame.pack(fill=tk.X, padx=10, pady=10)
        
        time_values = [f"{h:02d}:00" for h in range(5, 23)]
        ttk.Label(add_frame, text="Từ:").grid(row=0, column=0, padx=5)
        cbo_start = ttk.Combobox(add_frame, values=time_values, width=8, state="readonly")
        cbo_start.grid(row=0, column=1, padx=5)
        cbo_start.set("05:00")
        ttk.Label(add_frame, text="Đến:").grid(row=0, column=2, padx=5)
        cbo_end = ttk.Combobox(add_frame, values=time_values, width=8, state="readonly")
        cbo_end.grid(row=0, column=3, padx=5)
        cbo_end.set("17:00")
        ttk.Label(add_frame, text="Giá:").grid(row=0, column=4, padx=5)
        entry_price = ttk.Entry(add_frame, width=12)
        entry_price.grid(row=0, column=5, padx=5)
        var_weekend = tk.IntVar()
        chk_weekend = ttk.Checkbutton(add_frame, text="Giá Cuối Tuần?", variable=var_weekend)
        chk_weekend.grid(row=0, column=6, padx=10)
        
        def add_price():
            start = cbo_start.get()
            end = cbo_end.get()
            price_raw = entry_price.get()
            if not price_raw.isdigit():
                messagebox.showerror("Lỗi", "Giá tiền phải là số", parent=price_win)
                return
            if start >= end:
                messagebox.showerror("Lỗi", "Giờ bắt đầu phải nhỏ hơn giờ kết thúc", parent=price_win)
                return
            success, msg = self.db.add_price_rule(c_id, start, end, float(price_raw), var_weekend.get())
            if success:
                messagebox.showinfo("Thành công", msg, parent=price_win)
                load_prices()
            else:
                messagebox.showerror("Lỗi", msg, parent=price_win)
        ttk.Button(add_frame, text="Thêm", command=add_price).grid(row=1, column=0, columnspan=7, pady=10)
        
        def delete_price():
            selected = tree_price.selection()
            if not selected:
                messagebox.showwarning("Lỗi", "Chọn dòng giá để xóa", parent=price_win)
                return
            item = tree_price.item(selected[0])
            p_id = item['values'][0]
            if messagebox.askyesno("Xác nhận", "Xóa khung giá này?", parent=price_win):
                self.db.delete_price_rule(p_id)
                load_prices()
        ttk.Button(price_win, text="Xóa Dòng Đang Chọn", command=delete_price).pack(pady=5)

    def load_courts_list(self):
        for i in self.tree_courts.get_children():
            self.tree_courts.delete(i)
        if hasattr(self.db, 'get_all_courts'):
            courts = self.db.get_all_courts()
            for c in courts:
                self.tree_courts.insert("", tk.END, values=(c['id'], c['name'], c['status'], c['description']))
        else:
            courts = self.db.get_active_courts()
            for c in courts:
                self.tree_courts.insert("", tk.END, values=(c['id'], c['name'], c['status'], c['description']))

    def add_court_action(self):
        add_win = Toplevel(self.root)
        add_win.title("Thêm Sân Mới")
        add_win.geometry("400x300")
        ttk.Label(add_win, text="Tên Sân (VD: Sân 6):").pack(pady=5)
        entry_name = ttk.Entry(add_win, width=40)
        entry_name.pack(pady=5)
        ttk.Label(add_win, text="Mô Tả:").pack(pady=5)
        entry_desc = ttk.Entry(add_win, width=40)
        entry_desc.pack(pady=5)
        ttk.Label(add_win, text="Trạng Thái:").pack(pady=5)
        cbo_status = ttk.Combobox(add_win, values=["Hoạt động", "Bảo trì", "Dừng hoạt động"], state="readonly", width=37)
        cbo_status.current(0)
        cbo_status.pack(pady=5)
        def save():
            name = entry_name.get()
            desc = entry_desc.get()
            status = cbo_status.get()
            if not name:
                messagebox.showerror("Lỗi", "Tên sân không được để trống", parent=add_win)
                return
            success, msg = self.db.add_court(name, desc, status)
            if success:
                messagebox.showinfo("Thành công", msg, parent=add_win)
                self.load_courts_list()
                self.load_overview_timeline() 
                add_win.destroy()
            else:
                messagebox.showerror("Lỗi", msg, parent=add_win)
        ttk.Button(add_win, text="Lưu Sân Mới", command=save).pack(pady=20)

    def edit_court_action(self):
        selected = self.tree_courts.selection()
        if not selected:
            messagebox.showwarning("Lỗi", "Vui lòng chọn sân để sửa")
            return
        item = self.tree_courts.item(selected[0])
        vals = item['values']
        c_id = vals[0]
        edit_win = Toplevel(self.root)
        edit_win.title(f"Sửa Sân ID: {c_id}")
        edit_win.geometry("400x300")
        ttk.Label(edit_win, text="Tên Sân:").pack(pady=5)
        entry_name = ttk.Entry(edit_win, width=40)
        entry_name.insert(0, vals[1])
        entry_name.pack(pady=5)
        ttk.Label(edit_win, text="Mô Tả:").pack(pady=5)
        entry_desc = ttk.Entry(edit_win, width=40)
        entry_desc.insert(0, vals[3])
        entry_desc.pack(pady=5)
        ttk.Label(edit_win, text="Trạng Thái:").pack(pady=5)
        cbo_status = ttk.Combobox(edit_win, values=["Hoạt động", "Bảo trì", "Dừng hoạt động"], state="readonly", width=37)
        cbo_status.set(vals[2])
        cbo_status.pack(pady=5)
        def save():
            name = entry_name.get()
            desc = entry_desc.get()
            status = cbo_status.get()
            success, msg = self.db.update_court(c_id, name, desc, status)
            if success:
                messagebox.showinfo("Thành công", msg, parent=edit_win)
                self.load_courts_list()
                self.load_overview_timeline()
                edit_win.destroy()
            else:
                messagebox.showerror("Lỗi", msg, parent=edit_win)
        ttk.Button(edit_win, text="Cập Nhật", command=save).pack(pady=20)

    def delete_court_action(self):
        selected = self.tree_courts.selection()
        if not selected:
            messagebox.showwarning("Lỗi", "Vui lòng chọn sân để xóa")
            return
        item = self.tree_courts.item(selected[0])
        c_id = item['values'][0]
        name = item['values'][1]
        if messagebox.askyesno("Cảnh báo", f"Bạn có chắc muốn xóa sân '{name}'?\nLưu ý: Chỉ xóa được nếu sân chưa có booking nào."):
            success, msg = self.db.delete_court(c_id)
            if success:
                messagebox.showinfo("Thành công", msg)
                self.load_courts_list()
                self.load_overview_timeline()
            else:
                messagebox.showerror("Lỗi", msg)

    # --- TAB 4: QUẢN LÝ KHÁCH HÀNG (ĐÃ THÊM SORTING) ---
    def build_user_manager(self):
        frame = ttk.Frame(self.tab_users, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill=tk.X, pady=5)
        ttk.Label(search_frame, text="Tìm kiếm (Tên/SĐT):").pack(side=tk.LEFT, padx=5)
        self.entry_search_user = ttk.Entry(search_frame, width=30)
        self.entry_search_user.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Tìm", command=self.search_user_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Hiện tất cả", command=self.load_users).pack(side=tk.LEFT, padx=5)

        columns = ("id", "name", "email", "phone")
        headers = {
            "id": "ID", 
            "name": "Họ Tên", 
            "email": "Email", 
            "phone": "SĐT"
        }
        
        self.tree_users = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        # Gắn sort cho User Tree
        for col in columns:
            self.tree_users.heading(col, text=headers[col], command=lambda _col=col: self.treeview_sort_column(self.tree_users, _col, False))
        
        self.tree_users.column("id", width=50)
        self.tree_users.column("name", width=200)
        
        self.tree_users.pack(fill=tk.BOTH, expand=True)

        btn_frame = ttk.Frame(frame, padding="10")
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="✏️ Sửa thông tin", command=self.edit_user_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔑 Reset Mật khẩu", command=self.reset_password_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📜 Xem lịch sử đặt sân", command=self.view_user_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Xóa Khách Hàng", command=self.delete_user_action).pack(side=tk.RIGHT, padx=5)

        self.load_users()

    def load_users(self):
        for i in self.tree_users.get_children():
            self.tree_users.delete(i)
        users = self.db.get_all_customers()
        for u in users:
            self.tree_users.insert("", tk.END, values=(u['id'], u['full_name'], u['email'], u['phone_number']))

    def search_user_action(self):
        keyword = self.entry_search_user.get()
        if not keyword:
            self.load_users()
            return
        for i in self.tree_users.get_children():
            self.tree_users.delete(i)
        users = self.db.search_customers(keyword)
        for u in users:
            self.tree_users.insert("", tk.END, values=(u['id'], u['full_name'], u['email'], u['phone_number']))

    def delete_user_action(self):
        selected = self.tree_users.selection()
        if not selected:
            messagebox.showwarning("Lỗi", "Vui lòng chọn khách hàng cần xóa")
            return
        item = self.tree_users.item(selected[0])
        u_id = item['values'][0]
        name = item['values'][1]
        if messagebox.askyesno("Cảnh báo nguy hiểm", f"Bạn có chắc muốn XÓA vĩnh viễn khách hàng '{name}'?\n\nLưu ý: Không thể xóa nếu khách đã từng đặt sân."):
            success, msg = self.db.delete_customer(u_id)
            if success:
                messagebox.showinfo("Thành công", msg)
                self.load_users()
            else:
                messagebox.showerror("Lỗi", msg)

    def view_user_history(self):
        selected = self.tree_users.selection()
        if not selected:
            messagebox.showwarning("Lỗi", "Vui lòng chọn khách hàng")
            return
        item = self.tree_users.item(selected[0])
        u_id = item['values'][0]
        name = item['values'][1]
        history = self.db.get_user_bookings(u_id)
        hist_win = Toplevel(self.root)
        hist_win.title(f"Lịch sử đặt sân: {name}")
        hist_win.geometry("600x400")
        cols = ("date", "court", "time", "status")
        tree = ttk.Treeview(hist_win, columns=cols, show="headings")
        tree.heading("date", text="Ngày")
        tree.heading("court", text="Sân")
        tree.heading("time", text="Giờ")
        tree.heading("status", text="Trạng thái")
        tree.pack(fill=tk.BOTH, expand=True)
        for h in history:
            time_range = f"{h['start_time']} - {h['end_time']}"
            tree.insert("", tk.END, values=(h['booking_date'], h['court_name'], time_range, h['status']))

    def edit_user_action(self):
        selected = self.tree_users.selection()
        if not selected:
            messagebox.showwarning("Lỗi", "Vui lòng chọn khách hàng")
            return
        item = self.tree_users.item(selected[0])
        vals = item['values']
        u_id = vals[0]
        edit_win = Toplevel(self.root)
        edit_win.title(f"Sửa KH: {vals[1]}")
        edit_win.geometry("300x200")
        ttk.Label(edit_win, text="Họ tên:").pack(pady=5)
        entry_name = ttk.Entry(edit_win)
        entry_name.pack(pady=5)
        entry_name.insert(0, vals[1])
        ttk.Label(edit_win, text="Số điện thoại:").pack(pady=5)
        entry_phone = ttk.Entry(edit_win)
        entry_phone.pack(pady=5)
        entry_phone.insert(0, vals[3])
        def save():
            new_name = entry_name.get()
            new_phone = entry_phone.get()
            success, msg = self.db.admin_update_customer(u_id, new_name, new_phone)
            if success:
                messagebox.showinfo("Thành công", msg, parent=edit_win)
                self.load_users()
                edit_win.destroy()
            else:
                messagebox.showerror("Lỗi", msg, parent=edit_win)
        ttk.Button(edit_win, text="Lưu", command=save).pack(pady=10)

    def reset_password_action(self):
        selected = self.tree_users.selection()
        if not selected:
            messagebox.showwarning("Lỗi", "Vui lòng chọn khách hàng")
            return
        item = self.tree_users.item(selected[0])
        u_id = item['values'][0]
        name = item['values'][1]
        confirm = messagebox.askyesno("Xác nhận", f"Reset mật khẩu của '{name}' về mặc định là '123456'?")
        if confirm:
            if self.db.admin_reset_password(u_id, "123456"):
                messagebox.showinfo("Thành công", "Đã reset mật khẩu thành công!")
            else:
                messagebox.showerror("Lỗi", "Thao tác thất bại")

    # --- TAB 5: BÁO CÁO DOANH THU ---
    def build_stats_manager(self):
        frame = ttk.Frame(self.tab_stats, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        filter_group = ttk.LabelFrame(frame, text="Chọn khoảng thời gian", padding="15")
        filter_group.pack(fill=tk.X, pady=10)
        ttk.Label(filter_group, text="Từ ngày:").pack(side=tk.LEFT, padx=5)
        self.date_from = DateEntry(filter_group, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_from.set_date(datetime.now().replace(day=1))
        self.date_from.pack(side=tk.LEFT, padx=5)
        ttk.Label(filter_group, text="Đến ngày:").pack(side=tk.LEFT, padx=5)
        self.date_to = DateEntry(filter_group, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_to.pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_group, text="Xem báo cáo", command=self.load_stats).pack(side=tk.LEFT, padx=20)
        result_frame = ttk.Frame(frame, padding="20")
        result_frame.pack(fill=tk.BOTH, expand=True)
        self.lbl_rev = ttk.Label(result_frame, text="Tổng doanh thu: ...", font=("Arial", 18, "bold"), foreground="#27ae60")
        self.lbl_rev.pack(pady=20)
        self.lbl_count = ttk.Label(result_frame, text="Số lượng booking: ...", font=("Arial", 14))
        self.lbl_count.pack(pady=10)
        self.load_stats()

    def load_stats(self):
        d_from = str(self.date_from.get_date())
        d_to = str(self.date_to.get_date())
        stats = self.db.get_revenue_stats(d_from, d_to)
        rev = int(stats['total_revenue'])
        cnt = stats['count_bookings']
        self.lbl_rev.config(text=f"Tổng doanh thu: {rev:,} VND")
        self.lbl_count.config(text=f"Số lượng booking hoàn thành: {cnt}")