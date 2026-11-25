# 🏛️ Death Pantheon - Model Renaming Guide

## Overview
This guide shows the before/after names for all your AI models with the Death Pantheon branding.

## Naming Convention
**Format:** `DeathAIAUS-DEITY_NAME-SIZE-QUANT.gguf`

Example: `DeathAIAUS-THANATOS-22B-Q4_K_M.gguf`

---

## 👑 PRIMARY PANTHEON

### THANATOS (Greek - Personification of Death)
- **OLD:** `codestral-22b-q4_k_m.gguf`
- **NEW:** `DeathAIAUS-THANATOS-22B-Q4_K_M.gguf`
- **Role:** Primary Code Generator (13.3GB)

### MORRIGAN (Celtic - Goddess of Death, War, and Prophecy)
- **OLD:** `qwen2.5-coder-7b-instruct-q4_0.gguf`
- **NEW:** `DeathAIAUS-MORRIGAN-7B-Q4_0.gguf`
- **Role:** Code Analyst & Bug Prophet (4.7GB)

### ANUBIS (Egyptian - Judge of Souls)
- **OLD:** `LFM2-1.2B-Q8_0.gguf`
- **NEW:** `DeathAIAUS-ANUBIS-1.2B-Q8_0.gguf`
- **Role:** Quick Validator/Tester (1.2GB)

### HEL (Norse - Goddess of the Underworld)
- **OLD:** `mistral-7b-instruct-v0.1.Q4_0.gguf`
- **NEW:** `DeathAIAUS-HEL-7B-Q4_0.gguf`
- **Role:** General-Purpose Assistant (4.1GB)

---

## ⚔️ WARRIOR PANTHEON

### ARES (Greek - God of War)
- **OLD:** `Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf`
- **NEW:** `DeathAIAUS-ARES-7B-Q4_0.gguf`
- **Role:** Aggressive Debugging & Testing (4.1GB)

### KALI (Hindu - Goddess of Destruction)
- **OLD:** `mistral-7b-openorca.gguf2.Q4_0.gguf`
- **NEW:** `DeathAIAUS-KALI-7B-Q4_0.gguf`
- **Role:** Code Refactoring (4.1GB)

### SEKHMET (Egyptian - Warrior Goddess)
- **OLD:** `ghost-7b-v0.9.1-Q4_0.gguf`
- **NEW:** `DeathAIAUS-SEKHMET-7B-Q4_0.gguf`
- **Role:** Security Testing (4.1GB)

---

## 🧙 WISDOM PANTHEON

### OSIRIS (Egyptian - God of Resurrection)
- **OLD:** `wizardlm-13b-v1.2.Q4_0.gguf`
- **NEW:** `DeathAIAUS-OSIRIS-13B-Q4_0.gguf`
- **Role:** Legacy Code Resurrection (7.4GB)

### YAMA (Hindu - Lord of Death, Judge of Karma)
- **OLD:** `gpt4all-13b-snoozy-q4_0.gguf`
- **NEW:** `DeathAIAUS-YAMA-13B-Q4_0.gguf`
- **Role:** Code Review & Quality (7.4GB)

### ODIN (Norse - All-Father, God of Wisdom)
- **OLD:** `nous-hermes-llama2-13b.Q4_0.gguf`
- **NEW:** `DeathAIAUS-ODIN-13B-Q4_0.gguf`
- **Role:** Strategic Planning (7.4GB)

---

## 🌊 UNDERWORLD PANTHEON

### CHARON (Greek - Ferryman of the Dead)
- **OLD:** `dolphin-2.8-mistral-7b-v02-Q6_K.gguf`
- **NEW:** `DeathAIAUS-CHARON-7B-Q6_K.gguf`
- **Role:** Data Transfer & API Integration (5.9GB)

### HADES (Greek - God of the Underworld)
- **OLD:** `gpt4all-falcon-newbpe-q4_0.gguf`
- **NEW:** `DeathAIAUS-HADES-Q4_0.gguf`
- **Role:** Database & Backend (4.2GB)

### ERESHKIGAL (Mesopotamian - Queen of the Underworld)
- **OLD:** `mpt-7b-chat.gguf4.Q4_0.gguf`
- **NEW:** `DeathAIAUS-ERESHKIGAL-7B-Q4_0.gguf`
- **Role:** Conversational AI (3.8GB)

---

## 🔮 MINOR DEITIES

### AZRAEL (Islamic - Angel of Death)
- **OLD:** `DeepSeek-R1-Distill-Llama-8B-Q4_0.gguf`
- **NEW:** `DeathAIAUS-AZRAEL-8B-Q4_0.gguf`
- **Role:** Code Analysis (4.7GB)

### PSYCHE (Greek - Goddess of the Soul)
- **OLD:** `DeepSeek-R1-Distill-Qwen-1.5B-Q4_0.gguf`
- **NEW:** `DeathAIAUS-PSYCHE-1.5B-Q4_0.gguf`
- **Role:** Lightweight Reasoning (1.1GB)

### MORANA (Slavic - Goddess of Winter)
- **OLD:** `orca-mini-3b-gguf2-q4_0.gguf`
- **NEW:** `DeathAIAUS-MORANA-3B-Q4_0.gguf`
- **Role:** Quick Tasks (1.9GB)

### IZANAMI (Japanese - Goddess of Death and Creation)
- **OLD:** `qwen2-1_5b-instruct-q4_0.gguf`
- **NEW:** `DeathAIAUS-IZANAMI-1.5B-Q4_0.gguf`
- **Role:** Rapid Prototyping (937MB)

---

## 🎨 SPECIAL PURPOSE

### NEPHTHYS (Egyptian - Goddess of Mourning)
- **OLD:** `nomic-embed-text-v1.5.f16.gguf`
- **NEW:** `DeathAIAUS-NEPHTHYS-F16.gguf`
- **Role:** Text Embeddings (274MB)

### PERSEPHONE (Greek - Queen of the Underworld)
- **OLD:** `v2-1_768-nonema-pruned-Q8_0.gguf`
- **NEW:** `DeathAIAUS-PERSEPHONE-Q8_0.gguf`
- **Role:** Image Generation (2.0GB)

---

## 📝 How to Rename

### Automatic Renaming:
```bash
python rename_pantheon_models.py
```

This script will:
1. Scan your Google Drive model folders
2. Show you a preview of all changes
3. Ask for confirmation
4. Rename all models to the Death Pantheon branding

### Manual Renaming:
If you prefer to rename manually, use the OLD → NEW names listed above.

**Important Notes:**
- ⚠️ Make backups before renaming!
- ⚠️ Close any applications using the models
- ⚠️ Restart the IDE after renaming to see new names

---

## 🎉 After Renaming

Your model dropdown will show:
- `👑 THANATOS - Primary Code Generator`
- `🔮 MORRIGAN - Code Analyst & Bug Prophet`
- `⚖️ ANUBIS - Quick Validator/Tester`
- And more...

All branded as **DeathAIAUS** models with clear, powerful names!

---

**Copyright © 2025 DeathAIAUS. All rights reserved.**
