# DSX Documentation Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Automatically parse IBM DataStage `.dsx` export files and generate comprehensive, AI-powered documentation. Includes interactive Streamlit UI, command-line CLI, and GitHub Actions integration.

---

## 🎯 What It Does

### The Problem
- DataStage jobs are documented informally (or not at all)
- Documentation gets out of sync with actual pipeline changes
- Knowledge transfer takes weeks
- Non-technical stakeholders can't understand data flows
- Impact analysis requires manual investigation

### The Solution
This tool **automatically generates** professional documentation from DataStage job exports:

✅ Parse DSX files in seconds  
✅ Extract job structure, stages, links, parameters  
✅ Generate human-readable Markdown documentation  
✅ Perform semantic search on documentation  
✅ Automate via GitHub Actions CI/CD  
✅ Deploy as Streamlit app or CLI tool  

**Time saved:** 4-6 hours per job → 15-30 minutes automated

---

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Python 3.9+
- API key for LLM (free tier available)
- Your DataStage DSX files

### 1. Install
```powershell
# Clone repository
git clone https://github.com/YOUR-USERNAME/dsx-doc-assistant.git
cd dsx-doc-assistant

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up API Key
```powershell
# Create .env file
cp .env.example .env

# Edit .env - add your OpenRouter API key
# DSX_API_KEY=sk-...
```

Get free API key: [OpenRouter.ai](https://openrouter.io) (includes free credits)

### 3. Run Interactive UI
```powershell
streamlit run frontend.py
```

Browser opens at http://localhost:8501

### 4. Generate Documentation
1. Upload `.dsx` files
2. Click "Ingest to Database"
3. Select job and generate documentation
4. Download or search over your docs

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [INSTALLATION.md](docs/INSTALLATION.md) | Detailed setup for different environments |
| [USAGE.md](docs/USAGE.md) | How to use UI and CLI |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design and components |
| [API_REFERENCE.md](docs/API_REFERENCE.md) | Python module and API documentation |
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | Production deployment (Docker, Cloud, K8s) |
| [CONTRIBUTING.md](docs/CONTRIBUTING.md) | How to contribute code |
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common issues and solutions |
| [GITHUB_SETUP.md](docs/GITHUB_SETUP.md) | Create GitHub repo and set up CI/CD |

---

## 💡 Features

### Interactive UI (Streamlit)
- 📝 **Documentation Tab**: Upload DSX files, ingest metadata, generate docs
- 🔎 **Semantic Search Tab**: Ask natural language questions over docs
- 🗃️ **Database Browser**: Explore extracted jobs, stages, parameters
- 💾 **Persistent Database**: SQLite for local storage

### Command-Line Interface
- Batch processing of directories
- Parallel execution (`--workers N`)
- JSON output for CI/CD integration
- Exit codes for pipeline automation
- Change detection to skip unchanged files

### CI/CD Integration
- 🤖 GitHub Actions workflow included
- Auto-generates docs on push
- Commits results back to repo
- Works with any CI/CD platform

### Documentation Quality
- Structured Markdown format
- Job overview and business context
- Input sources and output targets
- Stage-by-stage transformations
- Column-level lineage
- Parameter documentation
- Performance notes and glossary

---

## 🔧 Use Cases

### Data Engineering Teams
Document all ETL/ELT pipelines automatically as they evolve

### Business Analysts
Understanding data flows without asking engineers for documents

### Compliance & Governance
Maintain audit trail of pipeline changes and documentation

### Onboarding New Team Members
Instantly access contextual documentation for any job

### Impact Analysis
Understand which jobs and columns are affected by changes

---

## 📊 Example Output

```markdown
# Customer Master Update (DSX file: CustMaster.dsx)

## Overview
Updates the customer master dimension with new/changed customer data
from multiple source systems, applies validation rules, and loads
to the enterprise data warehouse.

## Inputs (Sources)
| Source | Type | Records | Notes |
|--------|------|---------|-------|
| SAP ERP | DB2 Stage | 50K/day | New/changed customer records |
| Legacy CRM | Oracle | 30K/day | Historical customer data |

## Data Flow
SAP → Deduplication → Join with Legacy → Validation → Filters → DW

## Transformations
- **Deduplication**: Remove duplicate records from same source
- **JoinWithLegacy**: Enrich SAP data with legacy system info
- **Validation**: Check mandatory fields and data quality rules
- **FilterInvalid**: Remove records failing quality checks

## Output Targets
- **CustomerDim**: Main customer dimension table (80K records)

## Parameters
- P_StartDate: Batch start date
- P_Threshold: Quality score threshold (default: 0.95)

