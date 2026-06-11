# Timesheet Checker

## 1. Giới thiệu

Ứng dụng dùng để kiểm tra Timesheet từ nhiều nguồn dữ liệu:

* Redmine API
* File CSV local

Kết quả được tổng hợp và xuất ra file Excel nhằm hỗ trợ:

* Kiểm tra nhân sự log thiếu giờ
* Kiểm tra nhân sự không log giờ
* Tổng hợp giờ công theo người dùng
* Tổng hợp số giờ còn thiếu trong kỳ báo cáo

---

## 2. Yêu cầu môi trường

### Python

Khuyến nghị:

```bash
Python 3.11+
```

### Thư viện

```bash
pip install requests
pip install openpyxl
```

Hoặc:

```bash
pip install -r requirements.txt
```

---

## 3. Cấu trúc thư mục

```text
Spent time/
│
├── main.py
├── config.json
├── user_mapping.csv
│
├── input/
│   ├── timelog_redmine.csv
│   └── timelog_rm.csv
│
├── modules/
│   ├── __init__.py
│   ├── config_loader.py
│   ├── mapping_loader.py
│   ├── redmine_client.py
│   ├── csv_client.py
│   ├── timesheet_service.py
│   └── excel_report.py
│
└── output/
```

---

## 4. Cấu hình

### config.json

### Nguồn dữ liệu từ Redmine

```json
{
  "data_source": "redmine",
  "local_csv": {
    "input_folder": "input"
  },
  "redmines": [
    {
      "name": "REDMINE",
      "url": "https://redmine.company.com",
      "api_key": "YOUR_API_KEY"
    }
  ],
  "report": {
    "from_date": "2026-01-01",
    "min_hours_per_day": 8
  }
}
```

### Nguồn dữ liệu từ CSV

```json
{
  "data_source": "local_csv",
  "local_csv": {
    "input_folder": "input"
  },
  "redmines": [
    {
      "name": "LOCAL"
    }
  ],
  "report": {
    "from_date": "2026-01-01",
    "min_hours_per_day": 8
  }
}
```

---

## 5. User Mapping

### user_mapping.csv

```csv
Alias,StandardUser
taitm,Tai Tran Minh
tai.tran,Tai Tran Minh
tai.tranminh,Tai Tran Minh
```

### Ý nghĩa

Nhiều Alias sẽ được gom về một StandardUser.

Ví dụ:

```text
taitm
tai.tran
tai.tranminh
```

đều được tính là:

```text
Tai Tran Minh
```

---

## 6. Định dạng CSV

Ứng dụng hỗ trợ nhiều file CSV trong thư mục:

```text
input/
```

Ví dụ:

```csv
Project,Date,User,Hours
R&D,2026-06-01,taitm,8
R&D,2026-06-02,taitm,6
```

Các cột bắt buộc:

| Column  |
| ------- |
| Project |
| Date    |
| User    |
| Hours   |

### Định dạng ngày hỗ trợ

```text
yyyy-MM-dd
```

Ví dụ:

```text
2026-06-01
```

---

## 7. Chạy chương trình

```bash
python main.py
```

---

## 8. Kết quả

File Excel được sinh tại:

```text
output/
```

Ví dụ:

```text
timesheet_report_20260602_153000.xlsx
```

---

## 9. Các Sheet trong Excel

### INFO

Thông tin báo cáo:

| Item          | Value               |
| ------------- | ------------------- |
| From Date     | 2026-04-01          |
| To Date       | 2026-06-02          |
| Generated At  | 2026-06-02 15:30:00 |
| Total Entries | 2440                |

---

### DETAIL

Chi tiết toàn bộ dữ liệu.

| Date | User | Redmine | Project | Hours |
| ---- | ---- | ------- | ------- | ----: |

---

### UNDER_HOURS

Danh sách log dưới số giờ quy định.

| Date | User | Total Hours | Missing |
| ---- | ---- | ----------: | ------: |

Ví dụ:

| Date       | User          | Total Hours | Missing |
| ---------- | ------------- | ----------: | ------: |
| 2026-06-01 | Tai Tran Minh |           6 |       2 |

---

### NO_LOG

Danh sách nhân sự không log giờ.

| Date | User | Redmine |
| ---- | ---- | ------- |

---

### SUMMARY

Tổng hợp theo người dùng.

| User | Logged Days | Total Hours |
| ---- | ----------: | ----------: |

---

### MISSING_HOURS_SUMMARY

Tổng hợp số giờ còn thiếu.

| User | Missing Days | Missing Hours |
| ---- | -----------: | ------------: |

Ví dụ:

| User          | Missing Days | Missing Hours |
| ------------- | -----------: | ------------: |
| Tai Tran Minh |            5 |            28 |

---

## 10. Quy tắc tính toán

### UNDER_HOURS

Nếu:

```text
Total Hours < min_hours_per_day
```

thì đưa vào:

```text
UNDER_HOURS
```

---

### NO_LOG

Nếu:

```text
Ngày làm việc
+
Không có log
```

thì đưa vào:

```text
NO_LOG
```

---

### MISSING_HOURS_SUMMARY

Được tính bằng:

```text
UNDER_HOURS Missing
+
NO_LOG × min_hours_per_day
```

Ví dụ:

```text
01-Jun log 6h
=> thiếu 2h

02-Jun không log
=> thiếu 8h

Tổng thiếu = 10h
```

---

## 11. Hỗ trợ nhiều Redmine

Ví dụ:

```json
{
  "redmines": [
    {
      "name": "REDMINE",
      "url": "https://redmine.company.com",
      "api_key": "xxxxx"
    },
    {
      "name": "RM",
      "url": "https://rm.company.com",
      "api_key": "yyyyy"
    }
  ]
}
```

Dữ liệu sẽ được gộp tự động theo StandardUser.

---

## 12. Troubleshooting

### ModuleNotFoundError

Kiểm tra:

```text
modules/__init__.py
```

đã tồn tại hay chưa.

---

### JSONDecodeError

Kiểm tra:

```text
config.json
```

đúng cú pháp JSON.

---

### Không có dữ liệu UNDER_HOURS

Kiểm tra:

```text
user_mapping.csv
```

đã map đúng tên user hay chưa.

---

### Không đọc được Redmine

Kiểm tra:

* URL Redmine
* API Key
* Quyền truy cập API
* Endpoint:

```text
/time_entries.json
```
