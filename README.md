# Tiny11 Automated Builder

[![Build Tiny11](https://github.com/kelexine/tiny11-automated/actions/workflows/build-tiny11.yml/badge.svg)](https://github.com/kelexine/tiny11-automated/actions/workflows/build-tiny11.yml)

**Automated tool for creating a streamlined Windows 11 ISO with CI/CD support.**

---

## 📋 Overview

Tiny11 Automated Builder provides a **production-ready PowerShell script** to create a minimized Windows 11 ISO image by:

- ✨ **Removing bloatware** (40+ unnecessary apps)
- 🔒 **Disabling telemetry** (complete privacy protection)
- ⚡ **Optimizing performance** (faster boot, less resource usage)
- 🤖 **Full CI/CD automation** (GitHub Actions workflow)
- 🛠️ **System requirement bypass** (TPM, CPU, RAM checks removed)

### 🙏 Attribution

Based on [tiny11 builder by ntdevlabs](https://github.com/ntdevlabs/tiny11builder). Headless version created by **kelexine** for CI/CD automation.

---

## 🚀 Quick Start

### Option 1: GitHub Actions (Recommended)

1. **Fork** this repository
2. Go to **Actions** tab → **Build and Release Tiny11**
3. Click **"Run workflow"** and provide:
   - Windows 11 ISO download URL
   - Edition index (1 = Pro)
4. **Download** the built ISO from Artifacts or GitHub Releases

**Build time**: ~45–80 minutes

### Option 2: Manual Build (PowerShell)

```powershell
# 1. Mount a Windows 11 ISO and note the drive letter (e.g., E:)
# 2. Run PowerShell as Administrator
Set-ExecutionPolicy Bypass -Scope Process

# 3. Run the builder
.\scripts\tiny11maker-headless.ps1 -ISO E -INDEX 1

# With custom scratch drive (if C:\ space is limited)
.\scripts\tiny11maker-headless.ps1 -ISO E -INDEX 1 -SCRATCH D

# Debug mode (keeps temporary files)
.\scripts\tiny11maker-headless.ps1 -ISO E -INDEX 1 -SkipCleanup
```

**Requirements**: Windows 10/11, PowerShell 5.1+, 30GB+ free space, Admin rights

---

## 🔧 Script Parameters

```powershell
.\tiny11maker-headless.ps1
    -ISO <string>              # Drive letter of mounted ISO (e.g., "E")
    -INDEX <int>               # Image index (1=Pro)
    [-SCRATCH <string>]        # Optional: Scratch disk (default: script directory)
    [-SkipCleanup]             # Optional: Keep temp files for debugging
```

---

## 📦 What Gets Removed

### Bloatware Apps (40+ removed)

- Microsoft Teams, OneDrive, Edge
- Xbox Game Bar & Gaming Services
- Clipchamp, Paint 3D, 3D Viewer, Mixed Reality Portal
- Weather, News, Maps, Bing Search
- Skype, Cortana, People, Phone Link
- Copilot, Recall, AI Fabric, CoreAI (Windows 11 25H2+)
- Office Hub, Power Automate, Solitaire, Sticky Notes, To Do
- Get Help, Get Started, Feedback Hub, Quick Assist, DevHome

### Registry Optimizations

- TPM 2.0 / Secure Boot / CPU / RAM requirement bypass
- All telemetry endpoints disabled
- Sponsored apps and consumer features blocked
- OneDrive backup prompts disabled
- Windows Update disabled (can be re-enabled via `services.msc`)
- BitLocker encryption disabled
- Chat icon / Widgets / Cortana startup removed

---

## 📁 Repository Structure

```
tiny11-automated/
├── .github/workflows/
│   └── build-tiny11.yml              # GitHub Actions CI/CD workflow
├── scripts/
│   └── tiny11maker-headless.ps1      # Automated builder script
├── autounattend.xml                  # OOBE bypass & post-install cleanup
├── README.md
└── .gitignore
```

---

## 💾 System Requirements

### For Building ISOs

| Requirement | Minimum | Recommended |
|------------|---------|-------------|
| **OS** | Windows 10 | Windows 11 |
| **PowerShell** | 5.1 | 7.0+ |
| **RAM** | 8GB | 16GB+ |
| **Free Disk Space** | 20GB | 40GB+ |
| **Permissions** | Administrator | Administrator |

### For Running Built ISOs

System requirements are **bypassed** — Tiny11 can run on:
- Any x64 processor (Pentium, Core 2 Duo, etc.)
- 1GB+ RAM (2GB+ recommended)
- 10GB+ storage
- No TPM / Secure Boot required

---

## ⚠️ Disclaimer

This tool is provided "as is" without warranty. You **must** have a valid Windows license. Use at your own risk.

---

## 👨‍💻 Author

- **kelexine**: [GitHub](https://github.com/kelexine)
- **Original**: [ntdevlabs/tiny11builder](https://github.com/ntdevlabs/tiny11builder)
