import sys
import os

# Add project root to sys.path
sys.path.append(r"d:\Lọc cv\Resume_Ranker_AI-main\Resume_Ranker_AI-main")

from app.utils.text import extract_skills

jd_text = """
Tuyển Dụng: Lập Trình Viên .NET (C# / ASP.NET)

1. Mô tả công việc (Responsibilities)
• Tham gia thiết kế, phát triển và bảo trì các ứng dụng web sử dụng hệ sinh thái .NET (C#, ASP.NET MVC, ASP.NET Core API).
• Thiết kế kiến trúc, tối ưu hóa truy vấn và quản trị cơ sở dữ liệu trên SQL Server.
• Phối hợp chặt chẽ với đội ngũ thiết kế và Frontend để tích hợp giao diện người dùng (HTML, CSS, JavaScript, Vue.js).
• Thực hiện kiểm thử phần mềm (viết test case, ghi nhận bug report) để đảm bảo chất lượng mã nguồn và tính ổn định của hệ thống trước khi nghiệm thu.
• Viết tài liệu kỹ thuật và tham gia review code cùng các thành viên trong nhóm.
2. Yêu cầu ứng viên (Requirements)
• Kỹ năng bắt buộc:
o Tốt nghiệp Cao đẳng/Đại học chuyên ngành Công nghệ thông tin, Phần mềm hoặc các ngành liên quan.
o Thành thạo ngôn ngữ lập trình C#, nắm vững ASP.NET MVC và xây dựng RESTful API.
o Có kinh nghiệm thiết kế và làm việc với cơ sở dữ liệu SQL Server.
o Nắm vững nền tảng lập trình hướng đối tượng (OOP) và cấu trúc dữ liệu.
o Sử dụng thành thạo công cụ quản lý mã nguồn (Git).
• Điểm cộng (Khuyến khích có):
o Có kinh nghiệm làm việc với các framework Frontend, ưu tiên Vue.js.
o Có hiểu biết hoặc kinh nghiệm đóng gói, triển khai ứng dụng bằng Docker.
o Từng tham gia phát triển các phần mềm quản lý (như hệ thống quản lý bán hàng, quản lý nhân sự).
o Có tư duy logic tốt và khả năng đọc hiểu tài liệu tiếng Anh chuyên ngành.
"""

cv_text = """
PHAN THÀNH DANH
Vị trí ứng tuyển: .NET Developer
2. KỸ NĂNG CHUYÊN MÔN (TECHNICAL SKILLS)
• Ngôn ngữ & Framework: cshap, asp.net core api, asp.net mvc, vue.js
• Database & APIs: sql server, restful api
• Version Control & DevOps: git., docker, ci/cd.
"""

print("--- JD SKILLS ---")
jd_skills = extract_skills(jd_text)
print(jd_skills)

print("\n--- CV SKILLS ---")
cv_skills = extract_skills(cv_text)
print(cv_skills)

print("\n--- MATCHING ---")
matched = set(jd_skills).intersection(set(cv_skills))
print(f"Matched: {matched}")
print(f"Is 'C#' in JD? {'C#' in jd_skills}")
print(f"Is 'C#' in CV? {'C#' in cv_skills}")
