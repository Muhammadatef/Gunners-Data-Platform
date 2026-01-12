# CI/CD Guide for Arsenal Analytics Platform

## What is CI/CD?

**Continuous Integration (CI)** and **Continuous Deployment (CD)** are software development practices that automate testing and deployment.

### Why CI/CD Matters

1. **Catch Bugs Early**: Automated tests run on every code change
2. **Faster Releases**: Deploy in minutes instead of hours
3. **Consistent Quality**: Every deployment follows the same process
4. **Team Confidence**: Know your code works before it reaches production

---

## Our CI/CD Pipeline

### Overview

```
Developer Pushes Code
    ↓
GitHub Triggers Workflow
    ↓
Run Tests (CI)
    ├─ Linting (Code Quality)
    ├─ Unit Tests (Scrapers)
    ├─ Integration Tests (Database)
    └─ Security Scans
    ↓
Tests Pass? ──NO──> Send Notification, Stop
    ↓ YES
Build Docker Images (CD)
    ├─ Airflow Image
    └─ Dashboard Image
    ↓
Push to Docker Hub
    ↓
Deploy to Production Server
    ├─ Pull New Images
    ├─ Restart Services
    └─ Run Health Checks
    ↓
Success! ──> Send Notification
```

---

## Part 1: Continuous Integration (CI)

### Workflow File: `.github/workflows/ci.yml`

This file defines what happens when you push code.

#### Job 1: Code Quality Checks (Linting)

**What it does**: Checks code follows Python best practices

```yaml
- name: Run Black (code formatter check)
  run: black --check scrapers/ dags/ dashboard/
```

**Tools Used**:
- **Black**: Auto-formatter (ensures consistent style)
- **Flake8**: Linter (catches common mistakes)
- **Pylint**: Advanced linter (finds potential bugs)

**Example**: Catches issues like:
- Unused variables
- Missing imports
- Inconsistent indentation
- Code complexity warnings

#### Job 2: Test Scrapers

**What it does**: Validates scrapers work correctly

```yaml
- name: Run scraper tests
  run: pytest tests/test_scrapers.py -v --cov=scrapers
```

**Tests Include**:
1. **Structure Validation**: Check scraper output has required fields
2. **Data Quality**: Validate xG values are 0-1, coordinates are normalized
3. **Match Integrity**: Goals in metadata match Goal shots
4. **Player Data**: Ensure player names are populated

**Why Important**: If Understat changes their website structure, tests will catch it immediately.

#### Job 3: Test Database Schema

**What it does**: Validates database structure is correct

```yaml
services:
  postgres:
    image: postgres:15
```

**Process**:
1. Spin up a temporary PostgreSQL database
2. Run all migration scripts (create schemas, tables, views)
3. Verify all tables and columns exist
4. Check data integrity constraints

**Tests Include**:
- Bronze layer tables exist
- Silver layer views have correct columns
- Metrics layer views are accessible
- No NULL player names in data
- xG values within valid range

#### Job 4: Security Scans

**What it does**: Finds security vulnerabilities

**Tools**:
- **Safety**: Scans Python dependencies for known CVEs
- **Bandit**: Analyzes code for security issues

**Example Catches**:
- Outdated packages with security fixes
- SQL injection risks
- Hardcoded passwords
- Insecure random number generation

---

## Part 2: Continuous Deployment (CD)

### Workflow File: `.github/workflows/cd.yml`

This file defines how code gets deployed to production.

#### Job 1: Build & Push Docker Images

**What it does**: Creates Docker images and uploads to Docker Hub

```yaml
- name: Build and push Dashboard image
  uses: docker/build-push-action@v5
  with:
    context: ./dashboard
    push: true
    tags: yourusername/arsenal-dashboard:latest
```

**Process**:
1. Log in to Docker Hub using secrets
2. Build Airflow image from `airflow/Dockerfile`
3. Build Dashboard image from `dashboard/Dockerfile`
4. Tag with two versions:
   - `latest` (always current)
   - `{git-commit-sha}` (specific version for rollback)
5. Push to Docker Hub registry

**Why Two Tags?**:
- `latest`: Easy for users to pull newest version
- `{sha}`: Can rollback to exact previous version if needed

#### Job 2: Deploy to Production

**What it does**: Updates running services on production server

```yaml
- name: Deploy via SSH
  script: |
    cd /opt/arsenal-analytics
    git pull origin main
    docker compose pull
    docker compose up -d --no-deps --build dashboard
```

**Process**:
1. SSH into production server using private key
2. Pull latest code from GitHub
3. Pull latest Docker images
4. Restart services one by one (zero downtime)
5. Wait for health checks

