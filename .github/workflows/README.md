# CodeQL Security Scanning Automation

This repository uses **GitHub CodeQL Advanced** static application security testing (SAST) to automatically scan code for security vulnerabilities, memory leaks, and logic flaws. 

The analysis is tailored specifically for our dual-stack project containing both **Python scripts** and **Arduino C++ firmware**.

---

## 🛠️ How It Works

The workflow executes on a matrix strategy to scan both languages in parallel using CodeQL's lightweight **buildless mode** (`build-mode: none`).

### The Arduino (.ino) Compatibility Fix
CodeQL's standard C++ indexer does not natively recognize files ending in `.ino`. To bypass this limitation without requiring a complex, hardware-specific compilation environment, the workflow includes a pre-scan automation step:
1. It maps out the repository structure looking for any `*.ino` files.
2. It dynamically creates temporary copies of these files with a standard `*.cpp` extension inside the ephemeral GitHub Actions runner environment.
3. CodeQL treats these files as standard C++ files, successfully parsing the logic, buffers, and variables.

---

## 📅 Trigger Events

The workflow runs entirely in the background based on the following automation logic:
* **Code Pushes:** Automatically triggers whenever code is pushed directly to the `main` branch.
* **Pull Requests:** Automatically scans any incoming pull requests targeting the `main` branch to catch vulnerabilities *before* they are merged.
* **Weekly Schedule:** Runs a baseline health sweep every Saturday at 23:20 UTC (`20 23 * * 6`).

---

## 📂 File Architecture

For the automation to function, the script must be placed precisely within this directory structure at the root of the repository:

```text
.
└── .github/
    └── workflows/
        └── codeql.yml  <-- This configuration file
