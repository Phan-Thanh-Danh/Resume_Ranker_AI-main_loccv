import sys
import os

# Add project root to sys.path
sys.path.append(r"d:\Lọc cv\Resume_Ranker_AI-main\Resume_Ranker_AI-main")

from app.services.matcher import ResumeMatcherService

def test_classification():
    matcher = ResumeMatcherService()
    
    cases = [
        {
            "name": "Vietnamese JD",
            "text": "Tuyển dụng nhân viên lập trình Python. Yêu cầu: 2 năm kinh nghiệm, trách nhiệm công việc...",
            "filename": "Job_Description.docx",
            "expected_jd": True
        },
        {
            "name": "Vietnamese CV",
            "text": "Thông tin cá nhân: Nguyễn Văn A. Mục tiêu nghề nghiệp: Phát triển phần mềm. Kinh nghiệm làm việc...",
            "filename": "NguyenVanA_CV.docx",
            "expected_jd": False
        },
        {
            "name": "Ambiguous filename but JD content",
            "text": "We are hiring! Responsibilities include coding in Python and Java. Requirements: BS in CS.",
            "filename": "document.docx",
            "expected_jd": True
        },
        {
            "name": "Ambiguous filename but CV content",
            "text": "Education: University of Technology. Projects: Built a web app with React. Experience: Intern at ABC.",
            "filename": "document_1.docx",
            "expected_jd": False
        },
        {
            "name": "Filename 'tuyen dung' hint",
            "text": "Dev needed.",
            "filename": "tuyen dung.docx",
            "expected_jd": True
        }
    ]
    
    print("Testing JD/CV Classification Accuracy...")
    all_passed = True
    for case in cases:
        is_jd = matcher.is_probable_jd(case["text"], case["filename"])
        passed = (is_jd == case["expected_jd"])
        status = "PASSED" if passed else "FAILED"
        print(f"[{status}] {case['name']}: Detected as {'JD' if is_jd else 'Resume'} (Expected {'JD' if case['expected_jd'] else 'Resume'})")
        if not passed:
            all_passed = False
            
    if all_passed:
        print("\nAll classification tests passed!")
    else:
        print("\nSome classification tests failed.")

if __name__ == "__main__":
    test_classification()
