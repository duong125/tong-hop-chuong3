# Sổ điểm – Bài tập tổng hợp Chương 3

## 1. Danh sách Routes

Lệnh: `flask --app sodiem routes`

```
Endpoint           Methods          Rule
-----------------  ---------------  -------------------------------------------
api_score          DELETE, GET, PUT /api/students/<mssv>/scores/<course>
api_student_detail GET              /api/students/<mssv>
api_students       GET              /api/students
export_csv         GET              /students/<mssv>/export
index              GET              /
search             GET              /search
short_link         GET              /sv/<mssv>
static             GET              /static/<path:filename>
student_detail     GET              /students/<mssv>
student_list       GET              /students
```

Tổng cộng: 10 routes.

## 2. Kiểm thử bằng curl

### 2.1 Redirect 301

```
curl -i http://127.0.0.1:8000/sv/23T1020001

HTTP/1.1 301 MOVED PERMANENTLY
Location: /students/23T1020001
```

### 2.2 Xuất CSV

```
curl -i http://127.0.0.1:8000/students/23T1020001/export

HTTP/1.1 200 OK
Content-Type: text/csv; charset=utf-8
Content-Disposition: attachment; filename=diem_23T1020001.csv

hoc_phan,diem
PMMNM,8.5
CSDL,7.0
MMT,9.0
```

### 2.3 Lọc lớp + điểm TB

```
curl "http://127.0.0.1:8000/api/students?lop=k47a&min_avg=7"

Trả về JSON các sinh viên lớp K47A có điểm TB >= 7.
```

### 2.4 min_avg không hợp lệ

```
curl -i "http://127.0.0.1:8000/api/students?min_avg=abc"

HTTP/1.1 400 BAD REQUEST
{"detail":"min_avg phải là số.","error":"Dữ liệu không hợp lệ"}
```

### 2.5 Sinh viên không tồn tại

```
curl -i http://127.0.0.1:8000/api/students/999

HTTP/1.1 404 NOT FOUND
{"detail":"Không có sinh viên với MSSV = 999.","error":"Không tìm thấy"}
```

### 2.6 Thêm điểm mới (201)

```
curl -i -X PUT "http://127.0.0.1:8000/api/students/23T1020005/scores/web?score=9"

HTTP/1.1 201 CREATED
Location: /api/students/23T1020005/scores/WEB
{"average":9.0,"course":"WEB","mssv":"23T1020005","score":9.0}
```

### 2.7 Cập nhật điểm (200)

```
curl -X PUT "http://127.0.0.1:8000/api/students/23T1020005/scores/WEB?score=7.5"

HTTP/1.1 200 OK
{"average":7.5,"course":"WEB","mssv":"23T1020005","score":7.5}
```

### 2.8 Điểm ngoài [0,10]

```
curl -i -X PUT "http://127.0.0.1:8000/api/students/23T1020005/scores/WEB?score=11"

HTTP/1.1 400 BAD REQUEST
{"detail":"score phải trong khoảng [0, 10].","error":"Dữ liệu không hợp lệ"}
```

### 2.9 Xóa điểm (204)

```
curl -i -X DELETE http://127.0.0.1:8000/api/students/23T1020005/scores/WEB

HTTP/1.1 204 NO CONTENT
Body rỗng.
```

### 2.10 POST vào API → 405 JSON

```
curl -i -X POST http://127.0.0.1:8000/api/students/23T1020005/scores/WEB

HTTP/1.1 405 METHOD NOT ALLOWED
{"detail":"The method is not allowed for the requested URL.","error":"Phương thức không được hỗ trợ"}
```

### 2.11 POST vào trang web → 405 HTML

```
curl -i -X POST http://127.0.0.1:8000/students

HTTP/1.1 405 METHOD NOT ALLOWED
Content-Type: text/html; charset=utf-8
Trả lỗi dạng HTML.
```

## 3. Câu hỏi

**Vì sao Câu 4 dùng 301 còn Câu 8 trả 201 kèm Location?**

- 301 Moved Permanently: `/sv/<mssv>` là URL rút gọn, chuyển hướng vĩnh viễn sang `/students/<mssv>`. Client nên dùng URL mới từ giờ.
- 201 Created: thêm điểm mới thành công, một tài nguyên mới vừa được tạo. Header Location chỉ đến URL của tài nguyên vừa tạo để client truy cập.

**Thêm điểm rồi khởi động lại server, điểm còn không?**

Không. Dữ liệu chỉ lưu trong biến STUDENTS trên RAM. Khi server khởi động lại, biến được tạo lại từ dữ liệu ban đầu trong sodiem.py. Muốn lưu lâu dài phải dùng cơ sở dữ liệu.
