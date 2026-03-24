# GitHub Auto-Documentation Setup Guide

## 🎯 Goal
Automatically generate markdown documentation whenever you push .dsx files to GitHub.

---

## 📁 Repository Structure

```
your-github-repo/
├── dsx_files_input/              # Put your .dsx files here
│   ├── Job1.dsx
│   ├── Job2.dsx
│   └── ...
├── dsx_docs_output/              # Generated docs appear here (auto-created)
│   ├── Job1__Job1.md
│   ├── Job2__Job2.md
│   └── .dsx_checksums.json      # Tracks changes
├── .github/
│   └── workflows/
│       └── generate-docs.yml    # The automation script
└── dsx_docs_cli.py              # The CLI tool
```

---

## 🚀 Setup (5 Steps)

### **Step 1: Create the dsx_files_input folder**

```bash
# In your repo, create a folder for .dsx files
mkdir dsx_files_input

# Add your .dsx files
# (Copy your DataStage exports into this folder)
```

### **Step 2: Add the GitHub Actions workflow**

The file `.github/workflows/generate-docs.yml` has already been created! ✅

This workflow will:
- ✅ Run whenever you push .dsx files
- ✅ Generate markdown documentation
- ✅ Commit the docs back to your repo

### **Step 3: Add your API key as a GitHub secret**

1. Go to your GitHub repository
2. Click **Settings** (top menu)
3. Click **Secrets and variables** → **Actions** (left sidebar)
4. Click **New repository secret**
5. Name: `DSX_API_KEY`
6. Value: Your OpenRouter API key (e.g., `sk-...`)
7. Click **Add secret**

### **Step 4: Push to GitHub**

```powershell
# Add all files
git add .

# Commit
git commit -m "Add auto-documentation workflow"

# Push to GitHub
git push origin main
```

### **Step 5: Test it!**

```powershell
# Add a .dsx file to the dsx_files_input folder
cp "C:\path\to\some\job.dsx" ./dsx_files_input/

# Commit and push
git add dsx_files_input/
git commit -m "Add new DSX job"
git push origin main

# Watch GitHub Actions run!
# Go to: GitHub repo → Actions tab → See the workflow run
```

---

## 🔄 How It Works

### **Automatic Flow:**

```
1. You push .dsx file to GitHub
         ↓
2. GitHub Actions detects the change
         ↓
3. Workflow runs: python dsx_docs_cli.py --input ./dsx_files/ --output ./docs/
         ↓
4. Documentation generated
         ↓
5. Workflow commits docs/ back to your repo
         ↓
6. Done! Docs are now in your repo
```

### **What Happens:**

| Action | Result |
|--------|--------|
| Push `dsx_files_input/job.dsx` | Workflow triggers |
| Workflow runs | Generates `dsx_docs_output/job__job.md` |
| Workflow commits | Docs appear in your repo |
| Pull the changes | See the generated markdown files |

---

## 📊 Viewing Results

### **Option 1: On GitHub**
1. Go to your repository
2. Navigate to the `dsx_docs_output/` folder
3. Click on any `.md` file
4. GitHub will render it beautifully!

### **Option 2: Locally**
```powershell
# Pull the latest changes (includes generated docs)
git pull

# View the docs
ls ./dsx_docs_output/
code ./dsx_docs_output/Job1__Job1.md
```

### **Option 3: Check the workflow logs**
1. Go to your repo → **Actions** tab
2. Click on the latest workflow run
3. Expand **Generate DSX documentation** to see logs
4. Check `results.json` artifact for details

---

## ⚙️ Configuration Options

### **Change the input/output folders:**

Edit `.github/workflows/generate-docs.yml`:

```yaml
- name: Generate DSX documentation
  run: |
    python dsx_docs_cli.py \
      --input ./my-custom-dsx-folder/ \      # Change input folder
      --output ./documentation/ \             # Change output folder
      --workers 4
```

### **Control when it runs:**

```yaml
# Run only on specific branches
on:
  push:
    branches: [ main, production ]

# Run on any .dsx file change
on:
  push:
    paths:
      - '**/*.dsx'

# Run manually
on:
  workflow_dispatch:
```

### **Adjust processing speed:**

```yaml
# Use more workers for faster processing (but watch API rate limits!)
--workers 8

# Use fewer workers to avoid rate limits
--workers 1
```

---

## 🎯 Example Workflow

### **Day 1: Setup**
```powershell
# 1. Create folders
mkdir dsx_files_input
mkdir dsx_docs_output  # Optional - will be auto-created

# 2. Add GitHub Actions workflow (already done!)
# 3. Add API key secret on GitHub (Settings → Secrets)
# 4. Push to GitHub
git add .
git commit -m "Setup auto-documentation"
git push
```

### **Day 2+: Normal Usage**
```powershell
# Export a job from DataStage
# Copy it to dsx_files_input/
cp "C:\exports\MyJob.dsx" ./dsx_files_input/

# Commit and push
git add dsx_files_input/MyJob.dsx
git commit -m "Add MyJob"
git push

# Wait 2-3 minutes...
# Pull to get the generated docs
git pull

# View the documentation
code ./dsx_docs_output/MyJob__MyJob.md
```

---

## 🔍 Monitoring

### **Check if it's working:**

1. **GitHub Actions tab** - See if workflow ran successfully
2. **docs/ folder** - See if new .md files appeared
3. **results.json** - Check success/failure counts
4. **Workflow logs** - See detailed output

### **Troubleshooting:**

| Problem | Solution |
|---------|----------|
| Workflow doesn't run | Check if .dsx file is in `dsx_files_input/` folder |
| "Missing API key" error | Add `DSX_API_KEY` secret on GitHub |
| Docs not generated | Check workflow logs for errors |
| Rate limit errors | Reduce `--workers` to 1 |

---

## 📈 Advanced: Schedule Nightly Regeneration

Want to regenerate all docs every night? Add this to the workflow:

```yaml
on:
  push:
    paths:
      - 'dsx_files_input/**/*.dsx'
  schedule:
    - cron: '0 2 * * *'  # Run at 2 AM every day
```

This ensures docs stay fresh even if the tool improves!

---

## 🎉 Summary

**What you have now:**
- ✅ Push .dsx files to `dsx_files_input/` folder
- ✅ GitHub automatically generates docs
- ✅ Docs appear in `dsx_docs_output/` folder
- ✅ Everything version-controlled
- ✅ No manual work needed!

**Next steps:**
1. Add `DSX_API_KEY` as a GitHub secret
2. Push some .dsx files to test
3. Watch it work! 🚀

Need help? Check the workflow logs in the Actions tab! 📊
