# IBIS Deployment Guide

Complete guide to deploying IBIS in various environments.

## Table of Contents

1. [Local Development](#local-development)
2. [Linux Server (24/7 Operation)](#linux-server-24-7-operation)
3. [Docker Container](#docker-container)
4. [Cloud Deployment (AWS/GCP/Azure)](#cloud-deployment)
5. [Monitoring & Logging](#monitoring--logging)
6. [Troubleshooting](#troubleshooting)

---

## Local Development

### Prerequisites

- Python 3.8+
- KuCoin account with API keys
- Terminal/Command prompt

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/ibis-trader.git
cd ibis-trader

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cd ibis
cp keys.env.example keys.env
# Edit keys.env with your KuCoin API keys
cd ..
```

### Running Locally

```bash
# Paper trading mode (recommended for testing)
PAPER_TRADING=true python3 ibis_true_agent.py

# With debug output
DEBUG=true VERBOSE=true python3 ibis_true_agent.py

# Single scan test
python3 ibis_true_agent.py --scan-once
```

---

## Linux Server (24/7 Operation)

### Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- Python 3.8+
- systemd (most modern Linux distros)
- KuCoin API keys

### Installation

```bash
# SSH to server
ssh user@your-server.com

# Install Python and dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git

# Clone repository
cd /opt
sudo git clone https://github.com/yourusername/ibis-trader.git
sudo chown -R $USER:$USER ibis-trader
cd ibis-trader

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configure as Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/ibis.service
```

Paste this content:

```ini
[Unit]
Description=IBIS Autonomous Trading Agent
After=network.target

[Service]
Type=simple
User=trader
WorkingDirectory=/opt/ibis-trader
Environment="PATH=/opt/ibis-trader/venv/bin"
ExecStart=/opt/ibis-trader/venv/bin/python3 /opt/ibis-trader/ibis_true_agent.py
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Then:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable ibis

# Start service
sudo systemctl start ibis

# Check status
sudo systemctl status ibis

# View logs
sudo journalctl -u ibis -f  # Follow logs
sudo journalctl -u ibis --since "2 hours ago"  # View recent logs
```

### Using the Control Script

```bash
# Start with watchdog (auto-restart)
./start_ibis.sh watchdog

# Stop
./start_ibis.sh stop

# Check status
./start_ibis.sh status

# View logs
tail -f data/ibis_true.log
```

---

## Docker Container

### Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create data directory
RUN mkdir -p data

# Run agent
CMD ["python3", "ibis_true_agent.py"]
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  ibis:
    build: .
    container_name: ibis-trader
    environment:
      - PAPER_TRADING=false
      - DEBUG=false
    volumes:
      - ./data:/app/data
      - ./ibis/keys.env:/app/ibis/keys.env:ro
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Running with Docker

```bash
# Build image
docker build -t ibis-trader .

# Run container
docker run -d \
  --name ibis \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/ibis/keys.env:/app/ibis/keys.env:ro \
  ibis-trader

# Or with docker-compose
docker-compose up -d

# View logs
docker logs -f ibis
docker-compose logs -f ibis

# Stop
docker stop ibis
docker-compose down
```

---

## Cloud Deployment

### AWS EC2

```bash
# Launch EC2 instance (Ubuntu 20.04)
# Install from Linux Server section above
# Use security groups to restrict inbound access
# Use Elastic IP for stable address
```

### Google Cloud Run (Serverless)

```bash
# Note: Cloud Run has 15-minute timeout, suitable for batch jobs only
# For 24/7 operation, use Compute Engine (similar to EC2)
```

### Azure Virtual Machine

```bash
# Similar process to AWS EC2
# Use Azure Key Vault for API keys
# Consider Azure Container Registry for Docker images
```

### Environment Variables

For cloud deployment, set these environment variables:

```bash
PAPER_TRADING=false       # Use real trading
DEBUG=false               # Disable debug output
VERBOSE=false             # Disable verbose logging
KUCOIN_API_KEY=xxx        # Your KuCoin API key
KUCOIN_API_SECRET=xxx     # Your KuCoin API secret
KUCOIN_API_PASSPHRASE=xxx # Your KuCoin passphrase
```

**Security Note**: Use cloud provider's secret management (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault) instead of environment variables for production.

---

## Monitoring & Logging

### Log Files

```bash
# Real-time logs
tail -f data/ibis_true.log

# Last 100 lines
tail -100 data/ibis_true.log

# Search for errors
grep "ERROR\|CRITICAL" data/ibis_true.log

# Search for learning events
grep "Learning\|📚" data/ibis_true.log
```

### Health Check Script

```bash
# Check if IBIS is running
pgrep -f "ibis_true_agent.py"

# View current state
python3 -c "
from ibis.data_consolidation import load_state
import json
state = load_state()
print(f'Positions: {len(state[\"positions\"])}')
print(f'Portfolio: \${state[\"capital_awareness\"][\"total_assets\"]:.2f}')
print(f'Market Regime: {state[\"market_regime\"]}')
"

# Run diagnostic
python3 tests/diagnostics/check_system.py
```

### Performance Monitoring

```bash
# Monitor system resources
top  # CPU, memory
df -h  # Disk space
netstat -an | grep ESTABLISHED  # Network connections

# Monitor IBIS performance
python3 tests/diagnostics/check_performance.py
```

---

## Troubleshooting

### IBIS Won't Start

```bash
# Check Python installation
python3 --version

# Check dependencies
pip list | grep -E "requests|aiohttp|pandas"

# Check for errors
VERBOSE=true python3 ibis_true_agent.py
```

### API Connection Issues

```bash
# Verify API keys are set correctly
cat ibis/keys.env | grep -E "KUCOIN_"

# Test KuCoin connectivity
python3 -c "
from ibis.exchange.kucoin_client import get_kucoin_client
client = get_kucoin_client()
print('Connected!' if client else 'Failed')
"

# Check firewall/network
ping api.kucoin.com
curl -I https://api.kucoin.com
```

### Memory Issues

```bash
# Check memory usage
ps aux | grep ibis_true_agent

# Monitor in real-time
watch -n 5 'ps aux | grep ibis_true_agent | grep -v grep'

# If memory grows unbounded, there may be a leak
```

### State Corruption

```bash
# Backup current state
cp data/ibis_true_state.json data/ibis_true_state.json.backup

# Check state validity
python3 -c "
import json
with open('data/ibis_true_state.json') as f:
    state = json.load(f)
print('State valid!' if state else 'State invalid')
"

# Fix state (see QUICKREF.md)
```

---

## Maintenance Tasks

### Regular Backups

```bash
# Backup daily
0 0 * * * cp /opt/ibis-trader/data/ibis_true_state.json /backup/ibis_state_$(date +%Y%m%d).json
0 0 * * * cp /opt/ibis-trader/data/ibis_true_memory.json /backup/ibis_memory_$(date +%Y%m%d).json
```

### Update Dependencies

```bash
# Check for updates
pip list --outdated

# Update (with testing)
PAPER_TRADING=true python3 ibis_true_agent.py --scan-once
pip install --upgrade package-name
PAPER_TRADING=true python3 ibis_true_agent.py --scan-once
```

### Clean Old Logs

```bash
# Archive logs older than 30 days
find data -name "*.log" -mtime +30 -exec gzip {} \;

# Or use logrotate configuration
```

---

## Support

- 📖 Check README.md for general help
- 🔧 Review QUICKREF.md for operations
- 👨‍💻 See DEVELOPERS.md for technical details
- 💬 Open an issue for deployment-specific questions

---

*Happy trading! Keep IBIS running smoothly.* 🦅
