# Troubleshooting Guide

## Common Issues and Solutions

---

## Installation & Setup Issues

### Issue: `ModuleNotFoundError: No module named 'streamlit'`

**Cause**: Dependencies not installed or wrong environment

**Solutions**:
1. Verify virtual environment is active:
   ```powershell
   # Should show path with 'venv' in it
   (Get-Command python).Source
   ```

2. Reinstall dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Check requirements file:
   ```powershell
   cat requirements.txt
   pip install streamlit python-dotenv requests urllib3 jsonschema
   ```

---

### Issue: `'python' is not recognized as an internal or external command`

**Cause**: Python not in PATH

**Solutions**:
1. Verify Python installation:
   ```powershell
   python --version
   ```

2. If command not found, reinstall Python:
   - Check "Add Python to PATH" during installation
   - Restart terminal after reinstalling

3. Use full path if needed:
   ```powershell
   C:\Users\karthik.nagaraj\AppData\Local\Programs\Python\Python311\python --version
   ```

---

### Issue: `.env` file not loading

**Cause**: .env file not in correct location or not readable

**Solutions**:
1. Verify file exists:
   ```powershell
   Test-Path .\.env
   cat .env
   ```

2. Ensure file is named `.env` (not `.env.txt` or `.env.example`)

3. Check file contents:
   ```powershell
   # Should show
   DSX_API_KEY=sk-...
   DSX_CHAT_MODEL=openai/gpt-oss-120b
   ```

4. Reload environment by restarting shell:
   ```powershell
   # Exit and reopen PowerShell
   exit
   ```

---

## API & Authentication Issues

### Issue: `ValueError: Missing API key. Set DSX_API_KEY in your .env file`

**Cause**: API key not configured

**Solutions**:
1. Add to `.env`:
   ```env
   DSX_API_KEY=sk-your-actual-key-here
   ```

2. Check environment variable is set:
   ```powershell
   $env:DSX_API_KEY
   # Should show your key, not empty
   ```

3. For Docker/CI:
   ```powershell
   docker run -e DSX_API_KEY="sk-..." dsx-doc-assistant:latest
   ```

4. Get API key:
   - OpenRouter: https://openrouter.ai/keys
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/

---

### Issue: `401 Unauthorized` or `Invalid API key`

**Cause**: API key wrong, expired, or has no credits

**Solutions**:
1. Verify API key is correct:
   ```powershell
   echo $env:DSX_API_KEY
   # Copy and compare with key in your provider dashboard
   ```

2. Check account status:
   - OpenRouter: https://openrouter.ai/account/billing/overview
   - OpenAI: https://platform.openai.com/account/billing/overview
   - Anthropic: https://console.anthropic.com/

3. Generate new key:
   - Revoke old key in provider dashboard
   - Create new key
   - Update `.env`

4. Test key with curl:
   ```powershell
   $key = $env:DSX_API_KEY
   
   curl -X POST https://openrouter.ai/api/v1/models `
     -H "Authorization: Bearer $key" `
     -H "Content-Type: application/json"
   ```

---

### Issue: `429 Too Many Requests` or Rate Limited

**Cause**: Too many API requests too quickly

**Solutions**:
1. Increase retry delay:
   ```env
   DSX_CHAT_TIMEOUT_SEC=300
   DSX_CHAT_MAX_RETRIES=5
   ```

2. Reduce concurrent processing:
   ```powershell
   # Use --workers 1 instead of --workers 4
   python dsx_docs_cli.py --input ./dsx_files/ --output ./docs/ --workers 1
   ```

3. Wait and retry:
   ```powershell
   Start-Sleep -Seconds 60
   python dsx_docs_cli.py --input ./dsx_files/ --output ./docs/
   ```

4. Check API limits:
   - OpenRouter: https://openrouter.ai/account
   - OpenAI: https://platform.openai.com/account/rate-limits

---

## Application Runtime Issues

### Issue: Streamlit app won't start

**Cause**: Port already in use, config error, or dependency issue

**Solutions**:
1. Check if port 8501 is in use:
   ```powershell
   Get-Process | Where-Object {$_.Name -like "*python*"}
   netstat -ano | findstr :8501
   ```

2. Kill existing process:
   ```powershell
   Stop-Process -Name "pythonw" -Force
   ```

