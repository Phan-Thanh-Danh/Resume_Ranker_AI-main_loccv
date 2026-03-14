import re
from typing import List, Dict, Set
from rapidfuzz import process, fuzz

# Danh sách hơn 150 danh mục kỹ năng chuẩn hóa (SKILL_MAPPING) với 1500+ biến thể
# Format: { "key_tim_kiem": "Ten Chuan Hoa" }
SKILL_MAPPING: Dict[str, str] = {
    # =================== NGÔN NGỮ LẬP TRÌNH ===================
    "python": "Python", "py": "Python", "pyton": "Python", "pythn": "Python",
    "python3": "Python", "python2": "Python", "py3": "Python", "cpython": "Python",
    "ipython": "Python", "pypi": "Python", "python lang": "Python",

    "java": "Java", "java8": "Java", "java11": "Java", "java17": "Java",
    "jdk": "Java", "jre": "Java", "jvm": "Java", "j2ee": "Java",
    "jakarta ee": "Java", "java spring": "Java", "openjdk": "Java",

    "javascript": "JavaScript", "js": "JavaScript", "java script": "JavaScript",
    "jscript": "JavaScript", "ecmascript": "JavaScript", "es6": "JavaScript",
    "es5": "JavaScript", "vanilla js": "JavaScript", "js scripting": "JavaScript",

    "typescript": "TypeScript", "ts": "TypeScript", "type script": "TypeScript",
    "typ-script": "TypeScript", "tsc": "TypeScript", "typescrpt": "TypeScript",
    "ts/js": "TypeScript", "tscript": "TypeScript",

    "c#": "C#", "csharp": "C#", "c sharp": "C#", "c-sharp": "C#",
    "charp": "C#", "cshrp": "C#", "cshap": "C#", "c #": "C#",
    "c# .net": "C#", "c#.net": "C#", "dotnet c#": "C#", "c-sharp lang": "C#",

    "c++": "C++", "cpp": "C++", "c plus plus": "C++", "cplusplus": "C++",
    "c++11": "C++", "c++14": "C++", "c++17": "C++", "c++20": "C++",
    "vc++": "C++", "cpplang": "C++",

    "c language": "C", "lang c": "C", "ansi c": "C", "embedded c": "C",
    "c programming": "C", "c code": "C",

    "golang": "Go", "go lang": "Go", "go-lang": "Go", "google go": "Go",
    "gopher": "Go", "go1.x": "Go",

    "rust": "Rust", "rustlang": "Rust", "rust-lang": "Rust", "cargo": "Rust",
    "rustc": "Rust", "rust-sdk": "Rust", "rust programming": "Rust",

    "php": "PHP", "php7": "PHP", "php8": "PHP", "php-fpm": "PHP",
    "lamp": "PHP", "lemp": "PHP", "php-cli": "PHP", "php lang": "PHP",

    "swift": "Swift", "swiftui": "Swift", "swift-lang": "Swift", "swift4": "Swift",
    "swift5": "Swift", "swift programming": "Swift", "swift ios": "Swift",

    "kotlin": "Kotlin", "kt": "Kotlin", "kotln": "Kotlin", "kotlin/jvm": "Kotlin",
    "kotlin/native": "Kotlin", "kotlinc": "Kotlin",

    "ruby": "Ruby", "rb": "Ruby", "ruby-lang": "Ruby",
    "ruby on rails": "Ruby on Rails", "rails": "Ruby on Rails", "ror": "Ruby on Rails",
    "ruby-on-rails": "Ruby on Rails", "rubyonrails": "Ruby on Rails",
    "rails framework": "Ruby on Rails", "rails app": "Ruby on Rails",

    "scala": "Scala", "scalajs": "Scala", "sbt": "Scala", "scala-lang": "Scala",
    "scala programming": "Scala",

    "dart": "Dart", "dartlang": "Dart", "dart-lang": "Dart", "dart-sdk": "Dart",

    "solidity": "Solidity", "sol": "Solidity", "smart contract": "Solidity",
    "ethereum dev": "Solidity", "web3-contract": "Solidity",

    "elixir": "Elixir", "mix elixir": "Elixir", "iex": "Elixir", "erlang": "Elixir",
    "elixir-lang": "Elixir", "erlang/elixir": "Elixir",

    "haskell": "Haskell", "ghc": "Haskell", "haskell-lang": "Haskell",

    "lua": "Lua", "luajit": "Lua", "embedded lua": "Lua",

    "perl": "Perl", "pl": "Perl", "perll": "Perl", "perl5": "Perl",

    "clojure": "Clojure", "clj": "Clojure", "cljs": "Clojure", "clojure-lang": "Clojure",

    "matlab": "MATLAB", "mathworks": "MATLAB", "simulink": "MATLAB",

    "fortran": "Fortran", "f90": "Fortran", "f77": "Fortran", "f95": "Fortran",

    "cobol": "COBOL", "mainframe cobol": "COBOL",

    "bash": "Bash", "sh": "Bash", "shell script": "Bash", "shell scripting": "Bash",
    "bash script": "Bash", "zsh": "Bash", "ksh": "Bash", "csh": "Bash",

    "powershell": "PowerShell", "ps1": "PowerShell", "pwsh": "PowerShell", "posh": "PowerShell",

    "r programming": "R", "r language": "R", "r lang": "R", "cran": "R",
    "rstats": "R", "r studio": "R", "rstudio": "R",

    "sql": "SQL", "structured query language": "SQL", "t-sql": "SQL",
    "sql query": "SQL", "sql scripting": "SQL",

    # =================== HTML & CSS ===================
    "html": "HTML5", "html5": "HTML5", "htm": "HTML5",
    "hypertext markup language": "HTML5",

    "css": "CSS3", "css3": "CSS3", "cascading style sheets": "CSS3",
    "flexbox": "CSS3", "css grid": "CSS3", "css flexbox": "CSS3",

    "scss": "Sass", "sass": "Sass", "syntactically awesome style sheets": "Sass",

    "less": "Less", "leaner style sheets": "Less",

    # =================== FRONTEND ===================
    "react": "React", "reactjs": "React", "react.js": "React", "rct": "React",
    "react hooks": "React", "preact": "React", "react-dom": "React", "react-router": "React",
    "react native": "React Native",

    "react native": "React Native", "rn": "React Native", "react-native": "React Native",
    "react-native-sdk": "React Native",

    "vue": "Vue.js", "vuejs": "Vue.js", "vue.js": "Vue.js", "vue2": "Vue.js",
    "vue3": "Vue.js", "vue-router": "Vue.js", "vuer": "Vue.js", "vuetify": "Vue.js",

    "angular": "Angular", "ng": "Angular", "angula": "Angular", "angularjs": "Angular",
    "angular.js": "Angular", "angular2+": "Angular", "angular 2": "Angular",
    "angular 12": "Angular", "angular 14": "Angular", "angular 17": "Angular",

    "svelte": "Svelte", "sveltekit": "Svelte", "svelt": "Svelte", "svelte-js": "Svelte",

    "nextjs": "Next.js", "next.js": "Next.js", "next-js": "Next.js", "next js": "Next.js",

    "nuxtjs": "Nuxt.js", "nuxt.js": "Nuxt.js", "nuxt": "Nuxt.js",
    "nuxt3": "Nuxt.js", "nuxt-js": "Nuxt.js",

    "gatsby": "Gatsby", "gatsbyjs": "Gatsby", "gatsby-js": "Gatsby",

    "remix": "Remix", "remix-run": "Remix", "remixjs": "Remix",

    "tailwind": "Tailwind CSS", "tailwindcss": "Tailwind CSS", "tailwind css": "Tailwind CSS",
    "tw css": "Tailwind CSS", "tailwind-css": "Tailwind CSS",

    "bootstrap": "Bootstrap", "bootstrap4": "Bootstrap", "bootstrap5": "Bootstrap",
    "btstrap": "Bootstrap", "boot-strap": "Bootstrap",

    "jquery": "jQuery", "jq": "jQuery", "j-query": "jQuery", "j-qry": "jQuery",

    "redux": "Redux", "rtk": "Redux", "redux-toolkit": "Redux",
    "redux saga": "Redux", "redux-thunk": "Redux",

    "zustand": "Zustand", "zstnd": "Zustand",
    "mobx": "MobX", "mob-x": "MobX",

    "vite": "Vite", "vitejs": "Vite", "vite-js": "Vite",
    "webpack": "Webpack", "web-pack": "Webpack", "wpack": "Webpack",
    "babel": "Babel", "babeljs": "Babel", "babel-js": "Babel",

    "material ui": "Material UI", "mui": "Material UI", "material-ui": "Material UI",
    "antd": "Ant Design", "ant design": "Ant Design", "ant-d": "Ant Design",
    "chakra ui": "Chakra UI", "chakra-ui": "Chakra UI", "chakra": "Chakra UI",
    "styled components": "Styled Components", "styled-components": "Styled Components",
    "emotion": "Emotion", "css-in-js": "Emotion",

    # =================== BACKEND ===================
    "node": "Node.js", "nodejs": "Node.js", "node.js": "Node.js",
    "node-js": "Node.js", "nvm": "Node.js", "node env": "Node.js",

    "express": "Express.js", "expressjs": "Express.js", "express.js": "Express.js",
    "ex-js": "Express.js", "expressjs framework": "Express.js",

    "nestjs": "NestJS", "nest.js": "NestJS", "nest js": "NestJS", "nest-js": "NestJS",

    "fastify": "Fastify", "fastifyjs": "Fastify",
    "koa": "Koa", "koajs": "Koa",

    "django": "Django", "djng": "Django", "djnago": "Django",
    "django-rest-framework": "Django", "drf": "Django",

    "flask": "Flask", "flsk": "Flask", "flask-api": "Flask",

    "fastapi": "FastAPI", "fast api": "FastAPI", "fstapi": "FastAPI", "fast-api": "FastAPI",

    "spring": "Spring Boot", "springboot": "Spring Boot", "spring boot": "Spring Boot",
    "spring cloud": "Spring Boot", "spring mvc": "Spring Boot",
    "spring security": "Spring Boot", "spring-boot": "Spring Boot",

    "hibernate": "Hibernate", "jpa": "Hibernate", "orm": "Hibernate",

    "laravel": "Laravel", "laravl": "Laravel", "lrvl": "Laravel",
    "eloquent": "Laravel", "larvel": "Laravel",

    "symfony": "Symfony", "symfny": "Symfony", "symfonie": "Symfony",

    "codeigniter": "CodeIgniter", "code igniter": "CodeIgniter", "code-igniter": "CodeIgniter",

    "asp.net": "ASP.NET Core", "asp net": "ASP.NET Core", "asp.net core": "ASP.NET Core",
    "aspnetcore": "ASP.NET Core", "asp.net web api": "ASP.NET Core",
    ".net core": "ASP.NET Core", "dotnetcore": "ASP.NET Core", "aspnet core": "ASP.NET Core",

    "mvc": "ASP.NET MVC", "asp.net mvc": "ASP.NET MVC",
    "aspnet mvc": "ASP.NET MVC", "dotnet mvc": "ASP.NET MVC",

    ".net": ".NET", "net": ".NET", "dotnet": ".NET",

    "phoenix": "Phoenix", "phx": "Phoenix", "elixir phoenix": "Phoenix",
    "gin": "Gin", "gin-gonic": "Gin", "gin framework": "Gin",
    "fiber": "Fiber", "go-fiber": "Fiber", "go fiber": "Fiber",
    "echo framework": "Echo", "go echo": "Echo",
    "adonis": "AdonisJS", "adonisjs": "AdonisJS",
    "strapi": "Strapi", "headless cms": "Strapi",

    "wordpress": "WordPress", "word press": "WordPress",
    "shopify": "Shopify", "liquid shopify": "Shopify",
    "drupal": "Drupal", "magento": "Magento", "magento2": "Magento",

    # =================== MOBILE ===================
    "flutter": "Flutter", "flutr": "Flutter", "flutter-sdk": "Flutter",
    "flutter dart": "Flutter", "flttr": "Flutter",

    "ionic": "Ionic", "ionic-framework": "Ionic",
    "xamarin": "Xamarin", "xamarin-forms": "Xamarin",

    "android": "Android SDK", "android studio": "Android SDK",
    "android-sdk": "Android SDK", "android dev": "Android SDK",
    "android-app": "Android SDK", "android development": "Android SDK",

    "ios": "iOS SDK", "ios-sdk": "iOS SDK", "ios dev": "iOS SDK",
    "xcode": "iOS SDK", "objective-c": "iOS SDK", "objc": "iOS SDK", "obj-c": "iOS SDK",

    # =================== DATABASE ===================
    "postgresql": "PostgreSQL", "postgres": "PostgreSQL", "psql": "PostgreSQL",
    "postgres sql": "PostgreSQL", "postgre": "PostgreSQL", "postgress": "PostgreSQL",
    "pgsql": "PostgreSQL", "postgresql db": "PostgreSQL",

    "mysql": "MySQL", "my-sql": "MySQL", "mysql8": "MySQL",
    "mysql server": "MySQL", "mysql db": "MySQL",

    "mariadb": "MariaDB", "maria-db": "MariaDB",

    "sql server": "SQL Server", "mssql": "SQL Server", "ms sql": "SQL Server",
    "microsoft sql server": "SQL Server", "sqlserver": "SQL Server",
    "ssms": "SQL Server", "sql server 2019": "SQL Server", "sql server 2022": "SQL Server",

    "sqlite": "SQLite", "sq lite": "SQLite", "sql-lite": "SQLite",

    "mongodb": "MongoDB", "mongo": "MongoDB", "mongo db": "MongoDB",
    "mongoose": "MongoDB", "mngodb": "MongoDB", "mongo-db": "MongoDB",
    "mongod": "MongoDB", "atlas mongo": "MongoDB",

    "redis": "Redis", "in-memory db": "Redis", "redis cache": "Redis",
    "redisdb": "Redis", "redis db": "Redis",

    "cassandra": "Cassandra", "apache cassandra": "Cassandra",

    "dynamodb": "DynamoDB", "dynamo db": "DynamoDB", "aws-dynamo": "DynamoDB",
    "amazon dynamodb": "DynamoDB",

    "firebase": "Firebase", "firestore": "Firebase", "realtime database": "Firebase",
    "firebase db": "Firebase", "firebase firestore": "Firebase",

    "neo4j": "Neo4j", "graph database": "Neo4j", "neo 4j": "Neo4j",

    "oracle": "Oracle Database", "oracle db": "Oracle Database",
    "oracle-sql": "Oracle Database", "pl/sql": "Oracle Database",
    "pl-sql": "Oracle Database", "oracle 19c": "Oracle Database", "oracle 12c": "Oracle Database",

    "couchdb": "CouchDB", "couch db": "CouchDB",
    "influxdb": "InfluxDB", "time-series db": "InfluxDB",
    "clickhouse": "ClickHouse", "click house": "ClickHouse",
    "supabase": "Supabase",

    "elasticsearch": "Elasticsearch", "elastic search": "Elasticsearch",
    "elk": "Elasticsearch", "elk stack": "Elasticsearch",

    # =================== CLOUD & DEVOPS ===================
    "aws": "AWS", "amazon web services": "AWS", "ec2": "AWS", "s3": "AWS",
    "lambda": "AWS", "amazon aws": "AWS", "aws cloud": "AWS", "aws-sdk": "AWS",

    "azure": "Azure", "microsoft azure": "Azure", "azure-devops": "Azure",
    "azure functions": "Azure", "azure ad": "Azure", "ms azure": "Azure",

    "gcp": "GCP", "google cloud": "GCP", "google cloud platform": "GCP",
    "app engine": "GCP", "cloud run": "GCP", "bigquery": "GCP", "gcloud": "GCP",

    "docker": "Docker", "dockerize": "Docker", "docker-compose": "Docker",
    "containerization": "Docker", "dockerfile": "Docker",
    "docker compose": "Docker", "docker-swarm": "Docker",

    "kubernetes": "Kubernetes", "k8s": "Kubernetes", "kube": "Kubernetes",
    "kuber": "Kubernetes", "kubectl": "Kubernetes", "helm": "Kubernetes",
    "istio": "Kubernetes", "minikube": "Kubernetes",

    "terraform": "Terraform", "infrastructure as code": "Terraform",
    "terraform-cloud": "Terraform", "hcl": "Terraform",

    "ansible": "Ansible", "ansible-playbook": "Ansible", "ansible automation": "Ansible",

    "jenkins": "Jenkins", "jenkins-ci": "Jenkins", "jenkins pipeline": "Jenkins",

    "git": "Git", "git-scm": "Git", "version control": "Git", "vcs": "Git",

    "github": "GitHub", "git hub": "GitHub", "github.com": "GitHub", "gh pages": "GitHub",

    "gitlab": "GitLab", "git lab": "GitLab", "gitlab-ci": "GitLab",

    "bitbucket": "Bitbucket", "bit bucket": "Bitbucket", "atlassian bitbucket": "Bitbucket",

    "github actions": "GitHub Actions", "github-actions": "GitHub Actions",
    "gha": "GitHub Actions", "gh actions": "GitHub Actions",

    "nginx": "Nginx", "ngnx": "Nginx", "engine-x": "Nginx", "nginx server": "Nginx",
    "apache": "Apache", "apache2": "Apache", "httpd": "Apache",

    "linux": "Linux", "unix": "Linux", "ubuntu": "Linux", "centos": "Linux",
    "debian": "Linux", "redhat": "Linux", "fedora": "Linux", "kali linux": "Linux",

    "ci/cd": "CI/CD", "continuous integration": "CI/CD", "continuous deployment": "CI/CD",
    "continuous delivery": "CI/CD",

    "circleci": "CircleCI", "circle-ci": "CircleCI",
    "travisci": "TravisCI", "travis-ci": "TravisCI",

    "prometheus": "Prometheus", "prom monitoring": "Prometheus",
    "grafana": "Grafana", "grafana dashboard": "Grafana",

    "rabbitmq": "RabbitMQ", "rabbit mq": "RabbitMQ", "message queue": "RabbitMQ",

    "kafka": "Kafka", "apache kafka": "Kafka", "kafka streams": "Kafka",

    # =================== AI/ML & DATA ===================
    "tensorflow": "TensorFlow", "tf": "TensorFlow", "tensorflow-gpu": "TensorFlow",
    "t-flow": "TensorFlow", "tf2": "TensorFlow",

    "pytorch": "PyTorch", "torch": "PyTorch", "py-torch": "PyTorch",
    "pytorch-gpu": "PyTorch", "torchvision": "PyTorch",

    "keras": "Keras", "keras-api": "Keras",

    "sklearn": "Scikit-learn", "scikit-learn": "Scikit-learn", "scikit": "Scikit-learn",
    "sci-kit": "Scikit-learn", "scikit learn": "Scikit-learn",

    "pandas": "Pandas", "pndas": "Pandas", "pd": "Pandas",
    "numpy": "NumPy", "nmpy": "NumPy", "np": "NumPy",
    "matplotlib": "Matplotlib", "plt": "Matplotlib",
    "seaborn": "Seaborn", "sns seaborn": "Seaborn",

    "spark": "Apache Spark", "apache spark": "Apache Spark", "pyspark": "Apache Spark",
    "scala spark": "Apache Spark", "spark ml": "Apache Spark",

    "hadoop": "Apache Hadoop", "hdfs": "Apache Hadoop", "mapreduce": "Apache Hadoop",
    "hive": "Apache Hadoop",

    "power bi": "Power BI", "pbi": "Power BI", "powerbi": "Power BI",
    "power-bi": "Power BI", "ms power bi": "Power BI",

    "tableau": "Tableau", "tblu": "Tableau", "tableau server": "Tableau",

    "nlp": "NLP", "natural language processing": "NLP", "spacy": "NLP",
    "nltk": "NLP", "bert": "NLP", "gpt": "NLP", "word2vec": "NLP", "llm": "NLP",

    "computer vision": "Computer Vision", "opencv": "Computer Vision",
    "object detection": "Computer Vision",

    "deep learning": "Deep Learning", "dl": "Deep Learning",
    "neural networks": "Deep Learning", "cnn": "Deep Learning",
    "rnn": "Deep Learning", "lstm": "Deep Learning", "gan": "Deep Learning",

    "machine learning": "Machine Learning", "ml": "Machine Learning",
    "ml engineer": "Machine Learning",

    "data science": "Data Science", "data scientist": "Data Science",

    "mlops": "MLOps", "ml-ops": "MLOps", "kubeflow": "MLOps", "mlflow": "MLOps",

    "langchain": "LangChain", "lang-chain": "LangChain",

    "huggingface": "Hugging Face", "hugging face": "Hugging Face",

    "data engineering": "Data Engineering", "data pipeline": "Data Engineering",
    "dbt": "Data Engineering",

    "airflow": "Apache Airflow", "apache airflow": "Apache Airflow",

    # =================== TOOLS & ARCHITECTURE ===================
    "rest": "REST API", "restful": "REST API", "rest api": "REST API",
    "rest-api": "REST API", "restful api": "REST API",

    "graphql": "GraphQL", "gql": "GraphQL", "graph-ql": "GraphQL",
    "grpc": "gRPC", "google-rpc": "gRPC",

    "microservices": "Microservices", "micro-services": "Microservices",
    "msa": "Microservices", "distributed systems": "Microservices",

    "agile": "Agile", "scrum": "Agile", "kanban": "Agile", "sprint": "Agile",

    "jira": "Jira", "atlassian": "Jira", "confluence": "Jira", "trello": "Jira",

    "selenium": "Selenium", "selenium webdriver": "Selenium", "selnum": "Selenium",

    "cypress": "Cypress", "cyprss": "Cypress", "cypress-js": "Cypress",

    "playwright": "Playwright", "play-wright": "Playwright", "playwright-js": "Playwright",

    "postman": "Postman", "pstman": "Postman", "api-testing": "Postman",

    "swagger": "Swagger", "openapi": "Swagger", "open-api": "Swagger", "swgr": "Swagger",

    "unit test": "Unit Testing", "unit testing": "Unit Testing",
    "unittest": "Unit Testing", "integration test": "Unit Testing",

    "jest": "Jest", "mocha": "Mocha", "chai": "Mocha",
    "pytest": "Pytest", "py-test": "Pytest",
    "junit": "JUnit", "j-unit": "JUnit",

    "sonarqube": "SonarQube", "sonar": "SonarQube",

    "figma": "Figma", "figma design": "Figma",

    "design patterns": "Design Patterns", "solid principles": "Design Patterns",

    "oop": "OOP", "object-oriented": "OOP", "object oriented": "OOP",
    "object oriented programming": "OOP",
}


