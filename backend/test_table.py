import requests
import json

def test_table():
    url = "http://localhost:8000/api/table"
    
    # Test 1: No params
    print("Testing /api/table (No params)...")
    try:
        res = requests.get(url)
        data = res.json()
        print(f"Status: {res.status_code}")
        print(f"Total Records: {data.get('total')}")
        print(f"Data Length: {len(data.get('data', []))}")
        if len(data.get('data', [])) > 0:
            print("First row:", data['data'][0])
    except Exception as e:
        print(f"Error: {e}")
        
    # Test 2: With months param (e.g. month 1)
    print("\nTesting /api/table?months=1 (Jan)...")
    try:
        res = requests.get(url + "?months=1")
        data = res.json()
        print(f"Status: {res.status_code}")
        print(f"Total Records: {data.get('total')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_table()
