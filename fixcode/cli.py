import os
import subprocess
import json
from openai import OpenAI
from dotenv import load_dotenv
import sys
from pathlib import Path

load_dotenv(dotenv_path=Path.cwd() / ".env")
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

# Load executor map from .json
executors_path = Path(__file__).parent / "executors.json"
with open(executors_path) as f:
    EXECUTORS = json.load(f)

def get_extension(file):
    return Path(file).suffix.lower()

def fill_command(template, file):
    file_path = Path(file).resolve()
    return template.replace("$file", str(file_path))

def run_program(file):
    ext = get_extension(file)
    if ext not in EXECUTORS:
        print(f"[X] Unsupported or unknown file extension: {ext}")
        return None

    print(f"[•] Running {file} (extension: {ext})")
    cmd = fill_command(EXECUTORS[ext], file)
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print("[!] Error detected:\n", result.stderr)
        return result.stderr
    print("[✓] Program ran successfully:\n", result.stdout)
    return None

def read_file(file):
    return Path(file).read_text()

def ask_llm(code, error):
    print("[•] Asking Mistral (via OpenRouter) for a fix...")
    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct:free",
            messages=[{
                "role": "user",
                "content": f"I ran this code and got an error. Suggest a fix.\n\nCode:\n{code}\n\nError:\n{error}"
            }],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        print("[X] API call failed:", str(e))
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python tool.py <filename>")
        return

    file = sys.argv[1]
    error = run_program(file)
    if error:
        code = read_file(file)
        suggestion = ask_llm(code, error)
        if suggestion:
            print("\n[✔] Suggested Fix:\n")
            print(suggestion)

if __name__ == "__main__":
    main()
