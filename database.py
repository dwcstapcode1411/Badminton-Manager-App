import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta

class DatabaseConnection:
    def __init__(self):
        # CẤU HÌNH KẾT NỐI
        self.host = "localhost"
        self.user = "root"
        self.password = "YOUR_PASSWORD"  # MK của bạn
        self.database = "badminton_court_management"
        self.conn = None

    def connect(self):
        """Tạo kết nối đến CSDL"""
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return self.conn
        except Error as e:
            print(f"Lỗi kết nối Database: {e}")
            return None

    # --- AUTHENTICATION & USER MANAGEMENT ---

    def get_user_login(self, email, password, role):
        """Xác thực người dùng"""
        if self.connect():
            cursor = self.conn.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE email = %s AND password_hash = %s AND role = %s"
            cursor.execute(query, (email, password, role))
            user = cursor.fetchone()
            cursor.close()
            self.conn.close()
            return user
        return None

    def register_user(self, full_name, email, phone, password):
        """Đăng ký tài khoản khách hàng mới"""
        try:
            if self.connect():
                cursor = self.conn.cursor()
                query = """
                    INSERT INTO users (full_name, email, phone_number, password_hash, role)
                    VALUES (%s, %s, %s, %s, 'Khách hàng')
                """
                cursor.execute(query, (full_name, email, phone, password))
                self.conn.commit()
                self.conn.close()
                return True, "Đăng ký thành công! Vui lòng đăng nhập."
        except mysql.connector.Error as err:
            return False, f"Lỗi: Email hoặc SĐT đã tồn tại ({err})"
        except Exception as e:
            return False, str(e)

    def update_user_profile(self, user_id, full_name, phone):
        """Cập nhật thông tin cá nhân"""
        try:
            if self.connect():
                cursor = self.conn.cursor()
                query = "UPDATE users SET full_name = %s, phone_number = %s WHERE id = %s"
                cursor.execute(query, (full_name, phone, user_id))
                self.conn.commit()
                self.conn.close()
                return True, "Cập nhật thành công!"
        except Exception as e:
            return False, str(e)

    def change_password(self, user_id, old_pass, new_pass):
        """Đổi mật khẩu"""
        if self.connect():
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute("SELECT password_hash FROM users WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            
            if result and result['password_hash'] == old_pass:
                cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_pass, user_id))
                self.conn.commit()
                self.conn.close()
                return True, "Đổi mật khẩu thành công!"
            else:
                self.conn.close()
                return False, "Mật khẩu cũ không chính xác."
        return False, "Lỗi kết nối."

    # --- ADMIN USER MANAGEMENT ---

    def get_all_customers(self):
        """Lấy danh sách khách hàng"""
        data = []
        if self.connect():
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute("SELECT id, full_name, email, phone_number FROM users WHERE role = 'Khách hàng'")
            data = cursor.fetchall()
            self.conn.close()
        return data

    def search_customers(self, keyword):
        """Tìm kiếm khách hàng theo Tên hoặc SĐT"""
        data = []
        if self.connect():
            cursor = self.conn.cursor(dictionary=True)
            search_term = f"%{keyword}%"
            query = """
                SELECT id, full_name, email, phone_number 
                FROM users 
                WHERE role = 'Khách hàng' 
                AND (full_name LIKE %s OR phone_number LIKE %s)
            """
            cursor.execute(query, (search_term, search_term))
            data = cursor.fetchall()
            self.conn.close()
        return data

    def delete_customer(self, user_id):
        """Xóa khách hàng (Kiểm tra ràng buộc)"""
        try:
            if self.connect():
                cursor = self.conn.cursor()
                # Kiểm tra xem khách có booking nào không
                check_query = "SELECT COUNT(*) FROM bookings WHERE user_id = %s"
                cursor.execute(check_query, (user_id,))
                count = cursor.fetchone()[0]
                
                if count > 0:
                    self.conn.close()
                    return False, f"Không thể xóa: Khách hàng này đang có {count} dữ liệu đặt sân."
                
                delete_query = "DELETE FROM users WHERE id = %s AND role = 'Khách hàng'"
                cursor.execute(delete_query, (user_id,))
                self.conn.commit()
                self.conn.close()
                return True, "Đã xóa khách hàng thành công."
        except Exception as e:
            return False, str(e)

    def admin_update_customer(self, user_id, full_name, phone):
        return self.update_user_profile(user_id, full_name, phone)

    def admin_reset_password(self, user_id, new_pass):
        if self.connect():
            cursor = self.conn.cursor()
            query = "UPDATE users SET password_hash = %s WHERE id = %s"
            cursor.execute(query, (new_pass, user_id))
            self.conn.commit()
            self.conn.close()
            return True
        return False
    def get_all_courts(self):
        """Lấy TẤT CẢ sân (bao gồm cả bảo trì/dừng hoạt động) cho Admin"""
        data = []
        if self.connect():
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM courts ORDER BY name")
            data = cursor.fetchall()
            self.conn.close()
        return data

    def add_court(self, name, description, status):
        """Thêm sân mới"""
        try:
            if self.connect():
                cursor = self.conn.cursor()
                query = "INSERT INTO courts (name, description, status) VALUES (%s, %s, %s)"
                cursor.execute(query, (name, description, status))
                self.conn.commit()
                self.conn.close()
                return True, "Thêm sân thành công!"
        except Exception as e:
            return False, str(e)

    def update_court(self, court_id, name, description, status):
        """Cập nhật thông tin sân"""
        try:
            if self.connect():
                cursor = self.conn.cursor()
                query = "UPDATE courts SET name = %s, description = %s, status = %s WHERE id = %s"
                cursor.execute(query, (name, description, status, court_id))
                self.conn.commit()
                self.conn.close()
                return True, "Cập nhật sân thành công!"
        except Exception as e:
            return False, str(e)

    def delete_court(self, court_id):
        """Xóa sân (Chỉ xóa được nếu chưa có booking nào)"""
        try:
            if self.connect():
                cursor = self.conn.cursor()
                # Kiểm tra booking tồn tại
                check = "SELECT COUNT(*) FROM bookings WHERE court_id = %s"
                cursor.execute(check, (court_id,))
                cnt = cursor.fetchone()[0]
                
                if cnt > 0:
                    self.conn.close()
                    return False, f"Không thể xóa: Sân này đang có {cnt} lịch sử đặt.\nHãy chuyển trạng thái sang 'Dừng hoạt động' thay vì xóa."
                
                query = "DELETE FROM courts WHERE id = %s"
                cursor.execute(query, (court_id,))
                self.conn.commit()
                self.conn.close()
                return True, "Xóa sân thành công!"
        except Exception as e:
            return False, str(e)

    # --- PRICING MANAGEMENT (MỚI - QUẢN LÝ GIÁ) ---

    def get_court_prices(self, court_id):
        """Lấy danh sách bảng giá của 1 sân"""
        data = []
        if self.connect():
            cursor = self.conn.cursor(dictionary=True)
            # Format time để hiển thị đẹp hơn
            query = """
                SELECT id, court_id, 
                       DATE_FORMAT(start_time, '%H:%i') as start, 
                       DATE_FORMAT(end_time, '%H:%i') as end, 
                       price, is_weekend 
                FROM court_prices 
                WHERE court_id = %s 
                ORDER BY is_weekend, start_time
            """
            cursor.execute(query, (court_id,))
            data = cursor.fetchall()
            self.conn.close()
        return data

    def add_price_rule(self, court_id, start, end, price, is_weekend):
        """Thêm khung giá mới"""
        try:
            if self.connect():
                cursor = self.conn.cursor()
                query = "INSERT INTO court_prices (court_id, start_time, end_time, price, is_weekend) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(query, (court_id, start, end, price, is_weekend))
                self.conn.commit()
                self.conn.close()
                return True, "Thêm giá thành công!"
        except Exception as e:
            return False, str(e)

    def delete_price_rule(self, price_id):
        """Xóa khung giá"""
        try:
            if self.connect():
                cursor = self.conn.cursor()
                query = "DELETE FROM court_prices WHERE id = %s"
                cursor.execute(query, (price_id,))
                self.conn.commit()
                self.conn.close()
                return True, "Xóa giá thành công!"
        except Exception as e:
            return False, str(e)
    # --- COURT & BOOKING LOGIC ---

    def get_active_courts(self):
        courts = []
        if self.connect():
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM courts WHERE status = 'Hoạt động'")
            courts = cursor.fetchall()
            self.conn.close()
        return courts
    
    def get_courts_status_now(self):
        """
        Lấy trạng thái thực tế của tất cả các sân TẠI THỜI ĐIỂM HIỆN TẠI
        Trả về: List các sân kèm trạng thái 'Trống' hoặc 'Đang có khách'
        """
        data = []
        if self.connect():
            cursor = self.conn.cursor(dictionary=True)
            now = datetime.now()
            current_date = now.strftime('%Y-%m-%d')
            current_time = now.strftime('%H:%M:%S')
            
            # Lấy tất cả sân
            cursor.execute("SELECT id, name, status FROM courts")
            courts = cursor.fetchall()
            
            for court in courts:
                status_now = "Trống"
                color = "green"
                info = "Sẵn sàng"
                
                if court['status'] != 'Hoạt động':
                    status_now = court['status'] # Bảo trì/Dừng hoạt động
                    color = "#f39c12" # Cam
                    info = "Không khả dụng"
                else:
                    # Kiểm tra xem có booking nào đang diễn ra ngay lúc này không
                    query_busy = """
                        SELECT u.full_name, b.end_time 
                        FROM bookings b
                        JOIN users u ON b.user_id = u.id
                        WHERE b.court_id = %s 
                        AND b.booking_date = %s
                        AND b.start_time <= %s AND b.end_time > %s
                        AND b.status IN ('Đã check-in', 'Đã xác nhận', 'Hoàn thành')
                    """
                    cursor.execute(query_busy, (court['id'], current_date, current_time, current_time))
                    busy_booking = cursor.fetchone()
                    
                    if busy_booking:
                        status_now = "Đang có khách"
                        color = "#c0392b" # Đỏ
                        info = f"Khách: {busy_booking['full_name']}\nĐến: {busy_booking['end_time']}"
                
                data.append({
                    'id': court['id'],
                    'name': court['name'],
                    'status_text': status_now,
                    'color': color,
                    'info': info
                })
            
            self.conn.close()
        return data

    def check_conflict(self, court_id, date, start_time, end_time):
        if self.connect():
            cursor = self.conn.cursor()
            query = """
                SELECT COUNT(*) FROM bookings 
                WHERE court_id = %s 
                AND booking_date = %s 
                AND status NOT IN ('Đã hủy', 'Vắng mặt')
                AND (
                    (start_time < %s AND end_time > %s)
                )
            """
            cursor.execute(query, (court_id, date, end_time, start_time))
            count = cursor.fetchone()[0]
            self.conn.close()
            return count > 0
        return True

    def get_court_schedule(self, court_id, date_str):
        """Lấy danh sách các khung giờ đã đặt (Kèm tên khách) - Dùng cho Timeline View"""
        bookings = []
        if self.connect():
            cursor = self.conn.cursor(dictionary=True)
            query = """
                SELECT b.start_time, b.end_time, b.status, u.full_name
                FROM bookings b
                JOIN users u ON b.user_id = u.id
                WHERE b.court_id = %s 
                AND b.booking_date = %s 
                AND b.status NOT IN ('Đã hủy', 'Vắng mặt')
                ORDER BY b.start_time
            """
            cursor.execute(query, (court_id, date_str))
            raw_data = cursor.fetchall()
            self.conn.close()
            for b in raw_data:
                s_seconds = b['start_time'].total_seconds()
                e_seconds = b['end_time'].total_seconds()
                bookings.append({
                    'start': s_seconds / 3600,
                    'end': e_seconds / 3600,
                    'status': b['status'],
                    'customer_name': b['full_name']
                })
        return bookings

    def calculate_price(self, court_id, start_time_str, end_time_str, date_obj):
        total_price = 0
        if self.connect():
            cursor = self.conn.cursor(dictionary=True)
            fmt = "%H:%M"
            t_start = datetime.strptime(start_time_str, fmt)
            t_end = datetime.strptime(end_time_str, fmt)
            is_weekend = 1 if date_obj.weekday() >= 5 else 0
            
            query = "SELECT * FROM court_prices WHERE court_id = %s AND is_weekend = %s"
            cursor.execute(query, (court_id, is_weekend))
            prices = cursor.fetchall()
            
            current_t = t_start
            while current_t < t_end:
                current_time_only = current_t.time()
                price_per_hour = 0
                for p in prices:
                    p_start = (datetime.min + p['start_time']).time()
                    p_end = (datetime.min + p['end_time']).time()
                    if p_start <= current_time_only < p_end:
                        price_per_hour = float(p['price'])
                        break
                total_price += price_per_hour * 0.5 
                current_t += timedelta(minutes=30)
            self.conn.close()
        return total_price

    def create_booking(self, user_id, court_id, date, start, end, price):
        try:
            if self.connect():
                cursor = self.conn.cursor()
                import random
                code = f"BK-{random.randint(1000, 9999)}"
                query = """
                    INSERT INTO bookings (user_id, court_id, booking_date, start_time, end_time, total_price, status, payment_status, payment_method, check_in_code)
                    VALUES (%s, %s, %s, %s, %s, %s, 'Chờ xác nhận', 'Chưa thanh toán', 'Tiền mặt', %s)
                """
                cursor.execute(query, (user_id, court_id, date, start, end, price, code))
                self.conn.commit()
                self.conn.close()
                return True, "Đặt sân thành công!"
        except Exception as e:
            return False, str(e)

    def get_user_bookings(self, user_id):
        data = []
        if self.connect():
            cursor = self.conn.cursor(dictionary=True)
            query = """
                SELECT b.id, c.name as court_name, b.booking_date, b.start_time, b.end_time, b.total_price, b.status
                FROM bookings b
                JOIN courts c ON b.court_id = c.id
                WHERE b.user_id = %s
                ORDER BY b.booking_date DESC
            """
            cursor.execute(query, (user_id,))
            data = cursor.fetchall()
            self.conn.close()
        return data

    def cancel_booking(self, booking_id):
        if self.connect():
            cursor = self.conn.cursor()
            query = "UPDATE bookings SET status = 'Đã hủy' WHERE id = %s AND status = 'Chờ xác nhận'"
            cursor.execute(query, (booking_id,))
            self.conn.commit()
            rows = cursor.rowcount
            self.conn.close()
            return rows > 0
        return False

    def get_all_bookings(self, status_filter=None):
        data = []
        if self.connect():
            cursor = self.conn.cursor(dictionary=True)
            base_query = """
                SELECT b.id, u.full_name, c.name as court_name, b.booking_date, 
                       b.start_time, b.end_time, b.status, b.check_in_code
                FROM bookings b
                JOIN users u ON b.user_id = u.id
                JOIN courts c ON b.court_id = c.id
            """
            if status_filter and status_filter != "Tất cả":
                base_query += " WHERE b.status = %s"
                val = (status_filter,)
            else:
                val = ()
            base_query += " ORDER BY b.booking_date DESC, b.start_time ASC"
            cursor.execute(base_query, val)
            data = cursor.fetchall()
            self.conn.close()
        return data

    def update_booking_status(self, booking_id, new_status):
        if self.connect():
            cursor = self.conn.cursor()
            query = "UPDATE bookings SET status = %s WHERE id = %s"
            cursor.execute(query, (new_status, booking_id))
            self.conn.commit()
            self.conn.close()
            return True
        return False

    def get_revenue_stats(self, start_date=None, end_date=None):
        """Thống kê doanh thu theo khoảng thời gian"""
        stats = {'total_revenue': 0, 'count_bookings': 0}
        if self.connect():
            cursor = self.conn.cursor(dictionary=True)
            query = """
                SELECT SUM(total_price) as rev, COUNT(*) as cnt 
                FROM bookings 
                WHERE status IN ('Hoàn thành', 'Đã xác nhận')
            """
            params = []
            
            # Thêm điều kiện ngày nếu có
            if start_date and end_date:
                query += " AND booking_date BETWEEN %s AND %s"
                params.extend([start_date, end_date])
            
            cursor.execute(query, tuple(params))
            res = cursor.fetchone()
            if res['rev']:
                stats['total_revenue'] = float(res['rev'])
            stats['count_bookings'] = res['cnt']
            self.conn.close()
        return stats