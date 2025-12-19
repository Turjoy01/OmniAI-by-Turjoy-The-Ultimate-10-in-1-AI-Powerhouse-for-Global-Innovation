import requests
import sys

BASE_URL = "http://localhost:8000"

def test_temp_chat():
    print("Testing Temporary Chat Endpoints...")
    
    # 1. Create Session
    print("\n1. Creating Temporary Session...")
    try:
        response = requests.post(f"{BASE_URL}/api/temp-chat/session/create", data={"user_id": "test_user"})
        if response.status_code == 201:
            session_data = response.json()
            session_id = session_data["session_id"]
            print(f"SUCCESS: Session created. ID: {session_id}")
        else:
            print(f"FAILED: Status {response.status_code}, Response: {response.text}")
            return
    except Exception as e:
        print(f"ERROR: Could not connect to server. Is it running? {e}")
        return

    # 2. Send Message
    print("\n2. Sending Message...")
    try:
        payload = {
            "user_id": "test_user",
            "session_id": session_id,
            "message": "Hello, this is a test message for temporary chat."
        }
        response = requests.post(f"{BASE_URL}/api/temp-chat/message", data=payload)
        
        if response.status_code == 200:
            chat_data = response.json()
            print(f"SUCCESS: Message sent. AI Response: {chat_data['message'][:50]}...")
        else:
            print(f"FAILED: Status {response.status_code}, Response: {response.text}")
            return
    except Exception as e:
        print(f"ERROR: {e}")
        return

    print("\nVerification Complete!")

if __name__ == "__main__":
    test_temp_chat()
