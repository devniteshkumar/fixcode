import os
import subprocess
import json
from openai import OpenAI
from dotenv import load_dotenv
import sys
from pathlib import Path
import argparse

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

def ask_llm(code, error, umodel):
    print("[•] Asking LLM for a fix...")
    try:
        response = client.chat.completions.create(
            model=umodel,
            messages=[{
                "role": "user",
                "content": (
                    "I ran this code and got an error.\n\n"
                    f"Code:\n{code}\n\nError:\n{error}"
                )
            }],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("[X] API call failed:", str(e))
        return None
    
def update_env_model(new_model):
    env_path = Path(".env")
    if env_path.exists():
        lines = env_path.read_text().splitlines()
        updated = False
        for i, line in enumerate(lines):
            if line.startswith("FIXCODE_MODEL="):
                lines[i] = f"FIXCODE_MODEL={new_model}"
                updated = True
                break
        if not updated:
            lines.append(f"FIXCODE_MODEL={new_model}")
        env_path.write_text("\n".join(lines) + "\n")
    else:
        env_path.write_text(f"FIXCODE_MODEL={new_model}\n")
        
import re

def extract_raw_code(response: str) -> str:
    # Case 1: Extract from markdown code block
    match = re.search(r"```(?:\w+)?\n(.*?)```", response, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Case 2: No markdown formatting, just return up to first explanation line
    lines = response.strip().splitlines()
    code_lines = []
    for line in lines:
        # Stop at explanation
        if line.strip().lower().startswith(("the error", "explanation", "this code", "note:")):
            break
        code_lines.append(line)
    return "\n".join(code_lines).strip()


def main():
    parser = argparse.ArgumentParser(description="Fix broken code using LLM suggestions.")
    parser.add_argument("filename", help="Path to the code file to run and fix")
    parser.add_argument(
        "--model",
        default=os.getenv("FIXCODE_MODEL", "mistralai/mistral-7b-instruct:free"),
        help="OpenRouter/OpenAI model name to use (also configurable via FIXCODE_MODEL in .env)"
    )
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Automatically apply the suggested fix without prompting"
    )

    args = parser.parse_args()
    file = args.filename
    model = args.model
    auto_apply = args.yes

    if "--model" in sys.argv:
        update_env_model(model)

    error = run_program(file)
    if error:
        code = read_file(file)
        suggestion = ask_llm(code, error, model)
        if suggestion:
            cleaned = extract_raw_code(suggestion)
            print("\n[✔] Suggested Fix:\n")
            print(cleaned)
            if auto_apply:
                Path(file).write_text(cleaned)
                print("[✓] File updated with suggested fix.")
                main()
            else:
                apply = input("\n[?] Apply this fix to the file? (y/n): ").strip().lower()
                if apply == 'y':
                    Path(file).write_text(cleaned)
                    print("[✓] File updated with suggested fix.")
                    main()
                else:
                    print("[•] Fix not applied.")

if __name__ == "__main__":
    main()
