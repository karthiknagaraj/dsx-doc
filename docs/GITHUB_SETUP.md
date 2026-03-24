# GitHub Repository Setup Guide

Complete instructions for creating a GitHub repository and pushing your project with full documentation.

---

## Step 1: Create GitHub Repository

### Option A: Web Browser

1. Go to https://github.com/new
2. Fill in repository details:
   - **Repository name**: `dsx-doc-assistant`
   - **Description**: `Parse IBM DataStage .dsx exports and generate AI-powered documentation`
   - **Visibility**: Public (for open source) or Private
   - **Initialize with**: None (we already have files)
3. Click **Create repository**

### Option B: GitHub CLI

```bash
# Install GitHub CLI if needed
# https://cli.github.com/

# Create repository
gh repo create dsx-doc-assistant \
  --public \
  --source=. \
  --remote=origin \
  --push
```

---

## Step 2: Prepare Repository

### Initialize Git (if not done)

```powershell
# Navigate to project directory
cd c:\Users\karthik.nagaraj\Downloads\OneDrive_1_3-24-2026\dsx-doc-assistant-v1.0

# Initialize git repository
git init

# Check status
git status
```

### Verify .gitignore

Ensure `.gitignore` contains:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
*.egg
*.egg-info/
venv/
env/

# Environment
.env
.env.local
.env.*.local
.streamlit/secrets.toml

# Database
*.sqlite
*.db
dsx_graph_all.sqlite

# Generated files
dsx_docs_output/
*.md.bak
.dsx_checksums.json

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Test coverage
htmlcov/
.coverage
.pytest_cache/
```

---

## Step 3: Configure Git User

```powershell
# Set your identity (one-time)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Verify
git config --global --list
```

---

## Step 4: Add Files to Git

```powershell
# Stage all files
git add .

# Review what will be committed
git status

# Commit with message
git commit -m "Initial commit: DSX Documentation Assistant project

- CI/CD integration with GitHub Actions
- Streamlit interactive UI
- Command-line interface for batch processing
- Comprehensive documentation and API reference"
```

---

## Step 5: Connect to GitHub

### Create SSH Key (Recommended)

```powershell
# Generate SSH key if you don't have one
ssh-keygen -t ed25519 -C "your.email@example.com"

# Press Enter for default location
# Add a strong passphrase

# Copy public key
Get-Content ~/.ssh/id_ed25519.pub | Set-Clipboard

# Add to GitHub
# Go to https://github.com/settings/keys
# Click "New SSH key"
# Paste the key from clipboard
# Name it "My Computer"
# Click "Add SSH key"
```

### Add Remote (SSH)

```powershell
# Replace YOUR-USERNAME
git remote add origin git@github.com:YOUR-USERNAME/dsx-doc-assistant.git

# Verify
git remote -v
```

### Add Remote (HTTPS Alternative)

If you prefer HTTPS:

```powershell
git remote add origin https://github.com/YOUR-USERNAME/dsx-doc-assistant.git

# Test connection
git ls-remote origin
```

---

## Step 6: Push to GitHub

```powershell
# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main

# Watch for completion
# Should see:
# * [new branch]      main -> main
# branch 'main' set to track 'origin/main'.
```

---

## Step 7: Enable GitHub Features

### Protect Main Branch

1. Go to repository Settings → Branches
2. Add branch protection rule for `main`:
   - [x] Require pull request reviews before merging
   - [x] Require status checks to pass before merging
   - [x] Include administrators in restrictions

### Enable GitHub Pages (Optional)

For documentation website:

1. Settings → Pages
2. **Build and deployment**:
   - Source: Deploy from a branch
   - Select: `main` / `docs`
3. Choose theme or custom domain

### Enable Discussions (Optional)

1. Settings → General
2. Under "Features":
   - [x] Enable Discussions
   - [x] Enable Issues

### Add Topics

1. Settings → General
2. Under "About":
   - Click **Add topics**
   - Add: `datastage`, `documentation`, `etl`, `python`, `streamlit`, `ai`

---

## Step 8: Create GitHub Secrets (for CI/CD)

### Add API Key Secret

1. Go to Settings → Secrets and variables → Actions
2. Click **New repository secret**
3. **Name**: `DSX_API_KEY`
4. **Value**: Your OpenRouter API key
5. Click **Add secret**

### Verify Workflow Can Access

The `.github/workflows/generate-docs.yml` will use:

```yaml
env:
  DSX_API_KEY: ${{ secrets.DSX_API_KEY }}
```

---

## Step 9: Configure GitHub Actions

The workflow file `.github/workflows/generate-docs.yml` should contain:

```yaml
name: Generate DSX Documentation

on:
  push:
    paths:
      - 'dsx_files_input/**/*.dsx'
    branches:
      - main

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Generate documentation
        env:
          DSX_API_KEY: ${{ secrets.DSX_API_KEY }}
        run: |
          python dsx_docs_cli.py \
            --input ./dsx_files_input/ \
            --output ./dsx_docs_output/ \
            --skip-unchanged \
            --fail-on-error
      
      - name: Commit and Push
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add dsx_docs_output/
          git diff --quiet && git diff --cached --quiet || \
            (git commit -m "docs: Auto-generated DSX documentation" && \
             git push)
