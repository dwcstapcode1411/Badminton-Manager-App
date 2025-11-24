import tkinter as tk
from tkinter import ttk, messagebox, Toplevel

class LoginWindow:
    def __init__(self, root, db, on_login_success):
        self.root = root
        self.db = db
        self.on_login_success = on_login_success
        
        # Việt hóa tiêu đề cửa sổ
        self.root.title("Đăng Nhập - Quản Lý Sân Cầu Lông")
        self.root.geometry("400x400")
        self.root.resizable(False, False)
        
        # Xử lý sự kiện đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.setup_ui()

    def setup_ui(self):
        frame = ttk.Frame(self.root, padding="30")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="ĐĂNG NHẬP HỆ THỐNG", font=("Arial", 16, "bold"), foreground="#0052cc").pack(pady=15)
        
        # Email
        ttk.Label(frame, text="Email:").pack(anchor=tk.W)
        self.entry_email = ttk.Entry(frame, width=40)
        self.entry_email.pack(pady=5)
        
        # Password
        ttk.Label(frame, text="Mật khẩu:").pack(anchor=tk.W)
        self.entry_pass = ttk.Entry(frame, width=40, show="*")
        self.entry_pass.pack(pady=5)
        
        # Role
        ttk.Label(frame, text="Vai trò:").pack(anchor=tk.W)
        self.cbo_role = ttk.Combobox(frame, values=["Khách hàng", "Quản lý"], state="readonly", width=37)
        self.cbo_role.current(0)
        self.cbo_role.pack(pady=5)
        
        # Buttons
        btn_login = ttk.Button(frame, text="Đăng Nhập", command=self.handle_login)
        btn_login.pack(pady=15, fill=tk.X)
        
        # Register Link
        lbl_register = ttk.Label(frame, text="Chưa có tài khoản? Đăng ký ngay", foreground="blue", cursor="hand2")
        lbl_register.pack(pady=5)
        lbl_register.bind("<Button-1>", lambda e: self.open_register_window())

    def handle_login(self):
        email = self.entry_email.get()
        pwd = self.entry_pass.get()
        role = self.cbo_role.get()
        
        if not email or not pwd:
            messagebox.showerror("Thông báo", "Vui lòng nhập đầy đủ Email và Mật khẩu!")
            return
            
        user = self.db.get_user_login(email, pwd, role)
        
        if user:
            self.on_login_success(user)
        else:
            messagebox.showerror("Đăng nhập thất bại", "Email, mật khẩu hoặc vai trò không chính xác.\nVui lòng kiểm tra lại.")

    def open_register_window(self):
        reg_win = Toplevel(self.root)
        reg_win.title("Đăng Ký Tài Khoản Mới")
        reg_win.geometry("350x450")
        
        frame = ttk.Frame(reg_win, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="ĐĂNG KÝ THÀNH VIÊN", font=("Arial", 14, "bold"), foreground="#27ae60").pack(pady=10)
        
        ttk.Label(frame, text="Họ và Tên:").pack(anchor=tk.W)
        entry_name = ttk.Entry(frame, width=35)
        entry_name.pack(pady=2)
        
        ttk.Label(frame, text="Email:").pack(anchor=tk.W)
        entry_email = ttk.Entry(frame, width=35)
        entry_email.pack(pady=2)
        
        ttk.Label(frame, text="Số điện thoại:").pack(anchor=tk.W)
        entry_phone = ttk.Entry(frame, width=35)
        entry_phone.pack(pady=2)
        
        ttk.Label(frame, text="Mật khẩu:").pack(anchor=tk.W)
        entry_pass = ttk.Entry(frame, width=35, show="*")
        entry_pass.pack(pady=2)

        ttk.Label(frame, text="Nhập lại mật khẩu:").pack(anchor=tk.W)
        entry_confirm = ttk.Entry(frame, width=35, show="*")
        entry_confirm.pack(pady=2)
        
        def process_register():
            name = entry_name.get()
            email = entry_email.get()
            phone = entry_phone.get()
            pwd = entry_pass.get()
            confirm = entry_confirm.get()
            
            if not all([name, email, phone, pwd]):
                messagebox.showwarning("Thiếu thông tin", "Vui lòng điền đầy đủ các trường!", parent=reg_win)
                return
                
            if pwd != confirm:
                messagebox.showerror("Lỗi mật khẩu", "Mật khẩu xác nhận không khớp!", parent=reg_win)
                return
                
            success, msg = self.db.register_user(name, email, phone, pwd)
            if success:
                messagebox.showinfo("Chúc mừng", msg, parent=reg_win)
                reg_win.destroy()
            else:
                messagebox.showerror("Lỗi đăng ký", msg, parent=reg_win)
                
        ttk.Button(frame, text="Xác Nhận Đăng Ký", command=process_register).pack(pady=20, fill=tk.X)

    def on_close(self):
        self.root.quit()