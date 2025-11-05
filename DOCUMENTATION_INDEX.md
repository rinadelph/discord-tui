# Discordo Python Documentation Index

## Quick Start

Start with **one** of these documents based on your need:

### For Understanding the Project
1. **README.md** - Features, usage, setup instructions
2. **START_HERE.md** - Getting started guide
3. **PROJECT_STRUCTURE.md** - File organization and high-level architecture

### For Understanding Message Display
1. **CODEBASE_ANALYSIS.md** - Comprehensive overview with focus on message rendering
2. **ARCHITECTURE.md** - Detailed message rendering pipeline with diagrams
3. **QUICK_REFERENCE.md** - Fast lookup guide for developers

### For Development & Debugging
1. **QUICK_REFERENCE.md** - Code locations, file maps, debugging tips
2. **ARCHITECTURE.md** - Data flow diagrams
3. **CODEBASE_ANALYSIS.md** - Implementation details

---

## Document Guide

### README.md (6.2K)
**What it covers:**
- Project overview and features
- Installation instructions
- Usage and keybindings
- Configuration options
- Troubleshooting
- Contributing guidelines

**When to read it:** Starting the project, understanding capabilities

---

### PROJECT_STRUCTURE.md (6.7K)
**What it covers:**
- File mapping (Go → Python)
- Key differences between implementations
- Component descriptions
- Status of features (completed/in-progress/not implemented)
- Architecture philosophy

**When to read it:** Understanding overall structure, planning changes

---

### CODEBASE_ANALYSIS.md (17K) [NEW - CREATED FOR YOU]
**What it covers:**
- Comprehensive project overview
- Detailed architecture diagram
- Message display implementation
- Configuration system (TOML loading)
- UI layout and styling
- File location reference (complete list of all files)
- Message rendering pipeline
- Timestamp handling
- Features and implementation status
- Customization points

**When to read it:** Deep understanding of codebase, working on features

**Key sections for message display:**
- "Message Display Implementation" (lines 117-261)
- "Configuration System" (lines 263-360)
- "UI Layout & Styling" (lines 362-451)
- "File Locations Reference" (lines 453-515)

---

### ARCHITECTURE.md (20K) [NEW - CREATED FOR YOU]
**What it covers:**
- High-level architecture diagram (boxes and flows)
- Complete message rendering pipeline (7-stage flow)
- Configuration point details
- File organization
- Important implementation notes
- Data flow diagram
- MVC architecture explanation

**When to read it:** Visualizing system architecture, understanding message flow

**Key sections for message display:**
- "High-Level Architecture Diagram" (lines 1-59)
- "Message Rendering Pipeline" (lines 62-349)
- "Key Configuration Points" (lines 351-413)

---

### QUICK_REFERENCE.md (9.7K) [NEW - CREATED FOR YOU]
**What it covers:**
- Project at a glance
- File map with line numbers
- Key code locations
- Message loading pipeline (visual)
- Timestamp processing (visual)
- Configuration reference
- UI layout CSS
- Rich/Textual styling reference
- API endpoints used
- Data structures
- Key classes and methods
- Implementation details
- Debugging tips
- Common tasks

**When to read it:** Quick lookups, debugging, finding code locations

**Most used sections:**
- "File Map" (where to find things)
- "Key Code Locations" (pipeline flows)
- "Quick Debugging Tips" (where issues might be)

---

### SETUP.md (6.6K)
**What it covers:**
- Installation requirements
- Python environment setup
- Discord account setup
- Token retrieval
- Configuration creation
- Initial testing

**When to read it:** Setting up development environment

---

### START_HERE.md (4.1K)
**What it covers:**
- What Discordo is
- What's currently working
- What's not yet implemented
- How to run it
- Basic testing information

**When to read it:** First-time orientation to the project

---

### TESTING_GUILDS.md (6.8K)
**What it covers:**
- Testing approach for guilds/messages
- Guild loading process
- Message loading process
- Testing steps
- Troubleshooting issues

**When to read it:** Testing the application, debugging guild loading

---

### CHANGES.md (2.5K)
**What it covers:**
- Recent changes to the codebase
- Bug fixes
- Features added
- Status updates

