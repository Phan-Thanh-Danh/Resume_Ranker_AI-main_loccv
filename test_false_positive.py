import sys
sys.path.append(r"d:\Lọc cv\Resume_Ranker_AI-main\Resume_Ranker_AI-main")
from app.utils.text import extract_skills

java_jd = """
Thông Tin Tuyển Dụng Lập Trình Viên Java
Chúng tôi đang tìm kiếm những ứng viên nhiệt huyết, có đam mê lập trình.
Kỹ năng chuyên môn: Thành thạo lập trình JAVA, có kiến thức về Spring, Hibernate, RESTful API.
Cơ sở dữ liệu như MySQL, Oracle hoặc SQL Server.
Quản lý mã nguồn như Git.
Kiểm thử: JUnit, TestNG để kiểm thử phần mềm.
"""

print("=== FALSE POSITIVE TEST ===")
skills = extract_skills(java_jd)
print(f"Skills extracted from Java JD: {skills}")
print()
if "C#" in skills:
    print("❌ FAIL: C# incorrectly extracted from Java JD!")
else:
    print("✅ PASS: C# NOT extracted from Java JD (correct)")

if "Java" in skills:
    print("✅ PASS: Java correctly extracted")
else:
    print("❌ FAIL: Java not extracted from Java JD")

if "Spring Boot" in skills:
    print("✅ PASS: Spring Boot correctly extracted")
else:
    print("❌ FAIL: Spring Boot not extracted")
