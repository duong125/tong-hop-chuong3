from flask import (
    Flask, request, redirect, url_for,
    abort, make_response, jsonify
)
from markupsafe import escape

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

# ====== DỮ LIỆU ======

STUDENTS = {
    "23T1020001": {"name": "Nguyễn Văn An", "lop": "K47A",
                   "scores": {"PMMNM": 8.5, "CSDL": 7.0, "MMT": 9.0}},
    "23T1020002": {"name": "Trần Thị Bình", "lop": "K47A",
                   "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0}},
    "23T1020003": {"name": "Lê Hoàng Cường", "lop": "K47B",
                   "scores": {"PMMNM": 9.5, "CSDL": 9.0}},
    "23T1020004": {"name": "Phạm Minh Dũng", "lop": "K47B",
                   "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0}},
    "23T1020005": {"name": "Hoàng Thu Hà", "lop": "K47A",
                   "scores": {}},
    "23T1020006": {"name": "Võ Quốc Khánh", "lop": "K47C",
                   "scores": {"PMMNM": 7.5, "MMT": 8.0}},
}

# ====== HÀM PHỤ ======

def average(scores):
    if not scores:
        return None
    return round(sum(scores.values()) / len(scores), 2)

def rank(avg):
    if avg is None:
        return "Chưa có điểm"
    if avg >= 8.5:
        return "Giỏi"
    if avg >= 7.0:
        return "Khá"
    if avg >= 5.0:
        return "Trung bình"
    return "Yếu"

def student_summary(mssv):
    s = STUDENTS[mssv]
    avg = average(s["scores"])
    return {
        "mssv": mssv,
        "name": s["name"],
        "lop": s["lop"],
        "scores": s["scores"],
        "average": avg,
        "rank": rank(avg),
    }

def layout(title, body):
    t = escape(title)
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{t} - Sổ điểm</title></head>
<body>
<nav>
  <a href="{url_for('index')}">Trang chủ</a> ·
  <a href="{url_for('student_list')}">Sinh viên</a> ·
  <a href="{url_for('search')}">Tìm kiếm</a>
</nav>
<hr>
{body}
</body></html>"""

# ====== CÂU 1: TRANG CHỦ ======

@app.route("/")
def index():
    total = len(STUDENTS)
    classes = len(set(s["lop"] for s in STUDENTS.values()))
    body = f"""<h1>Sổ điểm</h1>
<p>Tổng số sinh viên: {total}</p>
<p>Số lớp: {classes}</p>
<ul>
  <li><a href="{url_for('student_list')}">Danh sách sinh viên</a></li>
  <li><a href="{url_for('api_students')}">API sinh viên</a></li>
</ul>"""
    return layout("Trang chủ", body)

# ====== CÂU 2: DANH SÁCH SINH VIÊN ======

@app.route("/students")
def student_list():
    lop_filter = request.args.get("lop", "").strip()
    all_lops = sorted(set(s["lop"] for s in STUDENTS.values()))

    links = [f'<a href="{url_for("student_list")}">Tất cả</a>']
    for lop in all_lops:
        links.append(
            f'<a href="{url_for("student_list", lop=lop)}">'
            f'{escape(lop)}</a>'
        )
    nav = " | ".join(links)

    items = []
    for mssv in STUDENTS:
        sm = student_summary(mssv)
        if lop_filter and sm["lop"].upper() != lop_filter.upper():
            continue
        items.append(sm)

    if not items:
        table = "<p>Không có sinh viên phù hợp.</p>"
    else:
        rows = ""
        for sm in items:
            avg_display = (escape(str(sm["average"]))
                           if sm["average"] is not None else "—")
            rows += f"""<tr>
<td><a href="{url_for('student_detail', mssv=sm['mssv'])}">{escape(sm['mssv'])}</a></td>
<td>{escape(sm['name'])}</td>
<td>{escape(sm['lop'])}</td>
<td>{avg_display}</td>
<td>{escape(sm['rank'])}</td>
</tr>"""
        table = f"""<table border="1">
<tr><th>MSSV</th><th>Họ tên</th><th>Lớp</th><th>Điểm TB</th><th>Xếp loại</th></tr>
{rows}</table>"""

    body = f"<h1>Danh sách sinh viên</h1>{nav}<br><br>{table}"
    return layout("Danh sách sinh viên", body)

# ====== CÂU 3: CHI TIẾT SINH VIÊN ======

@app.route("/students/<mssv>")
def student_detail(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
    sm = student_summary(mssv)
    avg_display = (escape(str(sm["average"]))
                   if sm["average"] is not None else "—")

    score_rows = ""
    for hp, d in sm["scores"].items():
        score_rows += f"<tr><td>{escape(hp)}</td><td>{d}</td></tr>"
    if not score_rows:
        score_rows = "<tr><td colspan='2'>Chưa có điểm</td></tr>"

    body = f"""<h1>{escape(sm['name'])}</h1>
<p>MSSV: {escape(sm['mssv'])}</p>
<p>Lớp: <a href="{url_for('student_list', lop=sm['lop'])}">{escape(sm['lop'])}</a></p>
<p>Điểm TB: {avg_display}</p>
<p>Xếp loại: {escape(sm['rank'])}</p>
<h2>Bảng điểm</h2>
<table border="1">
<tr><th>Học phần</th><th>Điểm</th></tr>
{score_rows}</table>
<p><a href="{url_for('export_csv', mssv=sm['mssv'])}">Tải bảng điểm (CSV)</a></p>
<p>Link rút gọn: <a href="{url_for('short_link', mssv=sm['mssv'])}">{url_for('short_link', mssv=sm['mssv'])}</a></p>"""
    return layout(escape(sm["name"]), body)

# ====== CÂU 4: LINK RÚT GỌN ======

@app.route("/sv/<mssv>")
def short_link(mssv):
    return redirect(url_for("student_detail", mssv=mssv), 301)

# ====== CÂU 5: XUẤT CSV ======

@app.route("/students/<mssv>/export")
def export_csv(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
    scores = STUDENTS[mssv]["scores"]
    lines = ["hoc_phan,diem"]
    for hp, d in scores.items():
        lines.append(f"{hp},{d}")
    resp = make_response("\n".join(lines) + "\n")
    resp.headers["Content-Type"] = "text/csv; charset=utf-8"
    resp.headers["Content-Disposition"] = f"attachment; filename=diem_{mssv}.csv"
    return resp

# ====== CÂU 6: TÌM KIẾM ======

@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    form = f"""<h1>Tìm kiếm sinh viên</h1>
<form method="GET" action="{url_for('search')}">
  <input type="text" name="q" value="{escape(q)}">
  <button type="submit">Tìm</button>
</form>"""

    result = ""
    if q:
        found = []
        for mssv, s in STUDENTS.items():
            if (q.lower() in s["name"].lower()
                    or q.lower() in mssv.lower()):
                found.append((mssv, s["name"]))
        result += f'<p>Tìm thấy {len(found)} kết quả cho "{escape(q)}"</p>'
        if found:
            result += "<ul>"
            for mssv, name in found:
                result += (
                    f'<li><a href="{url_for("student_detail", mssv=mssv)}">'
                    f'{escape(mssv)} – {escape(name)}</a></li>'
                )
            result += "</ul>"

    return layout("Tìm kiếm", form + result)

# ====== CÂU 7: API ĐỌC DỮ LIỆU ======

@app.route("/api/students")
def api_students():
    lop_filter = request.args.get("lop", "").strip()
    min_avg_raw = request.args.get("min_avg")

    min_avg = None
    if min_avg_raw is not None:
        try:
            min_avg = float(min_avg_raw)
        except ValueError:
            abort(400, description="min_avg phải là số.")

    result = []
    for mssv in STUDENTS:
        sm = student_summary(mssv)
        if lop_filter and sm["lop"].upper() != lop_filter.upper():
            continue
        if min_avg is not None:
            if sm["average"] is None or sm["average"] < min_avg:
                continue
        result.append(sm)
    return jsonify(result)

@app.route("/api/students/<mssv>")
def api_student_detail(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")
    return jsonify(student_summary(mssv))

# ====== CÂU 8: API ĐIỂM MỘT HỌC PHẦN ======

@app.route("/api/students/<mssv>/scores/<course>",
           methods=["GET", "PUT", "DELETE"])
def api_score(mssv, course):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")

    scores = STUDENTS[mssv]["scores"]
    course_upper = course.upper()

    if request.method == "GET":
        if course_upper not in scores:
            abort(404, description=f"Học phần {course_upper} chưa có điểm.")
        return jsonify({"mssv": mssv, "course": course_upper,
                        "score": scores[course_upper]})

    if request.method == "PUT":
        score_raw = request.args.get("score")
        if score_raw is None:
            abort(400, description="Thiếu tham số score.")
        try:
            score_val = float(score_raw)
        except ValueError:
            abort(400, description="score phải là số.")
        if score_val < 0 or score_val > 10:
            abort(400, description="score phải trong khoảng [0, 10].")

        is_new = course_upper not in scores
        scores[course_upper] = score_val
        avg = average(scores)
        data = {"mssv": mssv, "course": course_upper,
                "score": score_val, "average": avg}

        if is_new:
            resp = make_response(jsonify(data), 201)
            resp.headers["Location"] = url_for(
                "api_score", mssv=mssv, course=course_upper)
            return resp
        return jsonify(data)

    # DELETE
    if course_upper not in scores:
        abort(404, description=f"Học phần {course_upper} chưa có điểm.")
    del scores[course_upper]
    return "", 204

# ====== CÂU 9: XỬ LÝ LỖI ======

ERROR_TITLES = {
    400: "Dữ liệu không hợp lệ",
    404: "Không tìm thấy",
    405: "Phương thức không được hỗ trợ",
}

@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(405)
def handle_error(error):
    title = ERROR_TITLES.get(error.code, "Lỗi")
    if request.path.startswith("/api/"):
        return jsonify({"error": title,
                        "detail": error.description}), error.code
    body = (f"<h1>{error.code} – {escape(title)}</h1>"
            f"<p>{escape(error.description)}</p>")
    return layout(title, body), error.code
