import requests
import json
import uuid

BASE_URL = "http://localhost:8000/api/student"

def run_tests():
    print("Starting AI for Students Feature Tests...")

    # 1. Create Session
    print("\n1. Creating Session...")
    user_id = "student_user_123"
    resp = requests.post(f"{BASE_URL}/session/create", json={"user_id": user_id})
    assert resp.status_code == 201
    session_id = resp.json()["session_id"]
    print(f"Session ID: {session_id}")

    # 2. Homework Helper
    print("\n2. Testing Homework Helper...")
    resp = requests.post(f"{BASE_URL}/homework", json={
        "session_id": session_id,
        "user_id": user_id,
        "subject": "Physics",
        "question": "What is Newton's second law of motion?"
    })
    print("Homework Response Code:", resp.status_code)
    assert resp.status_code == 200
    print("Answer Snippet:", resp.json()["ai_response"][:100] + "...")

    # 3. Essay Generator
    print("\n3. Testing Essay Generator...")
    resp = requests.post(f"{BASE_URL}/essay", json={
        "session_id": session_id,
        "user_id": user_id,
        "topic": "The importance of renewable energy",
        "length": "short",
        "tone": "academic"
    })
    assert resp.status_code == 200
    print("Essay Snippet:", resp.json()["ai_response"][:100] + "...")

    # 4. Math Solver
    print("\n4. Testing Math Solver...")
    resp = requests.post(f"{BASE_URL}/math", json={
        "session_id": session_id,
        "user_id": user_id,
        "problem": "Solve for x: 2x + 5 = 15"
    })
    assert resp.status_code == 200
    print("Math Solution:", resp.json()["ai_response"])

    # 5. Study Mode
    print("\n5. Testing Study Mode...")
    resp = requests.post(f"{BASE_URL}/study", json={
        "session_id": session_id,
        "user_id": user_id,
        "topic": "Photosynthesis"
    })
    assert resp.status_code == 200
    print("Study Response:", resp.json()["ai_response"][:100] + "...")

    # 6. Flashcards
    print("\n6. Testing Flashcards...")
    resp = requests.post(f"{BASE_URL}/flashcards", json={
        "session_id": session_id,
        "user_id": user_id,
        "content": "The Eiffel Tower is in Paris. It was built in 1889. It is 330 meters tall."
    })
    assert resp.status_code == 200
    print("Flashcards:", resp.json()["ai_response"][:100] + "...")

    # 7. Summary
    print("\n7. Testing Summary...")
    resp = requests.post(f"{BASE_URL}/summary", json={
        "session_id": session_id,
        "user_id": user_id,
        "content": "Artificial intelligence is intelligence demonstrated by machines, as opposed to natural intelligence displayed by animals including humans. AI research has been defined as the field of study of intelligent agents, which refers to any system that perceives its environment and takes actions that maximize its chance of achieving its goals.",
        "detail_level": "concise"
    })
    assert resp.status_code == 200
    print("Summary:", resp.json()["ai_response"])

    # 8. History
    print("\n8. Getting History...")
    resp = requests.get(f"{BASE_URL}/history/{session_id}")
    assert resp.status_code == 200
    print(f"History length: {len(resp.json()['interactions'])}")
    assert len(resp.json()["interactions"]) >= 6

    # 9. Delete Session
    print("\n9. Deleting Session...")
    resp = requests.delete(f"{BASE_URL}/session/{session_id}")
    assert resp.status_code == 200
    print("Delete Response:", resp.json())

    print("\nALL STUDENT TOOL TESTS PASSED!")

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        import traceback
        print(f"\nTEST FAILED: {e}")
        traceback.print_exc()