3. Use different port:
   ```powershell
   streamlit run frontend.py --server.port 8502
   ```

4. Clear Streamlit cache:
   ```powershell
   rm -r ~/.streamlit/
   streamlit run frontend.py
   ```

---

### Issue: `FileNotFoundError: dsx_graph_all.sqlite not found`

**Cause**: Database not initialized yet

**Solutions**:
1. This is normal on first run - database will be created automatically when you:
   - Upload a DSX file
   - Click "Ingest to Database"

2. To manually create empty database:
   ```powershell
   python -c "
   import sqlite3
   conn = sqlite3.connect('dsx_graph_all.sqlite')
   conn.close()
   echo 'Database created'
   "
   ```

3. Check database exists:
   ```powershell
   Test-Path .\dsx_graph_all.sqlite
   ```

---

### Issue: DSX file upload fails

**Cause**: Invalid file format or large file

**Solutions**:
1. Verify file is valid DSX:
   ```powershell
   # DSX files are XML
   file myfile.dsx
   # Should show: ASCII text
   ```

2. Check file size:
   ```powershell
   (Get-Item myfile.dsx).Length / 1MB
   # If > 50MB, might be too large
   ```

3. Test with sample file:
   ```powershell
   # Download sample from dsx_files_input/
   ```

4. Check XML validity:
   ```powershell
   python -c "
   import xml.etree.ElementTree as ET
   try:
       tree = ET.parse('myfile.dsx')
       print('✓ Valid XML')
   except ET.ParseError as e:
       print(f'✗ Invalid XML: {e}')
   "
   ```

---

### Issue: `UnicodeDecodeError` when parsing DSX

**Cause**: File encoding issue

**Solutions**:
1. Convert file encoding:
   ```powershell
   # Using Python
   python -c "
   with open('myfile.dsx', 'r', encoding='utf-8-sig') as f:
       content = f.read()
   with open('myfile_fixed.dsx', 'w', encoding='utf-8') as f:
       f.write(content)
   "
   ```

2. Use different encoding:
   - Try `utf-16` or `latin-1` if UTF-8 fails

---

## Docker Issues

### Issue: Docker command not found

**Cause**: Docker not installed or not in PATH

**Solutions**:
1. Install Docker Desktop:
   - https://www.docker.com/products/docker-desktop
   - Restart after installation

2. Check installation:
   ```powershell
   docker --version
   docker ps
   ```

---

### Issue: Container fails to start

**Cause**: API key not provided, port in use, or image issue

**Solutions**:
1. Check logs:
   ```powershell
   docker logs dsx-assistant
   ```

2. Verify API key passed:
   ```powershell
   docker run -e DSX_API_KEY="sk-..." dsx-doc-assistant:latest
   ```

3. Check port availability:
   ```powershell
   Get-NetTCPConnection -LocalPort 8501
   ```

4. Use different port:
   ```powershell
   docker run -p 9999:8501 dsx-doc-assistant:latest
   ```

---

### Issue: Container can't reach API

**Cause**: Network isolation or firewall

**Solutions**:
1. Test from inside container:
   ```powershell
   docker exec dsx-assistant curl https://openrouter.ai/api/v1/models
   ```

2. Check internet connectivity:
   ```powershell
   docker exec dsx-assistant ping google.com
   ```

3. Check DNS:
   ```powershell
   docker exec dsx-assistant nslookup openrouter.ai
   ```

4. Use host network (Linux only):
   ```bash
   docker run --network host dsx-doc-assistant:latest
   ```

---

## Database Issues

### Issue: Database locked error

**Cause**: Another process using database

**Solutions**:
1. Close all instances:
   ```powershell
   Get-Process | Where-Object {$_.Name -like "*python*"} | Stop-Process
   ```

2. Check for locks:
   ```powershell
   Get-Item dsx_graph_all.sqlite* | Format-Table FullName, Length
   ```

3. Reset database:
   - In Streamlit UI: Documentation → Reset Database
   - Via CLI:
     ```powershell
     rm dsx_graph_all.sqlite
     ```

---

### Issue: Corrupted database

**Cause**: Incomplete transaction or power loss

