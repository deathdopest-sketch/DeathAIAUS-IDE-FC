#!/usr/bin/env python3
"""
Quick test to verify Death Pantheon models are detected
"""

import os
import json

# Load pantheon config
with open('death_pantheon.json', 'r', encoding='utf-8') as f:
    pantheon = json.load(f)

print("=" * 80)
print("TESTING DEATH PANTHEON MODEL DETECTION")
print("=" * 80)
print()

# Define search paths
search_paths = [
    r'G:\My Drive\DeathAIAUS_PANTHEON',
    r'G:\My Drive\DeathAIAUS_PANTHEON\LMStudio_Models',
    r'G:\My Drive\DeathAIAUS_PANTHEON\GPT4All_Original'
]

print("Scanning folders:")
for path in search_paths:
    exists = "[OK]" if os.path.exists(path) else "[X]"
    print(f"  {exists} {path}")
print()

# Find all .gguf files
found_models = []
for base_path in search_paths:
    if not os.path.exists(base_path):
        continue
    
    print(f"Scanning: {base_path}")
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.gguf'):
                full_path = os.path.join(root, file)
                size_gb = os.path.getsize(full_path) / (1024**3)
                found_models.append({
                    'file': file,
                    'path': full_path,
                    'size': size_gb
                })
                print(f"  [OK] Found: {file} ({size_gb:.1f}GB)")

print()
print("=" * 80)
print(f"SUMMARY: Found {len(found_models)} model files")
print("=" * 80)
print()

# Check if they match pantheon deities
print("Matching to Death Pantheon:")
print()

matched = 0
unmatched = 0

for model in found_models:
    filename = model['file'].lower()
    
    # Check if it's a DeathAIAUS branded file
    if 'deathaius' in filename:
        # Extract deity name
        parts = filename.replace('deathaius-', '').split('-')
        if parts:
            deity_name = parts[0].upper()
            
            # Find in pantheon
            found = False
            for model_file, info in pantheon['pantheon'].items():
                if info['name'].upper() == deity_name:
                    print(f"[OK] {model['file']}")
                    print(f"   -> {info['name']} - {info['role']}")
                    matched += 1
                    found = True
                    break
            
            if not found:
                print(f"[!] {model['file']}")
                print(f"   -> No match found for deity: {deity_name}")
                unmatched += 1
    else:
        # Check original filename
        found = False
        for model_file, info in pantheon['pantheon'].items():
            if model_file.lower() == filename:
                print(f"[OK] {model['file']} (original name)")
                print(f"   -> {info['name']} - {info['role']}")
                matched += 1
                found = True
                break
        
        if not found:
            print(f"[!] {model['file']}")
            print(f"   -> Not in Death Pantheon")
            unmatched += 1

print()
print("=" * 80)
print(f"[OK] Matched to pantheon: {matched}")
print(f"[!] Not matched: {unmatched}")
print("=" * 80)
print()

if matched > 0:
    print("SUCCESS! Your Death Pantheon models are detected!")
    print("The IDE will show them with deity names.")
else:
    print("WARNING: No models matched to pantheon")
    print("Check if files are renamed correctly.")
print()