**Zero Downtime Strategy**:
- `--no-deps`: Only restart changed service
- Services restart individually, not all at once
- Health checks verify before marking success

#### Job 3: Health Checks

**What it does**: Verifies deployment succeeded

```yaml
- name: Health Check
  run: |
    curl -f https://dashboard.example.com/_stcore/health
    curl -f https://airflow.example.com/health
```

**Checks**:
- Dashboard responds to HTTP requests
- Airflow scheduler is running
- Database is accessible

**If Health Checks Fail**: Automatic rollback triggered

#### Job 4: Rollback on Failure

**What it does**: Reverts to previous version if deployment fails

```yaml
if: failure()
steps:
  - Revert to previous Git commit
  - Restart with old Docker images
```

**Process**:
1. Detect failure from previous job
2. SSH into server
3. `git reset --hard HEAD~1` (undo last commit)
4. Restart containers with previous images
5. Notify team of rollback

---

## Setting Up CI/CD

### Step 1: Create GitHub Repository Secrets

Go to: **GitHub Repo → Settings → Secrets and variables → Actions**

Add these secrets:

| Secret Name | Purpose | Example |
|-------------|---------|---------|
| `DOCKER_USERNAME` | Docker Hub username | `muhammadatef` |
| `DOCKER_PASSWORD` | Docker Hub password/token | `dckr_pat_abc123...` |
| `DEPLOY_HOST` | Production server IP | `165.232.123.45` |
| `DEPLOY_USER` | SSH username | `ubuntu` |
| `DEPLOY_SSH_KEY` | SSH private key | `-----BEGIN RSA PRIVATE KEY-----...` |
| `DEPLOY_PORT` | SSH port | `22` |
| `DASHBOARD_URL` | Dashboard URL for health check | `http://165.232.123.45:8501` |
| `AIRFLOW_URL` | Airflow URL for health check | `http://165.232.123.45:8080` |
| `SLACK_WEBHOOK` | Slack notification webhook | `https://hooks.slack.com/...` |

### Step 2: Generate SSH Key for Deployment

On your local machine:

```bash
# Generate new SSH key pair
ssh-keygen -t rsa -b 4096 -f ~/.ssh/arsenal_deploy_key

# Copy public key to production server
ssh-copy-id -i ~/.ssh/arsenal_deploy_key.pub user@production-server

# Copy private key contents to GitHub Secret
cat ~/.ssh/arsenal_deploy_key
# Paste output into DEPLOY_SSH_KEY secret
```

### Step 3: Create Docker Hub Repository

1. Go to https://hub.docker.com
2. Create two repositories:
   - `arsenal-airflow` (Public or Private)
   - `arsenal-dashboard` (Public or Private)
3. Generate access token: **Account Settings → Security → New Access Token**
4. Copy token to `DOCKER_PASSWORD` secret

### Step 4: Configure Production Server

SSH into your production server and set up deployment directory:

```bash
# Create deployment directory
sudo mkdir -p /opt/arsenal-analytics
sudo chown $USER:$USER /opt/arsenal-analytics

# Clone repository
cd /opt/arsenal-analytics
git clone https://github.com/yourusername/arsenal-analytics.git .

# Create environment file
cp .env.example .env
nano .env  # Edit with production values

# Initial deployment
docker compose up -d
```

### Step 5: Test CI/CD Pipeline

**Test CI (No Deployment)**:
```bash
# Create feature branch
git checkout -b test-ci

# Make a small change
echo "# Test" >> README.md

# Push to GitHub
git add .
git commit -m "Test CI pipeline"
git push origin test-ci

# Create Pull Request on GitHub
# Watch Actions tab - CI tests should run
```

**Test CD (Deployment)**:
```bash
# Merge to main branch
git checkout main
git merge test-ci
git push origin main

# Watch Actions tab - CD should deploy
```

---

## Understanding the Workflow Triggers

### When Does CI Run?

```yaml
on:
  push:
    branches: [ main, develop ]  # Runs on push to these branches
  pull_request:
    branches: [ main ]  # Runs on PR to main
```

**Examples**:
- Push to `main` → Runs CI + CD
- Push to `develop` → Runs CI only
- Push to `feature-branch` → Nothing happens
- Create PR to `main` → Runs CI only

### When Does CD Run?

```yaml
if: github.ref == 'refs/heads/main'  # Only on main branch
```

**Only runs when**:
- Code is pushed to `main` branch
- All CI tests pass
- Can also trigger manually from Actions tab

---

## Monitoring Your Pipeline

