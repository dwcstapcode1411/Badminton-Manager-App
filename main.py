import tkinter as tk
from tkinter import messagebox
from database import DatabaseConnection
from login_window import LoginWindow
from customer_dashboard import CustomerDashboard
from manager_dashboard import ManagerDashboard

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw() # Ẩn cửa sổ gốc tạm thời
        self.db = DatabaseConnection()
        
        # Thử kết nối DB ngay khi mở app
        if not self.db.connect():
            messagebox.showerror("Lỗi Kết Nối", "Không thể kết nối đến Cơ sở dữ liệu.\nVui lòng kiểm tra cấu hình trong file 'database.py'.")
            self.root.destroy()
            return
        
        self.show_login()
        self.root.mainloop()
        
    def show_login(self):
        # Tạo cửa sổ đăng nhập mới
        self.login_window = tk.Toplevel()
        self.login_app = LoginWindow(self.login_window, self.db, self.on_login_success)
        
    def on_login_success(self, user_data):
        # Đóng cửa sổ đăng nhập
        self.login_window.destroy()
        
        # Hiển thị lại cửa sổ gốc (nếu cần) hoặc tạo cửa sổ dashboard mới
        # Ở đây ta dùng Toplevel cho dashboard để quản lý dễ hơn
        
        self.dashboard_window = tk.Toplevel()
        role = user_data['role']
        
        # LOGIC QUAN TRỌNG: So sánh với chuỗi Tiếng Việt trong Database
        if role == 'Khách hàng':
            CustomerDashboard(self.dashboard_window, self.db, user_data, self.logout)
        elif role == 'Quản lý' or role == 'Admin':
            ManagerDashboard(self.dashboard_window, self.db, user_data, self.logout)
        else:
            messagebox.showerror("Lỗi Phân Quyền", f"Vai trò '{role}' không hợp lệ hoặc chưa được hỗ trợ.")
            self.logout()
            
    def logout(self):
        # Đóng dashboard hiện tại
        try:
            if hasattr(self, 'dashboard_window') and self.dashboard_window.winfo_exists():
                self.dashboard_window.destroy()
        except:
            pass
            
        # Quay về màn hình đăng nhập
        self.show_login()

if __name__ == "__main__":
    app = App()