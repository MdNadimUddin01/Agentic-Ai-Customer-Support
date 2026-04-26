"""Test if gemini-2.5-flash works."""
import google.generativeai as genai

api_key = "AIzaSyBdqPZwVWo6TVN0fXupJkhpPui7cMq1pfU"
genai.configure(api_key=api_key)

models_to_test = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-pro-latest"]

for model_name in models_to_test:
    try:
        print(f"Testing {model_name}...")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say hello in one word")
        print(f"  ✓ Success: {response.text.strip()}")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
    print()
