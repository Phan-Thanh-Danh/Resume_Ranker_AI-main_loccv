import sys
import os

# Add project root to sys.path
sys.path.append(r"d:\Lọc cv\Resume_Ranker_AI-main\Resume_Ranker_AI-main")

from app.utils.text import extract_skills

test_cases = [
    {
        "input": "Em có làm project quản lý nhân sự dùng csharp với database là sql server. Frontend em code bằng vuejs. I am ready to go to work.",
        "expected": ["C#", "SQL Server", "Vue.js"]
    },
    {
        "input": "Backend Python developer with FastAPI, Docker, SQL",
        "expected": ["FastAPI", "Docker", "Python"] # SQL might map to something or be ignored if not in mapping, but here we check for the mapped ones
    },
    {
        "input": "Kinh nghiệm làm việc với Nodejs, React Native và AWS. Biết dùng Git và Jira.",
        "expected": ["AWS", "Git", "Jira", "Node.js", "React Native"]
    },
    {
        "input": "I code in Go. I also go to the gym.",
        "expected": ["Go"]
    },
    {
        "input": "Expert in Machine Learning and Deep Learning using Pytorch.",
        "expected": ["Deep Learning", "Machine Learning", "PyTorch"]
    }
]

def run_tests():
    print("Starting verification of skill extraction...")
    all_passed = True
    for i, case in enumerate(test_cases):
        result = extract_skills(case["input"])
        # Check if expected is subset of result (some cases might have more skills found)
        passed = all(skill in result for skill in case["expected"])
        print(f"Test {i+1}: {'PASSED' if passed else 'FAILED'}")
        print(f"  Input: {case['input']}")
        print(f"  Expected: {case['expected']}")
        print(f"  Result: {result}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\nAll skill extraction tests passed!")
    else:
        print("\nSome tests failed.")

if __name__ == "__main__":
    run_tests()
