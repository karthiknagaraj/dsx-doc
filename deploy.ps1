# Deployment Helper Script for Windows PowerShell
# This script helps you prepare and test your deployment

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('test-local', 'docker-build', 'docker-run', 'check-secrets', 'help')]
    [string]$Action = 'help'
)

function Show-Help {
    Write-Host "DSX Documentation Assistant - Deployment Helper"
    Write-Host "================================================"
    Write-Host ""
    Write-Host "Usage: .\deploy.ps1 -Action <action>"
    Write-Host ""
    Write-Host "Actions:"
    Write-Host "  test-local      Test the app locally with Streamlit"
    Write-Host "  docker-build    Build the Docker image"
    Write-Host "  docker-run      Run the Docker container"
    Write-Host "  check-secrets   Check for accidentally committed secrets"
    Write-Host "  help            Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\deploy.ps1 -Action test-local"
    Write-Host "  .\deploy.ps1 -Action docker-build"
    Write-Host "  .\deploy.ps1 -Action docker-run"
    Write-Host ""
    Write-Host "For full deployment guides, see DEPLOYMENT.md"
}

function Test-Local {
    Write-Host "Testing local Streamlit app..." -ForegroundColor Cyan
    
    # Check if Python is installed
    $pythonCheck = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCheck) {
        $pythonVersion = python --version 2>&1
        Write-Host "OK Python found: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "ERROR Python not found. Please install Python 3.8+" -ForegroundColor Red
        return
    }
    
    # Start Streamlit
    Write-Host ""
    Write-Host "Starting Streamlit app..." -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
    streamlit run frontend.py
}

function Build-Docker {
    Write-Host "Building Docker image..." -ForegroundColor Cyan
    
    # Check if Docker is installed
    $dockerCheck = Get-Command docker -ErrorAction SilentlyContinue
    if ($dockerCheck) {
        $dockerVersion = docker --version 2>&1
        Write-Host "OK Docker found: $dockerVersion" -ForegroundColor Green
    } else {
        Write-Host "ERROR Docker not found. Please install Docker Desktop." -ForegroundColor Red
        return
    }
    
    # Build the image
    Write-Host ""
    Write-Host "Building image 'dsx-doc-assistant'..." -ForegroundColor Cyan
    docker build -t dsx-doc-assistant .
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK Docker image built successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "To run the container, use:" -ForegroundColor Cyan
        Write-Host "  .\deploy.ps1 -Action docker-run" -ForegroundColor White
    } else {
        Write-Host "ERROR Docker build failed." -ForegroundColor Red
    }
}

function Run-Docker {
    Write-Host "Running Docker container..." -ForegroundColor Cyan
    
    # Check if image exists
    $imageExists = docker images -q dsx-doc-assistant 2>$null
    if (-not $imageExists) {
        Write-Host "ERROR Image 'dsx-doc-assistant' not found." -ForegroundColor Red
        Write-Host "  Run: .\deploy.ps1 -Action docker-build" -ForegroundColor Yellow
        return
    }
    
    # Check for .env file
    if (Test-Path ".env") {
        Write-Host "OK Using .env file for environment variables" -ForegroundColor Green
        Write-Host ""
        Write-Host "Starting container with docker-compose..." -ForegroundColor Cyan
        docker-compose up
    } else {
        Write-Host "WARNING No .env file found. Starting without API key..." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Starting container..." -ForegroundColor Cyan
        docker run -p 8501:8501 dsx-doc-assistant
    }
}

function Check-Secrets {
    Write-Host "Checking for accidentally committed secrets..." -ForegroundColor Cyan
    
    # Check .gitignore
    if (Test-Path ".gitignore") {
        $gitignoreContent = Get-Content ".gitignore" -Raw
        $requiredEntries = @('.env', '*.sqlite', '.streamlit/secrets.toml')
        
        Write-Host ""
        Write-Host "Checking .gitignore..." -ForegroundColor Cyan
        foreach ($entry in $requiredEntries) {
            if ($gitignoreContent -match [regex]::Escape($entry)) {
                Write-Host "OK .gitignore contains: $entry" -ForegroundColor Green
            } else {
                Write-Host "MISSING .gitignore should contain: $entry" -ForegroundColor Red
            }
        }
    }
    
    Write-Host ""
    Write-Host "OK Pre-deployment check complete" -ForegroundColor Green
}

# Main execution
switch ($Action) {
    'test-local' { Test-Local }
    'docker-build' { Build-Docker }
    'docker-run' { Run-Docker }
    'check-secrets' { Check-Secrets }
    'help' { Show-Help }
    default { Show-Help }
}
