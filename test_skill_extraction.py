import sys
sys.path.append(r"d:\Lọc cv\Resume_Ranker_AI-main\Resume_Ranker_AI-main")
from app.utils.text import extract_skills

# 50+ testcases: (input_text, expected_skill)
test_cases = [
    # C# variations
    ("I know csharp very well", "C#"),
    ("I know charp very well", "C#"),
    ("I know cshrp very well", "C#"),
    ("I know c# very well", "C#"),
    ("I know cshap very well", "C#"),
    # Python variations
    ("I love pyton", "Python"),
    ("I use py for scripts", "Python"),
    ("Coded in python3", "Python"),
    # JavaScript variations
    ("Frontend with java script", "JavaScript"),
    ("Used ecmascript daily", "JavaScript"),
    ("Used vanilla js", "JavaScript"),
    # Vue.js variations
    ("vuer was my choice", "Vue.js"),
    ("Used vue for frontend", "Vue.js"),
    ("Used vuejs framework", "Vue.js"),
    # React variations
    ("Used reactjs for frontend", "React"),
    ("Built SPA with react hooks", "React"),
    # Node.js variations
    ("Backend using nodejs", "Node.js"),
    ("Used node.js server", "Node.js"),
    ("Node env setup", "Node.js"),
    # Docker variations
    ("Containerization with dockerize", "Docker"),
    ("docker compose deployment", "Docker"),
    ("Used dockerfile", "Docker"),
    # Kubernetes variations
    ("Orchestration with k8s", "Kubernetes"),
    ("Deployed on kube cluster", "Kubernetes"),
    ("Used helm charts", "Kubernetes"),
    ("minikube local dev", "Kubernetes"),
    # PostgreSQL variations
    ("Stored data in postgres", "PostgreSQL"),
    ("Used pgsql queries", "PostgreSQL"),
    ("Worked with postgress", "PostgreSQL"),
    # MongoDB variations
    ("Used mongo db for storage", "MongoDB"),
    ("Used mongoose ORM", "MongoDB"),
    ("mngodb setup", "MongoDB"),
    # SQL Server variations
    ("Queried via mssql", "SQL Server"),
    ("Used ms sql server", "SQL Server"),
    ("Connected to sqlserver", "SQL Server"),
    # Scikit-learn variations
    ("sklearn pipeline", "Scikit-learn"),
    ("Used scikit for ML", "Scikit-learn"),
    ("sci-kit learning", "Scikit-learn"),
    # PyTorch variations
    ("torch model training", "PyTorch"),
    ("pytorch neural network", "PyTorch"),
    # Angular variations
    ("Built with angula framework", "Angular"),
    ("ng component development", "Angular"),
    ("angular2+ development", "Angular"),
    # AWS variations
    ("Deployed to ec2", "AWS"),
    ("Used lambda functions", "AWS"),
    ("s3 bucket storage", "AWS"),
    # ASP.NET variations
    ("Built with aspnetcore", "ASP.NET Core"),
    ("Used asp.net web api", "ASP.NET Core"),
    ("asp net development", "ASP.NET Core"),
    # CI/CD
    ("Used continuous integration", "CI/CD"),
    ("ci/cd pipeline setup", "CI/CD"),
]

print("=== COMPREHENSIVE TYPO STRESS TEST ===\n")
passed = 0
failed = 0
for (text, expected) in test_cases:
    skills = extract_skills(text)
    ok = expected in skills
    status = "✅ PASS" if ok else "❌ FAIL"
    if ok:
        passed += 1
    else:
        failed += 1
    print(f"{status} | '{text[:40]}' -> Expected: '{expected}' | Got: {skills}")

print(f"\n=== SUMMARY: {passed}/{len(test_cases)} PASSED, {failed} FAILED ===")