**When to read it:** Understanding what changed recently

---

### FIX_SUMMARY.md (2.1K)
**What it covers:**
- Summary of recent fixes
- Issues that were resolved
- Code changes made

**When to read it:** Understanding recent bugfixes

---

## Document Dependencies

```
README.md (entry point)
├─ Installation/Setup
│  └─ SETUP.md
│
├─ Understanding Features
│  └─ START_HERE.md
│
├─ Understanding Structure
│  └─ PROJECT_STRUCTURE.md
│
└─ Deep Dive
   ├─ CODEBASE_ANALYSIS.md (comprehensive)
   │  ├─ ARCHITECTURE.md (flows and diagrams)
   │  └─ QUICK_REFERENCE.md (quick lookups)
   │
   └─ Testing & Debugging
      ├─ TESTING_GUILDS.md
      ├─ CHANGES.md
      └─ FIX_SUMMARY.md
```

---

## Quick Navigation by Topic

### Message Display
1. Start: CODEBASE_ANALYSIS.md sections "Message Display Implementation"
2. Visual: ARCHITECTURE.md section "Message Rendering Pipeline"
3. Code locations: QUICK_REFERENCE.md section "File Map: Message Display Logic"
4. Debug: QUICK_REFERENCE.md section "Quick Debugging Tips"

### Configuration & Timestamps
1. Overview: CODEBASE_ANALYSIS.md section "Configuration System"
2. Details: ARCHITECTURE.md section "Key Configuration Points"
3. Reference: QUICK_REFERENCE.md section "Configuration Reference"
4. Timestamps: QUICK_REFERENCE.md section "Timestamp Processing"

### UI Layout & Styling
1. Overview: CODEBASE_ANALYSIS.md section "UI Layout & Styling"
2. Structure: QUICK_REFERENCE.md section "UI Layout Structure"
3. Styling: QUICK_REFERENCE.md section "Rich/Textual Styling"

### Architecture & Data Flow
1. High-level: ARCHITECTURE.md section "High-Level Architecture Diagram"
2. Detailed: CODEBASE_ANALYSIS.md section "Architecture Overview"
3. Data flow: ARCHITECTURE.md section "Data Flow Diagram"
4. API calls: QUICK_REFERENCE.md section "API Endpoints Used"

### File Organization
1. Files: PROJECT_STRUCTURE.md section "File Organization"
2. Detailed: CODEBASE_ANALYSIS.md section "File Locations Reference"
3. Quick map: QUICK_REFERENCE.md section "File Map"

### Implementation Status
1. Features: CODEBASE_ANALYSIS.md section "Key Features & Implementation Status"
2. What works: START_HERE.md
3. Changes: CHANGES.md and FIX_SUMMARY.md

### Development Tasks
1. Common tasks: QUICK_REFERENCE.md section "Common Tasks"
2. Setup: SETUP.md
3. Testing: TESTING_GUILDS.md

---

## Reading Time Estimates

| Document | Length | Read Time | Skim Time |
|----------|--------|-----------|-----------|
| README.md | 6K | 15 min | 5 min |
| START_HERE.md | 4K | 10 min | 3 min |
| SETUP.md | 7K | 15 min | 5 min |
| PROJECT_STRUCTURE.md | 7K | 15 min | 5 min |
| CODEBASE_ANALYSIS.md | 17K | 40 min | 15 min |
| ARCHITECTURE.md | 20K | 45 min | 20 min |
| QUICK_REFERENCE.md | 10K | 25 min | 10 min |
| **Total Deep Dive** | **77K** | **180 min** | **60 min** |
| **Quick Orientation** | **17K** | **40 min** | **13 min** |

---

## Recommended Reading Paths

### Path 1: Quick Orientation (30 minutes)
1. README.md (5 min)
2. START_HERE.md (5 min)
3. QUICK_REFERENCE.md - "Project at a Glance" (5 min)
4. QUICK_REFERENCE.md - "File Map" section (15 min)

