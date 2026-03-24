# CI/CD Pipeline Integration Guide

This guide shows how to integrate the DSX Documentation Generator into various CI/CD platforms.

---

## Table of Contents

1. [GitHub Actions](#github-actions)
2. [GitLab CI](#gitlab-ci)
3. [Jenkins](#jenkins)
4. [Azure DevOps](#azure-devops)
5. [Generic Script](#generic-script)

---

## Quick Start

### Prerequisites

1. **API Key**: Set up your OpenRouter (or other LLM provider) API key as a secret
2. **Python 3.8+**: Ensure Python is available in your CI environment
3. **DSX Files**: Store your `.dsx` files in a specific directory (e.g., `dsx_files/`)

### Basic Workflow

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the CLI tool
python dsx_docs_cli.py --input ./dsx_files/ --output ./docs/ \
    --json-output results.json --fail-on-error

# 3. The pipeline will:
#    - Generate markdown docs for all .dsx files
#    - Save them to ./docs/
#    - Exit with code 0 (success) or non-zero (failure)
```

---

## GitHub Actions

Create `.github/workflows/generate-dsx-docs.yml`:

```yaml
name: Generate DSX Documentation

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'dsx_files/**/*.dsx'  # Trigger only when .dsx files change
  pull_request:
    branches: [ main ]
  workflow_dispatch:  # Allow manual trigger

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
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
        DSX_CHAT_MODEL: ${{ vars.DSX_CHAT_MODEL || 'openai/gpt-oss-120b' }}
      run: |
        python dsx_docs_cli.py \
          --input ./dsx_files/ \
          --output ./docs/ \
          --workers 4 \
          --skip-unchanged \
          --json-output results.json \
          --fail-on-error
    
    - name: Upload documentation artifacts
      uses: actions/upload-artifact@v3
      with:
        name: dsx-documentation
        path: docs/
    
    - name: Upload results JSON
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: generation-results
        path: results.json
    
    - name: Commit and push docs (optional)
      if: github.event_name == 'push'
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add docs/
        git diff --quiet && git diff --staged --quiet || git commit -m "Auto-generate DSX documentation [skip ci]"
        git push
```

### Setup GitHub Secrets

1. Go to your repository → Settings → Secrets and variables → Actions
2. Add secret: `DSX_API_KEY` with your OpenRouter API key
3. (Optional) Add variable: `DSX_CHAT_MODEL` to customize the model

---

## GitLab CI

Create `.gitlab-ci.yml`:

```yaml
stages:
  - generate-docs
  - deploy

variables:
  DSX_INPUT_DIR: "dsx_files"
  DSX_OUTPUT_DIR: "docs"
  DSX_WORKERS: "4"

generate-dsx-docs:
  stage: generate-docs
  image: python:3.11-slim
  
  before_script:
    - pip install -r requirements.txt
  
  script:
    - |
      python dsx_docs_cli.py \
        --input ./${DSX_INPUT_DIR}/ \
        --output ./${DSX_OUTPUT_DIR}/ \
        --workers ${DSX_WORKERS} \
        --skip-unchanged \
        --json-output results.json \
        --fail-on-error
  
  artifacts:
    paths:
      - docs/
      - results.json
    expire_in: 30 days
    reports:
      dotenv: results.json  # Makes results available to other jobs
  
  only:
    changes:
      - dsx_files/**/*.dsx
      - dsx_docs_cli.py
      - doc_generator.py
  
  # Use GitLab CI/CD variables for API key
  # Set DSX_API_KEY in: Settings → CI/CD → Variables

deploy-docs:
  stage: deploy
  script:
    - echo "Deploy documentation to your documentation site"
    # Add deployment commands here (e.g., push to S3, GitHub Pages, etc.)
  dependencies:
    - generate-dsx-docs
  only:
    - main
```

### Setup GitLab Variables

1. Go to your project → Settings → CI/CD → Variables
2. Add variable: `DSX_API_KEY` with your API key (mark as "Masked" and "Protected")

---

## Jenkins

Create `Jenkinsfile`:

```groovy
pipeline {
    agent any
    
    environment {
        DSX_API_KEY = credentials('dsx-api-key')  // Reference Jenkins credential
        DSX_CHAT_MODEL = 'openai/gpt-oss-120b'
        DSX_INPUT_DIR = 'dsx_files'
        DSX_OUTPUT_DIR = 'docs'
    }
    
    stages {
        stage('Setup') {
            steps {
                sh '''
                    python3 -m pip install --upgrade pip
                    pip3 install -r requirements.txt
                '''
            }
        }
        
        stage('Generate Documentation') {
            steps {
                sh '''
                    python3 dsx_docs_cli.py \
                        --input ./${DSX_INPUT_DIR}/ \
                        --output ./${DSX_OUTPUT_DIR}/ \
                        --workers 4 \
                        --skip-unchanged \
                        --json-output results.json \
                        --fail-on-error
                '''
            }
        }
        
        stage('Archive Results') {
            steps {
                archiveArtifacts artifacts: 'docs/**/*.md', allowEmptyArchive: false
                archiveArtifacts artifacts: 'results.json', allowEmptyArchive: false
            }
        }
        
        stage('Parse Results') {
            steps {
                script {
                    def results = readJSON file: 'results.json'
                    echo "Generated ${results.success} docs successfully"
                    echo "Failed: ${results.failed}"
                    echo "Total tokens: ${results.total_tokens}"
                }
            }
        }
    }
    
    post {
        success {
            echo 'Documentation generated successfully!'
        }
        failure {
            echo 'Documentation generation failed!'
        }
        always {
            cleanWs()  // Clean workspace
        }
    }
}
```

### Setup Jenkins Credentials

1. Go to Jenkins → Manage Jenkins → Credentials
2. Add credential: Type "Secret text", ID `dsx-api-key`, Secret = your API key

---

## Azure DevOps

Create `azure-pipelines.yml`:

```yaml
trigger:
  branches:
    include:
      - main
      - develop
  paths:
    include:
      - dsx_files/**/*.dsx

pool:
  vmImage: 'ubuntu-latest'

variables:
  dsxInputDir: 'dsx_files'
  dsxOutputDir: 'docs'
  dsxWorkers: 4

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.11'
    addToPath: true

- script: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
  displayName: 'Install dependencies'

- script: |
    python dsx_docs_cli.py \
      --input ./$(dsxInputDir)/ \
      --output ./$(dsxOutputDir)/ \
      --workers $(dsxWorkers) \
      --skip-unchanged \
      --json-output results.json \
      --fail-on-error
  displayName: 'Generate DSX documentation'
  env:
    DSX_API_KEY: $(DSX_API_KEY)  # Reference Azure DevOps variable

- task: PublishBuildArtifacts@1
  inputs:
    pathToPublish: '$(dsxOutputDir)'
    artifactName: 'dsx-documentation'
  displayName: 'Publish documentation artifacts'

- task: PublishBuildArtifacts@1
  inputs:
    pathToPublish: 'results.json'
    artifactName: 'generation-results'
  condition: always()
  displayName: 'Publish results JSON'
```

### Setup Azure DevOps Variables

1. Go to Pipelines → Edit pipeline → Variables
2. Add variable: `DSX_API_KEY` with your API key (mark as "Secret")

---

## Generic Script (Any CI/CD)

If your CI/CD platform isn't listed above, use this generic shell script:

```bash
#!/bin/bash
# generate_dsx_docs.sh

set -e  # Exit on error

# Configuration
INPUT_DIR="${DSX_INPUT_DIR:-dsx_files}"
OUTPUT_DIR="${DSX_OUTPUT_DIR:-docs}"
WORKERS="${DSX_WORKERS:-4}"
JSON_OUTPUT="${DSX_JSON_OUTPUT:-results.json}"

# Check prerequisites
if [ -z "$DSX_API_KEY" ]; then
    echo "ERROR: DSX_API_KEY environment variable is not set"
    exit 3
fi

if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 is not installed"
    exit 3
fi

# Install dependencies
echo "Installing dependencies..."
python3 -m pip install --upgrade pip --quiet
pip3 install -r requirements.txt --quiet

# Generate documentation
echo "Generating documentation..."
python3 dsx_docs_cli.py \
    --input "./${INPUT_DIR}/" \
    --output "./${OUTPUT_DIR}/" \
    --workers "${WORKERS}" \
    --skip-unchanged \
    --json-output "${JSON_OUTPUT}" \
    --fail-on-error

# Parse results
if [ -f "${JSON_OUTPUT}" ]; then
    SUCCESS=$(python3 -c "import json; print(json.load(open('${JSON_OUTPUT}'))['success'])")
    FAILED=$(python3 -c "import json; print(json.load(open('${JSON_OUTPUT}'))['failed'])")
    TOKENS=$(python3 -c "import json; print(json.load(open('${JSON_OUTPUT}'))['total_tokens'])")
    
    echo "================================"
    echo "Documentation Generation Summary"
    echo "================================"
    echo "Success: ${SUCCESS}"
    echo "Failed:  ${FAILED}"
    echo "Tokens:  ${TOKENS}"
    echo "================================"
fi

echo "Done!"
```

**Make it executable:**
```bash
chmod +x generate_dsx_docs.sh
```

**Run it:**
```bash
export DSX_API_KEY="your-key-here"
./generate_dsx_docs.sh
```

---

## Advanced: Pre-commit Hook

Want to generate docs automatically before committing? Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Pre-commit hook to generate DSX documentation

# Check if any .dsx files changed
DSX_CHANGED=$(git diff --cached --name-only --diff-filter=ACM | grep '\.dsx$' || true)

if [ -n "$DSX_CHANGED" ]; then
    echo "DSX files changed. Generating documentation..."
    
    # Generate docs (non-blocking)
    python3 dsx_docs_cli.py \
        --input ./dsx_files/ \
        --output ./docs/ \
        --skip-unchanged \
        --workers 1 || echo "Warning: Doc generation failed"
    
    # Stage generated docs
    git add docs/
    
    echo "Documentation generated and staged."
fi
```

---

## Best Practices

### 1. **Cache Dependencies**
Speed up CI runs by caching Python packages:

**GitHub Actions:**
```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
```

### 2. **Run Only on Changes**
Only trigger when .dsx files change:

```yaml
on:
  push:
    paths:
      - 'dsx_files/**/*.dsx'
```

### 3. **Parallel Processing**
Use `--workers` flag for faster batch processing:

```bash
python dsx_docs_cli.py --input ./dsx_files/ --output ./docs/ --workers 4
```

### 4. **Skip Unchanged Files**
Use `--skip-unchanged` to avoid regenerating docs for unchanged files:

```bash
python dsx_docs_cli.py --input ./dsx_files/ --output ./docs/ --skip-unchanged
```

### 5. **Monitor Token Usage**
Parse `results.json` to track API costs:

```bash
TOKENS=$(cat results.json | jq '.total_tokens')
echo "Total tokens used: $TOKENS"
```

---

## Troubleshooting

### Issue: "Missing API key"
**Solution:** Ensure `DSX_API_KEY` is set as a secret/variable in your CI/CD platform

### Issue: "Rate limit exceeded"
**Solution:** Reduce `--workers` or add delays between API calls

### Issue: "Timeout errors"
**Solution:** Increase `--timeout` value (default: 180 seconds)

### Issue: "Pipeline fails but some docs generated"
**Solution:** Remove `--fail-on-error` flag to allow partial success

---

## Next Steps

1. Choose your CI/CD platform above
2. Copy the example configuration
3. Add your API key as a secret
4. Test with a small batch of .dsx files
5. Scale up once working

Need help? Check the main README.md or open an issue!