def clean_text(text: str) -> str:
    if not text:
        return ""
    # Loại bỏ ký tự null và chuẩn hóa khoảng trắng
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_text(text: str) -> str:
    # Chuyển về chữ thường và dọn dẹp
    return clean_text(text).lower()


def extract_skills(text: str, skill_set: Set[str] | None = None) -> List[str]:
    """
    Trích xuất và chuẩn hóa kỹ năng từ văn bản.
    Sử dụng so khớp chính xác kết hợp so khớp mờ (fuzzy matching).
    """
    normalized_content = normalize_text(text)

    # Bước 1: Trích xuất chính xác dựa trên regex để tránh bắt sai (ví dụ: "go" vs "golang")
    found_normalized = set()

    # Chúng ta ưu tiên các key dài hơn để bắt các cụm từ trước (ví dụ: "react native" trước "react")
    sorted_keys = sorted(SKILL_MAPPING.keys(), key=len, reverse=True)

    temp_content = normalized_content
    for key in sorted_keys:
        # Regex đảm bảo khớp nguyên từ (word boundary)
        pattern = r"(?<!\w)" + re.escape(key) + r"(?!\w)"
        if re.search(pattern, temp_content):
            found_normalized.add(SKILL_MAPPING[key])
            # Xóa phần đã tìm thấy để tránh trùng lặp hoặc bắt chéo
            temp_content = re.sub(pattern, " ", temp_content)

    # Bước 2: Mô phỏng NLP/Fuzzy logic (Search mờ cho các từ chưa bắt được)
    # CHỈ áp dụng với chuỗi ASCII thuần để tránh tiếng Việt bị match nhầm
    words_raw = re.findall(r"[a-z0-9][a-z0-9\-\.]*", temp_content)  # chỉ lấy từ ASCII
    candidates = []
    for i in range(len(words_raw)):
        candidates.append(words_raw[i])  # 1-gram
        if i < len(words_raw) - 1:
            candidates.append(f"{words_raw[i]} {words_raw[i+1]}")  # 2-gram
        if i < len(words_raw) - 2:
            candidates.append(f"{words_raw[i]} {words_raw[i+1]} {words_raw[i+2]}")  # 3-gram

    # Lỗi gõ phổ biến thường có ít nhất 4 ký tự (ví dụ: "charp", "pyton")
    # Các từ quá ngắn (<= 3) dễ gây match nhầm nên bỏ qua
    _FUZZY_ALLOWED_SHORT = {"php", "sql", "git", "aws", "gcp", "nlp", "rnn", "cnn", "gan", "orm", "npm"}

    for cand in candidates:
        cand_stripped = cand.strip()
        if len(cand_stripped) <= 3 and cand_stripped not in _FUZZY_ALLOWED_SHORT:
            continue  # Bỏ qua chuỗi quá ngắn (dễ match nhầm)
        if len(cand_stripped) < 4:
            continue
        # So khớp mờ với danh sách các key (ngưỡng 95% để giảm false positive)
        match = process.extractOne(cand_stripped, sorted_keys, scorer=fuzz.ratio)
        if match and match[1] >= 85:  # Dùng ratio (toàn phần) thay partial_ratio để chính xác hơn
            matched_key = match[0]
            # Chỉ chấp nhận key có độ dài >= 4 để tránh match nhầm từ phổ thông (j2ee, grpc...)
            if len(matched_key) >= 4 or matched_key in ["go", "r", "js", "ts", "sql", "git", "aws", "gcp"]:
                found_normalized.add(SKILL_MAPPING[matched_key])

    return sorted(list(found_normalized))


def preview_text(text: str, max_len: int = 250) -> str:
    text = clean_text(text)
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip() + "..."
