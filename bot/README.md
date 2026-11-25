# IDE Automation Bot

A bot that demonstrates the DeathAIAUS IDE by automatically creating and running projects, just like a user would.

## Features

- Launches the IDE automatically
- Creates a complete project with multiple files
- Runs the project to verify it works
- Runs tests to verify functionality
- Generates a summary report

## Usage

### Basic Usage

```bash
python bot/ide_automation_bot.py
```

### What It Does

1. **Launches IDE** - Starts the DeathAIAUS IDE (optional, can work without GUI)
2. **Creates Project** - Creates a demo project with:
   - `main.py` - Main application code
   - `test_calculator.py` - Unit tests
   - `README.md` - Project documentation
   - `requirements.txt` - Dependencies
   - `.gitignore` - Git ignore rules
3. **Runs Project** - Executes the created project
4. **Runs Tests** - Executes unit tests
5. **Generates Summary** - Creates a JSON summary report

## Demo Project

The bot creates a simple calculator application that demonstrates:
- Function definitions
- Error handling
- Unit testing
- Documentation

## Output

The bot creates:
- Project files in `workspace/bot_demo/`
- Summary report in `bot/bot_demo_summary.json`

## Comprehensive Logging

The bot logs **everything** to help debug issues:

- **Console Output** - Real-time progress with timestamps
- **Log Files** - Detailed logs saved to `bot/logs/bot_YYYYMMDD_HHMMSS.log`
- **Debug Information** - File paths, sizes, process IDs, return codes
- **Error Details** - Full tracebacks and error context

### Log Levels

- **INFO** - Normal operations and progress
- **DEBUG** - Detailed technical information
- **WARNING** - Non-critical issues
- **ERROR** - Failures with full tracebacks

### What Gets Logged

- IDE launch process (PID, return codes, stdout/stderr)
- File creation (paths, sizes, verification)
- Project execution (commands, return codes, output)
- Test execution (results, failures)
- Process cleanup (termination, errors)

All logs include timestamps and are saved to files for later analysis.

## Requirements

### Optional (for GUI automation)
```bash
pip install pyautogui
```

Without pyautogui, the bot will:
- Still create projects directly
- Still run and test them
- Just won't interact with the GUI

## Example Output

```
============================================================
IDE AUTOMATION BOT - FULL DEMO
============================================================

[13:45:00] Step 1: Launching IDE...
[13:45:03] ✓ IDE launched successfully

[13:45:05] Step 2: Creating project...
[13:45:05] Created workspace: workspace/bot_demo
[13:45:05] Created: main.py
[13:45:05] Created: README.md
[13:45:05] Created: requirements.txt
[13:45:05] Created: .gitignore
[13:45:05] Created: test_calculator.py
[13:45:05] ✓ Project created successfully

[13:45:06] Step 3: Running project...
[13:45:06] ✓ Project executed successfully

[13:45:07] Step 4: Running tests...
[13:45:07] ✓ All tests passed

[13:45:08] Step 5: Creating summary...
[13:45:08] ✓ Summary created

============================================================
DEMO COMPLETE!
============================================================
Project location: workspace/bot_demo
Files created: 5
  - main.py (1234 bytes)
  - README.md (567 bytes)
  - test_calculator.py (890 bytes)
  - requirements.txt (45 bytes)
  - .gitignore (234 bytes)
```

## Integration

The bot can be integrated into:
- CI/CD pipelines
- Automated testing
- Demo presentations
- Quality assurance

## Customization

Edit `bot/ide_automation_bot.py` to:
- Change the demo project
- Add more files
- Customize project structure
- Add more test scenarios

