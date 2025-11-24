/*
 * SCRIPT TẠO DATABASE QUẢN LÝ SÂN CẦU LÔNG (FIXED VERSION)
 * Ngày cập nhật: 25/11/2025
 * Fix lỗi: 1265 Data truncated - Cập nhật câu lệnh INSERT bookings đúng cột
 */

-- 1. Reset và Tạo Database
DROP DATABASE IF EXISTS badminton_court_management;
CREATE DATABASE badminton_court_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE badminton_court_management;

-- ========================================================
-- 2. TẠO BẢNG (TABLES)
-- ========================================================

-- Bảng Users
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('Khách hàng', 'Quản lý', 'Admin') DEFAULT 'Khách hàng',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Bảng Courts
CREATE TABLE courts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    image_url VARCHAR(255),
    status ENUM('Hoạt động', 'Bảo trì', 'Dừng hoạt động') DEFAULT 'Hoạt động',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Bảng Court_Prices
CREATE TABLE court_prices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    court_id INT NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    is_weekend BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_prices_court FOREIGN KEY (court_id) REFERENCES courts(id) ON DELETE CASCADE
);

-- Bảng Bookings
CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    court_id INT NOT NULL,
    booking_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    status ENUM('Chờ xác nhận', 'Đã xác nhận', 'Đã check-in', 'Hoàn thành', 'Đã hủy', 'Vắng mặt') DEFAULT 'Chờ xác nhận',
    payment_status ENUM('Chưa thanh toán', 'Đã thanh toán', 'Hoàn tiền') DEFAULT 'Chưa thanh toán',
    payment_method ENUM('Tiền mặt', 'Chuyển khoản', 'Momo') DEFAULT 'Tiền mặt',
    check_in_code VARCHAR(20) UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_booking_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
    CONSTRAINT fk_booking_court FOREIGN KEY (court_id) REFERENCES courts(id) ON DELETE RESTRICT
);

-- Bảng Payments
CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method ENUM('Tiền mặt', 'Chuyển khoản', 'Momo') DEFAULT 'Tiền mặt',
    payment_status ENUM('Chưa thanh toán', 'Đã thanh toán', 'Thất bại', 'Hoàn tiền') DEFAULT 'Chưa thanh toán',
    transaction_ref VARCHAR(100),
    payment_time DATETIME DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_payment_booking FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
);

-- Bảng Reviews
CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    user_id INT NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_review_booking FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    CONSTRAINT fk_review_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ========================================================
-- 3. DỮ LIỆU MẪU (SEED DATA ĐÃ SỬA LỖI)
-- ========================================================

-- A. Thêm Users
INSERT INTO users (full_name, email, phone_number, password_hash, role) VALUES 
('Nguyễn Quản Lý', 'admin@badminton.com', '0901111111', 'password123', 'Quản lý'),
('Trần Văn Hùng', 'hung.tran@gmail.com', '0902222222', 'password123', 'Khách hàng'),
('Lê Thị Mai', 'mai.le@yahoo.com', '0903333333', 'password123', 'Khách hàng'),
('Phạm Minh Tuấn', 'tuan.pham@outlook.com', '0904444444', 'password123', 'Khách hàng'),
('Hoàng Thùy Linh', 'linh.hoang@gmail.com', '0905555555', 'password123', 'Khách hàng'),
('Võ Quốc Khánh', 'khanh.vo@gmail.com', '0906666666', 'password123', 'Khách hàng'),
('Đặng Thu Thảo', 'thao.dang@gmail.com', '0907777777', 'password123', 'Khách hàng'),
('Bùi Tiến Dũng', 'dung.bui@gmail.com', '0908888888', 'password123', 'Khách hàng'),
('Ngô Thanh Vân', 'van.ngo@gmail.com', '0909999999', 'password123', 'Khách hàng'),
('Customer Test', 'customerA@gmail.com', '0912345678', 'password123', 'Khách hàng');

-- B. Thêm Courts
INSERT INTO courts (name, description, status) VALUES 
('Sân 1 (VIP)', 'Thảm Yonex chuẩn thi đấu, máy lạnh', 'Hoạt động'),
('Sân 2 (Thường)', 'Sân thảm tiêu chuẩn, thoáng mát', 'Hoạt động'),
('Sân 3 (Thường)', 'Sân thảm tiêu chuẩn, gần quầy nước', 'Hoạt động'),
('Sân 4 (Gỗ)', 'Sân sàn gỗ cao cấp, độ nảy tốt', 'Hoạt động'),
('Sân 5 (VIP)', 'Khu vực riêng tư, ghế nghỉ sofa', 'Hoạt động');