### GitHub Actions Tab

1. Go to your repository on GitHub
2. Click **Actions** tab
3. See all workflow runs:
   - ✅ Green checkmark = Passed
   - ❌ Red X = Failed
   - 🟡 Yellow dot = Running

### Viewing Logs

1. Click on a workflow run
2. Click on individual jobs (lint, test-scrapers, etc.)
3. Expand steps to see detailed logs
4. Download logs for debugging

### Slack Notifications

```yaml
- name: Notify deployment status
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

**Receives notifications for**:
- Deployment started
- Deployment succeeded
- Deployment failed (with error details)
- Rollback triggered

---

## Best Practices

### 1. Always Run Tests Locally First

```bash
# Before pushing, run tests locally
pytest tests/ -v

# Format code
black scrapers/ dags/ dashboard/

# Check linting
flake8 scrapers/ dags/ dashboard/
```

### 2. Use Feature Branches

```bash
# Don't commit directly to main
git checkout -b feature/add-player-positions

# Make changes, commit, push
git push origin feature/add-player-positions

# Create Pull Request on GitHub
# CI will test your changes
# Merge when tests pass
```

### 3. Version Your Docker Images

Always tag with Git commit SHA for easy rollback:

```bash
# Find commit SHA of last working version
git log --oneline

# Roll back to specific commit
git reset --hard abc1234

# Redeploy
git push --force origin main
```

### 4. Monitor Deployment Logs

```bash
# SSH into production server
ssh user@production-server

# Check logs
cd /opt/arsenal-analytics
docker compose logs -f --tail=100 dashboard
docker compose logs -f --tail=100 airflow-scheduler
```

### 5. Test Health Checks

```bash
# Manually test health endpoints
curl -f http://your-server:8501/_stcore/health
curl -f http://your-server:8080/health

# Should return 200 OK
```

---

## Troubleshooting

### CI Test Failures

**Problem**: Scraper tests fail

**Solution**:
```bash
# Run tests locally with verbose output
pytest tests/test_scrapers.py -v -s

# Check if Understat website changed
# Update scraper code in scrapers/playwright_scraper.py
```

**Problem**: Database tests fail

**Solution**:
```bash
# Check SQL syntax in database/init/*.sql
# Test locally with Docker Compose
docker compose up -d postgres
docker exec -it arsenalfc_postgres psql -U analytics_user -d arsenalfc_analytics
```

### Deployment Failures

**Problem**: Docker image build fails

**Solution**:
```bash
# Build locally to see full error
cd dashboard
docker build -t test-dashboard .

# Check Dockerfile and requirements.txt
```

**Problem**: SSH connection fails

**Solution**:
- Check `DEPLOY_HOST` secret is correct IP
- Verify `DEPLOY_SSH_KEY` has full private key including `-----BEGIN` and `-----END`
- Test SSH manually: `ssh -i ~/.ssh/key user@host`

**Problem**: Health checks timeout

**Solution**:
```bash
# SSH into server
# Check service status
docker compose ps

# Check logs
docker compose logs dashboard

# Restart service
docker compose restart dashboard
```

---

## Cost Considerations

### GitHub Actions Minutes

- **Free tier**: 2,000 minutes/month for private repos
- **Our pipeline**: ~10 minutes per run
- **Estimate**: 200 deployments/month free

### Docker Hub

- **Free tier**: Unlimited public repositories
- **Pull rate limits**: 200 pulls per 6 hours (anonymous), unlimited (authenticated)

### Production Server

- **Recommended**: DigitalOcean Droplet ($12/month, 2GB RAM)
- **Alternatives**: AWS EC2 t2.small, Linode, Vultr

---

## Next Steps

1. **Set up secrets** in GitHub repository
2. **Push workflows** to trigger first CI run
3. **Monitor Actions tab** to see tests pass
4. **Configure production server** for deployment
5. **Test deployment** with small change
6. **Set up Slack notifications** for team alerts

---

## Learning Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com)
- [CI/CD Best Practices](https://www.atlassian.com/continuous-delivery/principles/continuous-integration-vs-delivery-vs-deployment)
- [Pytest Documentation](https://docs.pytest.org)

---

## Summary

**CI/CD gives you**:
- ✅ Automated testing on every code change
- ✅ Consistent deployments
- ✅ Fast feedback loop
- ✅ Easy rollbacks
- ✅ Team confidence

**You learned**:
- How CI tests code quality, scrapers, database, security
- How CD builds, pushes, deploys Docker images
- How to set up secrets and SSH keys
- How to monitor and troubleshoot pipelines
- Best practices for safe deployments
