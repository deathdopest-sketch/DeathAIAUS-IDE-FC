# 🎯 Core AI Model Roles - Quick Reference

## Overview

The Settings dialog now has **4 core model roles** for quick access to your most common development tasks:

1. **💻 Coder** - Code Generation
2. **🗺️ Planner** - Architecture & Design  
3. **🧪 Tester** - Validation & QA
4. **📋 Reviewer** - Code Review & Quality

---

## 🚀 Access in Settings

**To Configure:**
1. Open **AI → Settings** (or **File → Settings**)
2. Go to **"Models"** tab
3. See 4 model dropdowns with recommendations
4. Choose your preferred model for each role
5. Close Settings (auto-saved)

---

## 🎯 The 4 Core Roles

### 1. 💻 **Coder (Code Generation)**

**Purpose:** Generates new code, implements features, writes functions

**Recommended Model:** **THANATOS (22B)**
- Largest and most powerful model
- Best for complex code generation
- Handles multi-file projects
- Deep understanding of languages

**When Used:**
- Creating new features
- Generating boilerplate code
- Implementing complex algorithms
- Writing entire classes/modules

**Alternative Models:**
- **MORRIGAN (7B)** - Faster, good for simple code
- **OSIRIS (13B)** - Good balance of speed/power
- **HEL (7B)** - General-purpose generation

---

### 2. 🗺️ **Planner (Architecture & Design)**

**Purpose:** Designs system architecture, plans project structure, makes high-level decisions

**Recommended Model:** **ODIN (13B)**
- Strategic thinking
- Big-picture view
- Wise architectural decisions
- Experience with patterns

**When Used:**
- Planning new projects
- Designing system architecture
- Breaking down large tasks
- Choosing tech stack
- Creating project roadmaps

**Alternative Models:**
- **THANATOS (22B)** - Maximum planning power
- **OSIRIS (13B)** - Legacy system planning
- **YAMA (13B)** - Quality-focused planning

---

### 3. 🧪 **Tester (Validation & QA)**

**Purpose:** Tests code, validates functionality, finds bugs, ensures quality

**Recommended Model:** **ANUBIS (1.2B)**
- Fast validation
- Efficient testing
- Quick bug detection
- Lightweight but precise

**When Used:**
- Running test suites
- Validating code changes
- Finding bugs
- Checking edge cases
- Quick sanity checks

**Alternative Models:**
- **ARES (7B)** - Aggressive testing
- **MORRIGAN (7B)** - Bug prophet, finds hidden issues
- **SEKHMET (7B)** - Security testing focus

---

### 4. 📋 **Reviewer (Code Review & Quality)**

**Purpose:** Reviews code quality, suggests improvements, checks best practices

**Recommended Model:** **YAMA (13B)**
- Judge of code karma
- Quality-focused
- Best practices expert
- Detailed feedback

**When Used:**
- Code reviews
- Quality audits
- Refactoring suggestions
- Performance optimization
- Security reviews

**Alternative Models:**
- **ODIN (13B)** - Architectural review
- **OSIRIS (13B)** - Legacy code review
- **KALI (7B)** - Destructive review (finds weaknesses)

---

## 💡 How to Use Them

### Example Workflow:

**1. New Feature Development:**
```
Planner (ODIN) → Design the feature
   ↓
Coder (THANATOS) → Implement the code
   ↓
Tester (ANUBIS) → Validate it works
   ↓
Reviewer (YAMA) → Check quality
```

**2. Bug Fix:**
```
Tester (ANUBIS) → Find the bug
   ↓
Coder (THANATOS) → Fix it
   ↓
Reviewer (YAMA) → Ensure fix is clean
```

**3. Refactoring:**
```
Reviewer (YAMA) → Identify issues
   ↓
Planner (ODIN) → Plan improvements
   ↓
Coder (THANATOS) → Refactor code
   ↓
Tester (ANUBIS) → Validate refactor
```

---

## ⚙️ Advanced: Workflow Configuration

**Beyond the 4 core roles**, you can configure **12-step workflows** for specialized tasks:

- **Coding Projects:** Generate → Analyze → Validate
- **Large Projects:** Plan → Implement → Review
- **Quick Tasks:** Prototype → Task → Logic
- **Security Audit:** Detect → Destroy → Test

**Access:** Settings → Models tab → Scroll to "Advanced: Configure Workflows"

---

## 🎨 Customization Tips

### For Speed:
```
Coder:    MORRIGAN (7B)
Planner:  HEL (7B)
Tester:   ANUBIS (1.2B)
Reviewer: MORRIGAN (7B)
```

### For Power:
```
Coder:    THANATOS (22B)
Planner:  ODIN (13B)
Tester:   ARES (7B)
Reviewer: YAMA (13B)
```

### For Balance:
```
Coder:    THANATOS (22B)
Planner:  ODIN (13B)
Tester:   ANUBIS (1.2B)
Reviewer: YAMA (13B)
```
(This is the default recommended setup)

### For Security Focus:
```
Coder:    THANATOS (22B)
Planner:  ODIN (13B)
Tester:   SEKHMET (7B)
Reviewer: KALI (7B)
```

---

## 🔧 Settings vs Workflows

**Settings (4 Roles):**
- Quick access
- Common tasks
- General development
- Easy to change on-the-fly

**Workflows (12 Steps):**
- Specialized tasks
- Multi-step processes
- Project-specific
- More granular control

**Use Both:**
- Settings for day-to-day work
- Workflows for specific project types

---

## 💾 Where Settings Are Saved

**Core Roles:** Stored as IDE preferences (in memory)
**Workflows:** Saved to `workflow_config.json` (persistent)

To reset to defaults:
- Core roles: Just select different models in Settings
- Workflows: Click "🔄 Reset to Defaults" in workflow configurator

---

## 🎉 Summary

**You now have:**
- ✅ 4 core model roles in Settings
- ✅ Quick access dropdowns
- ✅ Smart recommendations for each role
- ✅ Emoji indicators for easy identification
- ✅ Flexibility to choose any of 20 models
- ✅ Plus 12-step workflow configuration for advanced use

**This gives you professional-grade AI model management!**

---

**Copyright © 2025 DeathAIAUS. All rights reserved.**
