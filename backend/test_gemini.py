"""Test script to check available Gemini models."""
import google.generativeai as genai
import os

# Set API key
api_key = "AIzaSyBdqPZwVWo6TVN0fXupJkhpPui7cMq1pfU"
genai.configure(api_key=api_key)

print("Listing available models...")
print("-" * 60)

# List all models
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"Model: {model.name}")
        print(f"  Display Name: {model.display_name}")
        print(f"  Description: {model.description[:100]}...")
        print()

print("-" * 60)
print("Testing a simple generation...")

try:
    # Try with the base model name
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say hello")
    print(f"✓ Success with 'gemini-pro': {response.text}")
except Exception as e:
    print(f"✗ Failed with 'gemini-pro': {e}")

print("-" * 60)