## Column Lineage
SapCustomerId → CustomerId  
SapName + LegacyName → CustomerFullName  
SapActiveFlag → IsActive
```

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Parsing** | Python XML | Parse DataStage DSX files |
| **Database** | SQLite | Store metadata and documentation |
| **LLM** | OpenRouter API | Generate natural language docs |
| **UI** | Streamlit | Interactive web interface |
| **Search** | Vector embeddings | Semantic/similarity search |
| **Deployment** | Docker/Docker Compose | Containerization |
| **CI/CD** | GitHub Actions | Automation |

---

## 🚀 Deployment Options

### Lightweight: Local/Development
```powershell
# Run directly
streamlit run frontend.py
```

### Recommended: Docker
```powershell
# One-liner
docker-compose up -d
```

### Production: Cloud
- **Azure**: App Service, Container Instances, AKS
- **AWS**: ECS, Lambda (async), App Runner
- **GCP**: Cloud Run, App Engine
- **Kubernetes**: Full K8s manifests included

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for:

- Setting up development environment
- Running tests
- Code style guidelines
- Pull request process
- Areas needing help

**Quick contributes:**
- 📝 Improve documentation
- 🐛 Report and fix bugs
- ✨ Add features
- 🧪 Add tests
- 📚 Write examples

---

## ⚙️ Configuration

### Environment Variables

```env
# Required
DSX_API_KEY=sk-your-api-key-here

# Optional (with defaults)
DSX_CHAT_MODEL=openai/gpt-oss-120b          # LLM model
DSX_CHAT_BASE_URL=https://openrouter.ai/api/v1  # API endpoint
DSX_CHAT_TIMEOUT_SEC=180                    # Request timeout
DSX_CHAT_MAX_RETRIES=3                      # Retry attempts
DSX_DOCS_MAX_WORKERS=1                      # Batch processing
```

Copy `.env.example` and edit:
```powershell
cp .env.example .env
# Edit .env with your values
```

---

## 📈 Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Parse DSX | < 5s | Single file |
| Generate docs | 15-30s | Per job, depends on size |
| Ingest to DB | < 2s | Parse + store |
| Semantic search | < 1s | Query time |
| Batch processing | Linear | With `--workers 4`: ~4x faster |

---

## 🔒 Security

✅ API keys stored in environment variables (never in code)  
✅ SQLite database local-only (no remote exposure)  
✅ GitHub Secrets for CI/CD  
✅ `.env` in `.gitignore` (never committed)  
✅ Input validation on all DSX files  

⚠️ For sensitive environments:
- Use VPC/network isolation
- Restrict database access
- Audit API key usage
- Implement RBAC for shared deployments

---

## 🐛 Troubleshooting

Common issues and solutions are in [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md):

- API key errors
- Docker issues
- Database problems
- Performance optimization
- And more...

Quick help:
```powershell
# Check setup
python -c "from doc_generator import load_chat_config; cfg = load_chat_config(); print('✓ Config OK')"

# Test API
curl -H "Authorization: Bearer $env:DSX_API_KEY" https://openrouter.ai/api/v1/models

# View logs
streamlit run frontend.py  # Terminal shows debug info
```

---

## 📋 Requirements

### Minimum
- Python 3.9+
- 4GB RAM
- 500MB disk
- Internet connection

### Recommended
- Python 3.11
- 8GB+ RAM
- 2GB disk
- Good bandwidth

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/) - Web framework
- [OpenRouter](https://openrouter.io/) - LLM API
- [Python](https://www.python.org/) - Programming language
- [Docker](https://www.docker.com/) - Containerization

---

## 📞 Support

- **Documentation**: Start with [README](docs/), especially [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- **GitHub Issues**: Report bugs or request features
- **GitHub Discussions**: Ask questions and share ideas
- **Examples**: Check `dsx_files_input/` for sample DSX files

---

## 🎬 Getting Started

1. **First time?** → [INSTALLATION.md](docs/INSTALLATION.md)
2. **Want to use it?** → [USAGE.md](docs/USAGE.md)
3. **Need to deploy?** → [DEPLOYMENT.md](docs/DEPLOYMENT.md)
4. **Want to code?** → [CONTRIBUTING.md](docs/CONTRIBUTING.md)
5. **Something broken?** → [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
6. **Setting up GitHub?** → [GITHUB_SETUP.md](docs/GITHUB_SETUP.md)

---

## 📚 Project Status

**Current Version**: 1.0.0  
**Status**: Active Development  
**Python Support**: 3.9, 3.10, 3.11, 3.12

### What's Next
- [ ] Support for additional DSX elements
- [ ] Export to HTML/PDF formats
- [ ] Enhanced data lineage visualization
- [ ] Integration with Databricks, Snowflake
- [ ] Web-based document management
- [ ] Team collaboration features

---

## 💬 Example Commands

```powershell
# Interactive UI
streamlit run frontend.py

# Generate docs for single file
python dsx_docs_cli.py --input job.dsx --output ./docs/

# Batch with parallelization
python dsx_docs_cli.py --input ./dsx_files/ --output ./docs/ --workers 4

# With JSON output (CI/CD)
python dsx_docs_cli.py --input ./dsx_files/ --output ./docs/ \
  --json-output results.json --fail-on-error

# Docker
docker-compose up -d
# Opens at http://localhost:8501
```

---

**Made with ❤️ for DataStage teams everywhere**

