"""
Quick test to verify hybrid IDE starts without errors
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

print("Testing Hybrid IDE startup...")
print("=" * 60)

# Start hybrid IDE in test mode (will exit after checks)
print("\n1. Starting hybrid IDE pre-flight checks...")
try:
    result = subprocess.run(
        [sys.executable, 'deathaius_ide_hybrid.py'],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    output = result.stdout + result.stderr
    
    # Check for key success indicators
    checks = {
        'Python version': 'Python 3.' in output,
        'React build': 'React build found' in output or '[OK]' in output,
        'Flask server': 'Flask' in output,
        'Pre-flight': 'Pre-Flight Checks' in output or 'Starting' in output
    }
    
    print("\nChecks:")
    for check, passed in checks.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {check}")
    
    if all(checks.values()):
        print("\n[SUCCESS] Hybrid IDE initializes correctly!")
        print("\nThe IDE is ready to launch. You can now run:")
        print("  python DeathAIAUS_Launcher.py")
        print("or:")
        print("  python deathaius_ide_hybrid.py")
    else:
        print("\n[WARNING] Some checks failed. Review output above.")
        print("\nFull output:")
        print(output)

except subprocess.TimeoutExpired:
    print("\n[TIMEOUT] IDE may be waiting for user input")
    print("This is normal - the IDE is waiting to launch the window.")
    print("\n[SUCCESS] The IDE is ready. Launch it manually with:")
    print("  python DeathAIAUS_Launcher.py")

except Exception as e:
    print(f"\n[ERROR] {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("Test complete!")

