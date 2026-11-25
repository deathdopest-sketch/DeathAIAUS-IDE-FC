#!/usr/bin/env python3
"""
Death Pantheon Model Renamer
Renames all AI models to DeathAIAUS branded names
"""

import os
import json
import shutil
from pathlib import Path

# Load the pantheon configuration
with open('death_pantheon.json', 'r', encoding='utf-8') as f:
    pantheon_data = json.load(f)

# Create the renaming map
rename_map = {}
for old_filename, info in pantheon_data['pantheon'].items():
    # Get the base filename without path
    old_name = old_filename
    
    # Create new branded name
    # Format: DeathAIAUS-DEITY_NAME-SIZE-QUANT.gguf
    deity_name = info['name'].upper()
    
    # Extract size and quant from original filename
    # Example: codestral-22b-q4_k_m.gguf -> 22B-Q4_K_M
    parts = old_name.lower().replace('.gguf', '').split('-')
    
    size_part = ''
    quant_part = ''
    
    for i, part in enumerate(parts):
        # Find size (like 22b, 7b, 1.2b, etc.)
        if 'b' in part and any(c.isdigit() for c in part):
            size_part = part.upper().replace('_', '.').replace('B', 'B')
        
        # Find quantization (like q4_k_m, q8_0, etc.)
        if part.startswith('q') and any(c.isdigit() for c in part):
            # Collect full quant (might be q4_k_m or q4_0)
            quant_part = part.upper().replace('_', '_')
    
    # Build new filename
    new_name = f"DeathAIAUS-{deity_name}"
    if size_part:
        new_name += f"-{size_part}"
    if quant_part:
        new_name += f"-{quant_part}"
    new_name += ".gguf"
    
    rename_map[old_name] = new_name

# Define the Google Drive paths to search
search_paths = [
    r'G:\My Drive\DeathAIAUS_PANTHEON',
    r'G:\My Drive\DeathAIAUS_PANTHEON\LMStudio_Models',
    r'G:\My Drive\DeathAIAUS_PANTHEON\GPT4All_Original',
    # Also check old paths in case some models are still there
    r'G:\My Drive\GPT4All_Models',
    r'G:\My Drive\GPT4All_Models\LMStudio_Models',
    r'G:\My Drive\GPT4All_Models\GPT4All_Original'
]

print("=" * 80)
print("🏛️ DEATH'S PANTHEON - Model Renamer")
print("=" * 80)
print()

# Find all models and their paths
models_to_rename = []

for base_path in search_paths:
    if not os.path.exists(base_path):
        print(f"⚠️  Path not found: {base_path}")
        continue
    
    print(f"🔍 Scanning: {base_path}")
    
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.gguf'):
                file_lower = file.lower()
                
                # Check if this file matches any in our rename map
                for old_name, new_name in rename_map.items():
                    if old_name.lower() == file_lower:
                        full_path = os.path.join(root, file)
                        new_path = os.path.join(root, new_name)
                        
                        # Get deity info for display
                        deity_info = pantheon_data['pantheon'].get(old_name, {})
                        
                        models_to_rename.append({
                            'old_path': full_path,
                            'new_path': new_path,
                            'old_name': file,
                            'new_name': new_name,
                            'deity': deity_info.get('name', 'Unknown'),
                            'emoji': deity_info.get('emoji', '🤖')
                        })
                        break

print()
print("=" * 80)
print(f"Found {len(models_to_rename)} models to rename")
print("=" * 80)
print()

if not models_to_rename:
    print("❌ No models found to rename!")
    print("   Make sure your models are in the correct directories.")
    exit(0)

# Show preview
print("📋 PREVIEW - What will be renamed:")
print()

for i, model in enumerate(models_to_rename, 1):
    print(f"{i}. {model['emoji']} {model['deity']}")
    print(f"   OLD: {model['old_name']}")
    print(f"   NEW: {model['new_name']}")
    print(f"   PATH: {os.path.dirname(model['old_path'])}")
    print()

# Auto-proceed (no confirmation needed - it's just renaming files, easy to rename back)
print("=" * 80)
print("✅ Auto-proceeding with rename (just file names, no data loss)...")
print("=" * 80)

print()
print("=" * 80)
print("🔄 Renaming models...")
print("=" * 80)
print()

# Perform the renaming
success_count = 0
error_count = 0

for model in models_to_rename:
    try:
        # Check if target already exists
        if os.path.exists(model['new_path']):
            print(f"⚠️  SKIP: {model['new_name']} (already exists)")
            continue
        
        # Rename the file
        shutil.move(model['old_path'], model['new_path'])
        print(f"✅ RENAMED: {model['emoji']} {model['deity']}")
        print(f"   → {model['new_name']}")
        success_count += 1
    except Exception as e:
        print(f"❌ ERROR: {model['old_name']}")
        print(f"   {str(e)}")
        error_count += 1

print()
print("=" * 80)
print("✅ COMPLETE!")
print("=" * 80)
print(f"✅ Successfully renamed: {success_count} models")
if error_count > 0:
    print(f"❌ Errors: {error_count} models")
print()
print("🎉 Your Death Pantheon is ready!")
print("   Restart the IDE to see the new names in the model list.")
print()
