# Sổ điểm – Bài tập tổng hợp Chương 3

## flask routes

```
(chạy lệnh: flask --app sodiem routes rồi dán kết quả vào đây)
```

## Kết quả curl

```
(dán output từng lệnh curl vào đây)
```

## Câu hỏi

**Vì sao Câu 4 dùng 301 còn Câu 8 trả 201 kèm Location?**

301 là chuyển hướng vĩnh viễn, báo client URL cũ không dùng nữa, hãy dùng URL mới.
201 là tạo tài nguyên mới thành công, Location chỉ đến tài nguyên vừa tạo để client truy cập.

**Thêm điểm rồi khởi động lại server, điểm còn không?**

Không. Dữ liệu nằm trong biến Python trên RAM, tắt server là mất.
Muốn giữ lâu dài phải dùng database.