-- C. Thêm Bảng Giá
INSERT INTO court_prices (court_id, start_time, end_time, price, is_weekend) VALUES 
(1, '05:00:00', '17:00:00', 60000, 0), (1, '17:00:00', '23:00:00', 100000, 0),
(1, '05:00:00', '17:00:00', 80000, 1), (1, '17:00:00', '23:00:00', 120000, 1),
(2, '05:00:00', '17:00:00', 40000, 0), (2, '17:00:00', '23:00:00', 70000, 0),
(2, '05:00:00', '17:00:00', 50000, 1), (2, '17:00:00', '23:00:00', 90000, 1),
(3, '05:00:00', '17:00:00', 40000, 0), (3, '17:00:00', '23:00:00', 70000, 0),
(3, '05:00:00', '17:00:00', 50000, 1), (3, '17:00:00', '23:00:00', 90000, 1),
(4, '05:00:00', '17:00:00', 40000, 0), (4, '17:00:00', '23:00:00', 70000, 0),
(4, '05:00:00', '17:00:00', 50000, 1), (4, '17:00:00', '23:00:00', 90000, 1),
(5, '05:00:00', '17:00:00', 60000, 0), (5, '17:00:00', '23:00:00', 100000, 0),
(5, '05:00:00', '17:00:00', 80000, 1), (5, '17:00:00', '23:00:00', 120000, 1);

-- D. Thêm Bookings (ĐÃ SỬA LỖI CỘT)
-- Cấu trúc đúng: (user_id, court_id, booking_date, start_time, end_time, total_price, status, payment_status, payment_method, check_in_code)

INSERT INTO bookings (user_id, court_id, booking_date, start_time, end_time, total_price, status, payment_status, payment_method, check_in_code) VALUES 
-- Hôm qua
(2, 1, CURDATE() - INTERVAL 1 DAY, '17:00:00', '19:00:00', 200000, 'Hoàn thành', 'Đã thanh toán', 'Tiền mặt', 'BK-001'),
(3, 2, CURDATE() - INTERVAL 1 DAY, '18:00:00', '20:00:00', 140000, 'Hoàn thành', 'Đã thanh toán', 'Tiền mặt', 'BK-002'),

-- Hôm nay
(4, 1, CURDATE(), '09:00:00', '11:00:00', 120000, 'Hoàn thành', 'Đã thanh toán', 'Tiền mặt', 'BK-003'),
(5, 3, CURDATE(), '17:00:00', '18:30:00', 105000, 'Đã xác nhận', 'Chưa thanh toán', 'Tiền mặt', 'BK-004'),
(6, 5, CURDATE(), '19:00:00', '21:00:00', 200000, 'Chờ xác nhận', 'Chưa thanh toán', 'Tiền mặt', 'BK-005'),
(10, 2, CURDATE(), '18:00:00', '20:00:00', 140000, 'Đã xác nhận', 'Đã thanh toán', 'Tiền mặt', 'BK-006'),

-- Ngày mai (Dòng gây lỗi cũ đã được sửa: thêm cột payment_method là 'Chuyển khoản')
(7, 4, CURDATE() + INTERVAL 1 DAY, '06:00:00', '08:00:00', 80000, 'Đã xác nhận', 'Chưa thanh toán', 'Chuyển khoản', 'BK-007'),
(8, 1, CURDATE() + INTERVAL 1 DAY, '18:00:00', '20:00:00', 200000, 'Chờ xác nhận', 'Chưa thanh toán', 'Tiền mặt', 'BK-008');

-- E. Thêm Payments
INSERT INTO payments (booking_id, amount, payment_method, payment_status) VALUES 
(1, 200000, 'Tiền mặt', 'Đã thanh toán'),
(2, 140000, 'Momo', 'Đã thanh toán'),
(3, 120000, 'Tiền mặt', 'Đã thanh toán'),
(6, 140000, 'Chuyển khoản', 'Đã thanh toán');

-- F. Thêm Reviews
INSERT INTO reviews (booking_id, user_id, rating, comment) VALUES 
(1, 2, 5, 'Sân VIP quá đẹp, đáng tiền!'),
(2, 3, 4, 'Sân ổn, nhưng hơi ồn ào.');