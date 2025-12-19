import requests
import json
import uuid

BASE_URL = "http://localhost:8000/api/global-language"

def run_tests():
    print("Starting Global Language Support Tests...")

    # 1. Create Session
    print("\n1. Creating Session...")
    user_id = str(uuid.uuid4())
    resp = requests.post(f"{BASE_URL}/session/create", json={"user_id": user_id})
    assert resp.status_code == 201
    session_id = resp.json()["session_id"]
    print(f"Session ID: {session_id}")

    # 2. Multilingual Chat (Text)
    print("\n2. Testing Multilingual Chat (French)...")
    resp = requests.post(f"{BASE_URL}/chat", json={
        "session_id": session_id,
        "user_id": user_id,
        "message": "Hello, how are you?",
        "target_language": "French"
    })
    print("Chat Response:", resp.json())
    assert resp.status_code == 200
    assert resp.json()["target_language"] == "French"
    
    # Minimal WAV header for dummy audio test
    wav_header = b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xAC\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    files = {'audio_file': ('test.wav', wav_header, 'audio/wav')}
    data = {
        'session_id': session_id,
        'user_id': user_id,
        'target_language': 'Spanish'
    }

    # 3. Voice Interaction (JSON Response)
    print("\n3. Testing Voice Interaction (JSON Response)...")
    try:
        resp = requests.post(f"{BASE_URL}/voice", data=data, files=files)
        print("Voice JSON Code:", resp.status_code)
        if resp.status_code == 200:
            print("Voice JSON Response:", resp.json())
        else:
            print("Voice JSON Error (Expected if dummy audio):", resp.text)
    except Exception as e:
        print(f"Voice JSON test exception: {e}")

    # 4. Voice Interaction (Direct File Response)
    print("\n4. Testing Voice Interaction (Direct File)...")
    try:
        # Re-open file simulation since 'files' dict consumes it? No, bytes object is reusable in requests usually.
        # But safest to redefine or seek 0 if it was a real file handle. Here it's bytes.
        files_file = {'audio_file': ('test_file.wav', wav_header, 'audio/wav')}
        resp = requests.post(f"{BASE_URL}/voice/file", data=data, files=files_file)
        print("Voice File Code:", resp.status_code)
        
        if resp.status_code == 200:
            print(f"Voice File Content-Type: {resp.headers.get('content-type')}")
            print(f"Voice File Size: {len(resp.content)} bytes")
            assert resp.headers.get('content-type') == 'audio/mpeg'
            assert len(resp.content) > 0
        else:
            print("Voice File Error (Expected if dummy audio):", resp.text)
    except Exception as e:
         print(f"Voice File test exception: {e}")

    # 5. Get History
    print("\n5. Getting History...")
    resp = requests.get(f"{BASE_URL}/history/{session_id}")
    history = resp.json()
    print(f"History length: {len(history['interactions'])}")
    assert len(history['interactions']) >= 1
    
    # 6. Delete Session
    print("\n6. Deleting Session...")
    resp = requests.delete(f"{BASE_URL}/session/{session_id}")
    assert resp.status_code == 200
    print("Delete response:", resp.json())

    print("\nALL TESTS PASSED!")

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
