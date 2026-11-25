# Bot Logging Guide

The IDE Automation Bot logs **everything** to help you debug issues and understand what's happening.

## Log Locations

### Console Output
- Real-time progress displayed in terminal
- Timestamped messages
- Color-coded status indicators

### Log Files
- Location: `bot/logs/bot_YYYYMMDD_HHMMSS.log`
- Format: Timestamped entries with log levels
- Encoding: UTF-8 (handles all characters)

## Log Levels

### INFO
Normal operations and progress updates:
- Step completion
- File creation
- Process status

### DEBUG
Detailed technical information:
- File paths and sizes
- Process IDs
- Command execution details
- Return codes
- Directory contents

### WARNING
Non-critical issues:
- Missing optional dependencies
- Tests that didn't run
- Processes that didn't terminate cleanly

### ERROR
Failures with full context:
- Exception tracebacks
- Error messages
- Failed operations

## What Gets Logged

### IDE Launch
- IDE script path and size
- Python executable path
- Working directory
- Process PID
- Process return codes
- stdout/stderr output
- Window detection status

### Project Creation
- Workspace directory path
- Directory creation status
- Each file being created:
  - File path
  - Content length
  - File size after creation
  - Verification status
- All files in workspace listing

### Project Execution
- Command being executed
- Working directory
- Process return code
- stdout length and content
- stderr length and content
- Timeout status

### Test Execution
- Test file path and size
- Command being executed
- Test results
- Pass/fail status
- Error output

### Cleanup
- Process termination attempts
- Kill attempts if needed
- Cleanup completion status

## Example Log Entry

```
2025-11-29 14:02:14,673 [DEBUG] Writing file: C:\Users\Death\Desktop\DeathAIAUS-IDE-FC\workspace\bot_demo\main.py
2025-11-29 14:02:14,673 [DEBUG] Content length: 807 characters
2025-11-29 14:02:14,674 [INFO] Created: main.py (846 bytes)
2025-11-29 14:02:14,674 [DEBUG] File verified: True
```

## Debugging Issues

### If IDE Doesn't Launch
Check logs for:
- IDE script path (is it correct?)
- Python executable path
- Process return code
- stdout/stderr output

### If Files Don't Create
Check logs for:
- Workspace directory path
- Permission errors
- File write attempts
- File verification status

### If Project Doesn't Run
Check logs for:
- Command being executed
- Working directory
- Return code
- stdout/stderr output
- Timeout status

### If Tests Fail
Check logs for:
- Test file path
- Import errors
- Assertion failures
- Exception tracebacks

## Log File Analysis

Each log file contains:
1. Initialization info (log file path, bot version)
2. Step-by-step execution
3. All debug information
4. Error tracebacks
5. Final summary

## Tips

1. **Always check the log file** - It has more detail than console output
2. **Look for ERROR entries** - These show what went wrong
3. **Check DEBUG entries** - These show technical details
4. **Compare timestamps** - See how long operations take
5. **Search for keywords** - "ERROR", "FAIL", "Exception" to find issues quickly

## Log Retention

Logs are kept in `bot/logs/` directory. Consider:
- Archiving old logs periodically
- Deleting logs older than 30 days
- Keeping logs for successful runs for reference

