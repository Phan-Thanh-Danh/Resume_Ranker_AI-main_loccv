import urllib.request
import json

def verify_metadata():
    url = "http://127.0.0.1:8001/openapi.json"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
        
        print("Verifying API Metadata...")
        title = data.get("info", {}).get("title")
        description = data.get("info", {}).get("description")
        
        print(f"Title: {title}")
        print(f"Description: {description}")
        
        if title == "Hệ thống Xếp hạng CV AI":
            print("Title: OK")
        else:
            print(f"Title: MISMATCH (Got: {title})")
            
        print("\nMetadata check complete.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_metadata()
