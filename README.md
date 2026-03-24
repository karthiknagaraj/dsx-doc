# DSX Documentation Assistant

Parse IBM DataStage .dsx exports and generate human-readable documentation using AI, with both an interactive UI and CI/CD automation support.

## Run Locally In 3 Steps

1. Install dependencies

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Configure API key

```powershell
Copy-Item .env.example .env
# Edit .env and set DSX_API_KEY
```

3. Start the app

```powershell
python -m streamlit run .\frontend.py
```

Open http://localhost:8501.

## Fast Navigation

- Full project overview: [COMPREHENSIVE_README.md](COMPREHENSIVE_README.md)
- Documentation index: [docs/README.md](docs/README.md)
- Quick navigation guide: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

## Documentation Hub

### Core Guides
- [Architecture](docs/ARCHITECTURE.md)
- [Installation](docs/INSTALLATION.md)
- [Usage](docs/USAGE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Contributing](docs/CONTRIBUTING.md)

### GitHub and CI/CD
- [GitHub Setup](docs/GITHUB_SETUP.md)
- [GitHub Automation Setup](GITHUB_AUTOMATION_SETUP.md)
- [CI/CD Integration](CI_CD_INTEGRATION.md)
- [GitHub Publishing Checklist](GITHUB_PUBLISHING_CHECKLIST.md)

### Additional Context
- [Documentation Summary](DOCUMENTATION_SUMMARY.md)
- [Project Analysis Complete](PROJECT_ANALYSIS_COMPLETE.md)
- [Business Requirements Context](_datastage_doc_assistant_req.md)

## Code Layout

- App entry point: [frontend.py](frontend.py)
- CLI automation: [dsx_docs_cli.py](dsx_docs_cli.py)
- Doc generation: [doc_generator.py](doc_generator.py)
- DSX parsing: [dsx_to_canonical.py](dsx_to_canonical.py)
- Semantic search: [embeddings.py](embeddings.py)
- Streamlit tabs: [tab_documentation.py](tab_documentation.py), [tab_semantic_search.py](tab_semantic_search.py)
- Utilities: [utils.py](utils.py)
- Tests: [tests/test_doc_format.py](tests/test_doc_format.py)
- Sample inputs: [dsx_files_input/](dsx_files_input/)
- Workflow: [.github/workflows/generate-docs.yml](.github/workflows/generate-docs.yml)

## Typical Workflows

### Interactive mode
1. Upload DSX files in the Documentation tab.
2. Generate Markdown documentation for a selected job.
3. Use Semantic Search to ask natural-language questions.

### Automation mode
1. Place DSX files in [dsx_files_input/](dsx_files_input/).
2. Run CLI to generate docs in CI/CD.
3. Use GitHub Actions workflow for continuous updates.

## Repository Purpose

This repository now contains both:

- Full runnable codebase
- Full documentation set with cross-linked guides
