# FixCode

A command-line tool that automatically detects errors in your code and suggests AI-powered fixes using Large Language Models.

## Features

- **Multi-language support**: Supports Python, C, C++, and JavaScript files
- **Automatic error detection**: Runs your code and captures runtime errors
- **AI-powered fixes**: Uses OpenAI-compatible APIs to suggest intelligent code fixes
- **Simple CLI interface**: Just run `fixcode yourfile` and get instant suggestions

## Supported Languages

| Language   | Extension | Executor         |
|------------|-----------|------------------|
| Python     | `.py`     | `python3`        |
| C          | `.c`      | `gcc + ./a.out`  |
| C++        | `.cpp`    | `g++ + ./a.out`  |
| JavaScript | `.js`     | `node`           |

For more languages, add to the executors.json

## Installation

### From Source

1. Clone or download this repository
2. Navigate to the project directory
3. Install the package:

```bash
pip install -e .
```

### Requirements

- Python 3.6+
- OpenAI API key (or OpenRouter API key)
- Appropriate compilers/interpreters for the languages you want to debug:
  - `python3` for Python files
  - `gcc` for C files
  - `g++` for C++ files
  - `node` for JavaScript files

## Configuration

Create a `.env` file in your project directory with your API credentials:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
FIXCODE_MODEL=mistralai/mistral-7b-instruct:free
```

### Using OpenRouter (Alternative)

If you prefer to use OpenRouter instead of OpenAI directly:

```env
OPENAI_API_KEY=your_openrouter_key_here
OPENAI_BASE_URL=https://openrouter.ai/api/v1
FIXCODE_MODEL=mistralai/mistral-7b-instruct:free
```

## Usage

### Basic Usage

```bash
fixcode path/to/your/file.py
```

### Specify AI Model

You can specify which AI model to use with the `--model` flag:

```bash
fixcode path/to/your/file.py --model "gpt-4"
fixcode path/to/your/file.py --model "claude-3-sonnet"
fixcode path/to/your/file.py --model "mistralai/mistral-7b-instruct:free"
```

### Set Default Model

You can set a default model in your `.env` file:

```env
FIXCODE_MODEL=gpt-4
```

Or use the `--model` flag once and it will be automatically saved to your `.env` file for future use.


## Project Structure

```
fixcode/
├── fixcode/
│   ├── __init__.py
│   ├── cli.py              # Main CLI application
│   └── executors.json      # Language-specific execution commands
├── setup.py               # Package configuration
├── pyproject.toml         # Build system configuration
├── MANIFEST.in            # Package data files
├── .env                   # API configuration (create this)
├── .gitignore
└── README.md
```

## Command Line Options

```
fixcode [-h] [--model MODEL] filename

Fix broken code using LLM suggestions.

positional arguments:
  filename       Path to the code file to run and fix

optional arguments:
  -h, --help     show this help message and exit
  --model MODEL  OpenRouter/OpenAI model name to use (also configurable via FIXCODE_MODEL in .env)
```

## Dependencies

- `openai`: For AI API communication
- `python-dotenv`: For environment variable management

## Extending Language Support

To add support for new programming languages, edit `fixcode/executors.json`:

```json
{
  ".py": "python3 $file",
  ".c": "gcc $file && ./a.out",
  ".cpp": "g++ $file && ./a.out",
  ".js": "node $file",
  ".go": "go run $file",
  ".java": "javac $file && java $(basename $file .java)"
}
```

The `$file` placeholder will be replaced with the actual file path.
