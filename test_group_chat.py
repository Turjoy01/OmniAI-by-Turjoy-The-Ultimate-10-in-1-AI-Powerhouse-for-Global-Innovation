import requests
import json
import uuid

BASE_URL = "http://localhost:8000/api/group-chat"
USER_ID_A = str(uuid.uuid4())
USER_ID_B = str(uuid.uuid4())

def run_tests():
    print("Starting Group Chat Tests (with Session)...")

    # 1. Create Session for User A
    print("\n1. Creating Session for User A...")
    resp = requests.post(f"{BASE_URL}/session/create", json={"user_id": USER_ID_A})
    assert resp.status_code == 201
    data_a = resp.json()
    session_id_a = data_a["session_id"]
    print(f"User A ID: {USER_ID_A}")
    print(f"Session A ID: {session_id_a}")

    # 2. Create Student Group
    print("\n2. Creating Student Group...")
    resp = requests.post(f"{BASE_URL}/group/create", json={
        "user_id": USER_ID_A,
        "session_id": session_id_a,
        "name": "Math Study Group",
        "type": "student"
    })
    print(resp.json())
    assert resp.status_code == 201
    group_id = resp.json()["group_id"]
    print(f"Group ID: {group_id}")

    # 3. User A sends message
    print("\n3. User A sending message...")
    resp = requests.post(f"{BASE_URL}/group/message", json={
        "user_id": USER_ID_A,
        "session_id": session_id_a,
        "group_id": group_id,
        "content": "Hello AI, can you help me with calculus?"
    })
    print("AI Response:", resp.json())
    if resp.status_code != 200:
        print("Error:", resp.text)
    assert resp.status_code == 200
    assert resp.json()["is_ai"] == True

    # 4. Create Session for User B
    print("\n4. Creating Session for User B...")
    resp = requests.post(f"{BASE_URL}/session/create", json={"user_id": USER_ID_B})
    data_b = resp.json()
    session_id_b = data_b["session_id"]
    print(f"User B ID: {USER_ID_B}")
    print(f"Session B ID: {session_id_b}")

    # 5. User B joins group
    print("\n5. User B joining group...")
    resp = requests.post(f"{BASE_URL}/group/join", json={
        "user_id": USER_ID_B,
        "session_id": session_id_b,
        "group_id": group_id
    })
    assert resp.status_code == 200
    print("Join response:", resp.json())

    # 6. User B sends message
    print("\n6. User B sending message...")
    resp = requests.post(f"{BASE_URL}/group/message", json={
        "user_id": USER_ID_B,
        "session_id": session_id_b,
        "group_id": group_id,
        "content": "I also need help with derivatives."
    })
    print("AI Response:", resp.json())
    assert resp.status_code == 200

    # 7. Get History
    print("\n7. Getting History...")
    resp = requests.get(f"{BASE_URL}/group/history/{group_id}")
    history = resp.json()
    print(f"History length: {len(history)}")
    assert len(history) >= 4 
    
    # 8. Delete Group
    print("\n8. Deleting Group (by User A)...")
    resp = requests.delete(f"{BASE_URL}/group/{group_id}?user_id={USER_ID_A}")
    assert resp.status_code == 200
    print("Delete response:", resp.json())

    print("\nALL TESTS PASSED!")

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