### Path 2: Understanding Message Display (60 minutes)
1. CODEBASE_ANALYSIS.md - "Message Display Implementation" (20 min)
2. ARCHITECTURE.md - "Message Rendering Pipeline" (20 min)
3. QUICK_REFERENCE.md - "Key Code Locations" (10 min)
4. QUICK_REFERENCE.md - "Quick Debugging Tips" (10 min)

### Path 3: Complete Understanding (180 minutes)
1. README.md (15 min)
2. PROJECT_STRUCTURE.md (15 min)
3. CODEBASE_ANALYSIS.md (40 min)
4. ARCHITECTURE.md (45 min)
5. QUICK_REFERENCE.md (25 min)
6. SETUP.md or TESTING_GUILDS.md (10 min)

### Path 4: Developer Setup & Debug (90 minutes)
1. README.md (5 min)
2. SETUP.md (15 min)
3. QUICK_REFERENCE.md (25 min)
4. ARCHITECTURE.md - sections on config and debugging (25 min)
5. TESTING_GUILDS.md (15 min)

---

## Key Takeaways Summary

### Architecture
- Three-layer architecture: UI (Textual widgets) → Logic (DiscordoApp) → API (Discord REST)
- Message display handled by MessagesPanel using Rich.Text for styling
- Configuration system loads TOML files with defaults and user overrides

### Message Display Flow
1. User selects channel → triggers event
2. Async API call fetches last 50 messages
3. Messages processed: timestamp, author color, timezone conversion
4. Rich.Text objects created with styles
5. Written to RichLog widget with word wrapping

### Key Files
- **Message display**: `discordo/cmd/application.py` (MessagesPanel, _format_message)
- **Configuration**: `discordo/internal/config.py` (Timestamps, Theme, Keys)
- **Styling**: `discordo/internal/theme.py` (Style, Theme dataclasses)
- **Entry point**: `discordo/cmd/cmd.py` → `main.py`

### Important Implementation Details
- Timestamps hardcoded as '%Y-%m-%d %H:%M:%S' (not using config format)
- Timezone hardcoded as America/New_York
- Author colors fetched from member roles (async API calls)
- Message wrapping enabled via RichLog `wrap=True`

### Customization Points
- Timestamp format: `config.toml [timestamps] format`
- Display width: CSS in `application.py`
- Colors/styles: Theme section in `config.toml` and code

---

## Using These Docs During Development

### When you need to...

**Find where a feature is implemented**
→ QUICK_REFERENCE.md "File Map" → locate file and line numbers

**Understand how messages are rendered**
→ ARCHITECTURE.md "Message Rendering Pipeline" → visualize 7-stage flow

**Debug a timestamp issue**
→ QUICK_REFERENCE.md "Quick Debugging Tips" → check specific locations

**Add a new configuration option**
→ CODEBASE_ANALYSIS.md "Configuration System" → understand TOML loading

**Understand widget styling**
→ QUICK_REFERENCE.md "Rich/Textual Styling" → copy style examples

**Find an API endpoint**
→ QUICK_REFERENCE.md "API Endpoints Used" → see all endpoints

**Optimize message loading**
→ ARCHITECTURE.md "Important Implementation Notes" → see performance issues

---

## Contributing to Documentation

When adding new features or fixing bugs:
1. Update the relevant section in CODEBASE_ANALYSIS.md
2. Update "Key Features & Implementation Status" if applicable
3. Update QUICK_REFERENCE.md file locations if code moved
4. Add entry to CHANGES.md

---

## Questions & Answers

**Q: I'm new to the project. Where should I start?**
A: Read README.md first, then follow "Path 1: Quick Orientation"

**Q: I need to understand message display.**
A: Follow "Path 2: Understanding Message Display"

**Q: I want to modify timestamp formatting.**
A: Read QUICK_REFERENCE.md "Timestamp Processing" section

**Q: Where's the main application code?**
A: `discordo/cmd/application.py` - see QUICK_REFERENCE.md "File Map"

**Q: How does configuration work?**
A: See CODEBASE_ANALYSIS.md "Configuration System" section

**Q: I found a bug. Where do I look?**
A: Use QUICK_REFERENCE.md "Quick Debugging Tips" for specific locations

---

*Last updated: November 5, 2024*
*Documentation covers: Discordo Python - Discord TUI Client*
