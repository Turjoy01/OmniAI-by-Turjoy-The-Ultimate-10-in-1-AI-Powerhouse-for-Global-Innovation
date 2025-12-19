import asyncio
import requests
import os
from services.openai_service import OpenAIService

BASE_URL = "http://localhost:8000/api/global-language"

async def run_debug_test():
    print("Step 1: Generating real test audio via OpenAI...")
    ai_svc = OpenAIService()
    try:
        test_audio_bytes = await ai_svc.generate_audio("How is the weather?")
        with open("debug_test_input.mp3", "wb") as f:
            f.write(test_audio_bytes)
        print(f"Generated test audio: {len(test_audio_bytes)} bytes")
    except Exception as e:
        print(f"Failed to generate test audio: {e}")
        return

    print("\nStep 2: Creating session...")
    resp = requests.post(f"{BASE_URL}/session/create", json={"user_id": "debug_user"})
    session_id = resp.json()["session_id"]
    print(f"Session ID: {session_id}")

    print("\nStep 3: Sending voice to /voice/file...")
    files = {'audio_file': ('debug_test_input.mp3', open("debug_test_input.mp3", "rb"), 'audio/mpeg')}
    data = {
        'session_id': session_id,
        'user_id': 'debug_user',
        'target_language': 'English'
    }

    try:
        resp = requests.post(f"{BASE_URL}/voice/file", data=data, files=files)
        print(f"Status Code: {resp.status_code}")
        print(f"Response Headers: {resp.headers}")
        
        if resp.status_code == 200:
            print(f"Response Content Length: {len(resp.content)} bytes")
            if len(resp.content) == 0:
                print("!!! ERROR: Received 0 bytes !!!")
            else:
                with open("debug_output_answer.mp3", "wb") as f:
                    f.write(resp.content)
                print("Saved response to debug_output_answer.mp3")
        else:
            print(f"Error Response: {resp.text}")
    except Exception as e:
        print(f"Exception during request: {e}")
    finally:
        files['audio_file'][1].close()

if __name__ == "__main__":
    asyncio.run(run_debug_test())