**Solutions**:
1. Validate database:
   ```powershell
   python -c "
   import sqlite3
   conn = sqlite3.connect('dsx_graph_all.sqlite')
   cursor = conn.cursor()
   cursor.execute('PRAGMA integrity_check;')
   result = cursor.fetchone()
   print(result if result[0] == 'ok' else result)
   conn.close()
   "
   ```

2. Backup and recreate:
   ```powershell
   cp dsx_graph_all.sqlite dsx_graph_all.sqlite.bak
   rm dsx_graph_all.sqlite
   # Re-ingest files
   ```

---

## Documentation Generation Issues

### Issue: Empty or missing documentation

**Cause**: Generation failed, or wrong model selected

**Solutions**:
1. Check model selection:
   ```env
   DSX_CHAT_MODEL=openai/gpt-oss-120b
   ```

2. Increase timeout:
   ```env
   DSX_CHAT_TIMEOUT_SEC=300
   ```

3. Check logs:
   ```powershell
   streamlit run frontend.py
   # Check terminal output for errors
   ```

4. Try with different model:
   ```env
   DSX_CHAT_MODEL=openai/gpt-3.5-turbo
   ```

---

### Issue: Generated docs are low quality

**Cause**: Using fast model, short timeout, or incomplete data

**Solutions**:
1. Use better model:
   ```env
   DSX_CHAT_MODEL=openai/gpt-4
   ```

2. Increase timeout and retries:
   ```env
   DSX_CHAT_TIMEOUT_SEC=300
   DSX_CHAT_MAX_RETRIES=5
   ```

3. Verify DSX file is complete:
   - Check it opens in DataStage Manager
   - Verify it contains job definitions

---

## Semantic Search Issues

### Issue: No search results found

**Cause**: Chunks not built or embeddings not generated

**Solutions**:
1. Build chunks first:
   - 🔎 Semantic Search Tab
   - Click "1) Build/update chunks"
   - Wait for completion ✓

2. Generate embeddings:
   - Click "2) Generate embeddings (API)"
   - Wait for completion ✓

3. Check database:
   ```powershell
   python -c "
   import sqlite3
   conn = sqlite3.connect('dsx_graph_all.sqlite')
   cursor = conn.cursor()
   cursor.execute('SELECT COUNT(*) FROM embeddings;')
   count = cursor.fetchone()[0]
   print(f'Embeddings in DB: {count}')
   conn.close()
   "
   ```

---

### Issue: Search results irrelevant

**Cause**: Poor query quality or bad embeddings

**Solutions**:
1. Use specific terminology:
   - ✓ "How are customer ID fields transformed?"
   - ✗ "Tell me about the job"

2. Regenerate embeddings:
   - Clear existing: Documentation Tab → Reset Database
   - Regenerate docs and embeddings

3. Try different search terms:
   - Use technical terms from job
   - Ask about specific transformations
   - Reference column or stage names

---

## Performance Issues

### Issue: Slow DSX file parsing

**Cause**: Large file or slow system

**Solutions**:
1. Check file size:
   ```powershell
   (Get-Item myfile.dsx).Length / 1MB
   ```

2. Split large file:
   - Export individual jobs from DataStage
   - Process one at a time

3. Increase timeout:
   ```env
   DSX_CHAT_TIMEOUT_SEC=300
   ```

---

### Issue: High memory usage

**Cause**: Large database or many embeddings

**Solutions**:
1. Check database size:
   ```powershell
   (Get-Item dsx_graph_all.sqlite).Length / 1MB
   ```

2. Archive old files:
   ```powershell
   # Reset database and re-ingest current files only
   rm dsx_graph_all.sqlite
   ```

3. Increase system memory:
   - Add RAM to computer
   - Increase Docker memory limit: `-m 2g`

---

## Getting Help

If issue not resolved:

1. **Check logs**:
   ```powershell
   # Application logs
   streamlit run frontend.py
   # See terminal output
   ```

2. **Test connectivity**:
   ```powershell
   curl https://openrouter.ai/api/v1/models \
     -H "Authorization: Bearer $env:DSX_API_KEY"
   ```

3. **Create GitHub Issue**:
   - Include error message
   - Show commands you ran
   - Share `.env` (without API key)
   - Attach DSX file if possible

4. **Check Documentation**:
   - [README.md](../README.md)
   - [INSTALLATION.md](INSTALLATION.md)
   - [USAGE.md](USAGE.md)