```

---

## Step 10: Verify Setup

### Check Repository Status

```powershell
# Verify remote is set
git remote -v

# Verify branch tracking
git branch -v

# Check recent pushes
git log --oneline -5
```

### Test CI/CD

1. Add a DSX file to `dsx_files_input/`:
   ```powershell
   cp "dsx_files_input/BilRev_Fact.dsx" .git/keep  # temporary
   git add dsx_files_input/BilRev_Fact.dsx
   git commit -m "test: Add sample DSX file"
   git push
   ```

2. Watch GitHub Actions:
   - Go to repository **Actions** tab
   - Watch workflow run
   - Check logs for errors

3. Verify generated docs:
   - Check `dsx_docs_output/` folder
   - Should contain `.md` files

---

## Step 11: Organization Setup (Optional)

### Create Organization

For team/enterprise use:

1. Go to https://github.com/organizations/new
2. Fill in details
3. Complete signup

### Add Team Members

1. Settings → Members
2. Click **Invite a member**
3. Search for username
4. Grant appropriate role

### Configure Org Settings

1. Settings → General:
   - [x] Enable Issues
   - [x] Enable Discussions
   - [x] Enable Projects

---

## Common Git Commands

### Everyday Usage

```powershell
# Check status
git status

# Stage files
git add .
git add specific_file.py

# Commit
git commit -m "feat: Add new feature"

# Push
git push

# Pull latest
git pull

# View history
git log --oneline
```

### Branch Management

```powershell
# Create feature branch
git checkout -b feature/my-feature

# Switch branch
git checkout main

# Delete branch
git branch -d feature/my-feature

# Push branch to GitHub
git push -u origin feature/my-feature
```

### Pull Requests

```powershell
# Push feature branch
git push -u origin feature/my-feature

# Then on GitHub.com:
# 1. Your branch notifications shows "Compare & pull request"
# 2. Click that button
# 3. Fill in PR description
# 4. Click "Create pull request"
```

---

## Documentation Structure on GitHub

```
dsx-doc-assistant/
├── README.md                          # Main overview
├── docs/
│   ├── ARCHITECTURE.md               # System design
│   ├── INSTALLATION.md               # Setup instructions
│   ├── USAGE.md                      # How to use
│   ├── API_REFERENCE.md              # Technical API docs
│   ├── DEPLOYMENT.md                 # Production deployment
│   ├── CONTRIBUTING.md               # Contributing guide
│   └── TROUBLESHOOTING.md            # Problem solving
├── .github/
│   └── workflows/
│       └── generate-docs.yml         # CI/CD automation
├── dsx_files_input/                  # Input DSX files (samples)
├── dsx_docs_output/                  # Generated documentation
├── tests/                            # Test files
├── requirements.txt                  # Dependencies
├── docker-compose.yml                # Docker setup
├── Dockerfile                        # Container image
└── *.py                             # Python modules
```

---

## Next Steps After Setup

1. **Verify CI/CD Works**:
   - Push a DSX file
   - Watch Actions tab
   - Check generated docs

2. **Add README Badges**:
   ```markdown
   [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
   [![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
   ![Tests](https://github.com/YOUR-USERNAME/dsx-doc-assistant/actions/workflows/generate-docs.yml/badge.svg)
   ```

3. **Create Release**:
   - Go to Releases
   - Click "Create a new release"
   - Tag: `v1.0.0`
   - Add changelog notes

4. **Enable Discussions**:
   - Discussions tab for community Q&A
   - Encourage contributions

5. **Add CONTRIBUTING.md**:
   - Link to [CONTRIBUTING.md](../../docs/CONTRIBUTING.md)
   - Make it easy for others to contribute

---

## Troubleshooting GitHub Setup

### Issue: "fatal: Not a git repository"

```powershell
# Initialize git if needed
cd your-project-directory
git init
```

### Issue: "Permission denied (publickey)"

SSH key not found or not configured:

```powershell
# Verify SSH key exists
Test-Path ~/.ssh/id_ed25519

# Test connection
ssh -T git@github.com

# Should show: "Hi USERNAME! You've successfully authenticated..."
```

### Issue: "fatal: 'origin' does not appear to be a 'git' repository"

Remote not configured:

```powershell
git remote add origin git@github.com:YOUR-USERNAME/dsx-doc-assistant.git
git remote -v
```

### Issue: "rejected ... because the remote contains work that you do not have locally"

```powershell
# Pull first
git pull origin main

# Then push
git push origin main
```

---

## Security Reminders

✅ **DO:**
- Store API key in GitHub Secrets
- Use SSH keys for authentication
- Keep `.env` in `.gitignore`
- Review PRs before merging

❌ **DON'T:**
- Commit API keys to repository
- Share SSH private keys
- Use weak passwords
- Grant unnecessary permissions

---

## Resources

- [GitHub Docs](https://docs.github.com)
- [Git Tutorial](https://git-scm.com/book)
- [GitHub CLI Documentation](https://cli.github.com/)
- [SSH Key Setup](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)

