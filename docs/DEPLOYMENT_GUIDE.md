# RailServe Deployment Guide

## Deployment Architecture

RailServe uses a two-application architecture:
1. **Database API** - SQLite database with REST API
2. **Main Application** - Frontend and business logic

Both applications need to be deployed separately.

## Prerequisites

- Vercel account (for database API)
- Hosting platform account for main app (Vercel, Railway, etc.)
- Git repository (optional but recommended)

## Step 1: Deploy Database API

### Option A: Deploy with Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Navigate to database API**:
   ```bash
   cd database-api
   ```

3. **Deploy**:
   ```bash
   vercel
   ```

4. **Follow the prompts**:
   - Link to existing project or create new
   - Set project name (e.g., `railserve-db-api`)
   - Confirm deployment

5. **Note the deployment URL**:
   ```
   https://railserve-db-api.vercel.app
   ```

### Option B: Deploy via Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your Git repository
4. Set root directory to `database-api`
5. Deploy

### Option C: Deploy from GitHub

1. Push `database-api` folder to GitHub
2. Connect Vercel to your repository
3. Configure:
   - **Root Directory**: `database-api`
   - **Build Command**: (leave empty)
   - **Output Directory**: (leave empty)
4. Deploy

## Step 2: Configure Database API

### Environment Variables (Optional)

In Vercel dashboard, add:
- `SECRET_KEY` - Flask secret key (optional, auto-generated if not set)

### Test the API

```bash
# Health check
curl https://your-api-url.vercel.app/health

# Get stations
curl https://your-api-url.vercel.app/api/stations

# Get trains
curl https://your-api-url.vercel.app/api/trains
```

## Step 3: Deploy Main Application

### Option A: Vercel

1. **Set environment variable**:
   ```bash
   DATABASE_API_URL=https://your-database-api.vercel.app
   SESSION_SECRET=your-secret-key-here
   FLASK_ENV=production
   ```

2. **Deploy**:
   ```bash
   vercel
   ```

### Option B: Railway

1. **Create new project** on Railway
2. **Add environment variables**:
   ```
   DATABASE_API_URL=https://your-database-api.vercel.app
   SESSION_SECRET=your-secret-key-here
   FLASK_ENV=production
   ```
3. **Deploy from GitHub** or using Railway CLI

### Option C: Other Platforms

For any platform that supports Python/Flask:

1. **Set environment variables**:
   - `DATABASE_API_URL`
   - `SESSION_SECRET`
   - `FLASK_ENV=production`

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run with Gunicorn**:
   ```bash
   gunicorn --bind 0.0.0.0:5000 --reuse-port main:app
   ```

## Step 4: Initialize Database

The SQLite database (`railway.db`) is created automatically when the database API starts. To populate it with initial data:

### Option 1: Manual Initialization

Create a script to call your API endpoints and populate data:

```python
import requests

API_URL = "https://your-api.vercel.app"

# Add stations
stations = [
    {"name": "Mumbai Central", "code": "BCT", "city": "Mumbai", "state": "Maharashtra"},
    {"name": "New Delhi", "code": "NDLS", "city": "Delhi", "state": "Delhi"},
    # ... more stations
]

for station in stations:
    requests.post(f"{API_URL}/api/stations", json=station)
```

### Option 2: Database Import

1. Download an existing `railway.db` file
2. Deploy it with your database API

## Step 5: Post-Deployment Checks

### 1. Test Database API

```bash
# Health check
curl https://your-db-api.vercel.app/health

# Check endpoints
curl https://your-db-api.vercel.app/api/stations
curl https://your-db-api.vercel.app/api/trains
```

### 2. Test Main Application

- Visit your main app URL
- Try user registration
- Test login
- Search for trains
- Test booking flow

### 3. Check Logs

**Vercel:**
```bash
vercel logs
```

**Railway:**
- Check logs in Railway dashboard

## Environment Variables Reference

### Database API
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | No | Auto-generated | Flask secret key |

### Main Application
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_API_URL` | **Yes** | - | Database API URL |
| `SESSION_SECRET` | **Yes** | - | Session encryption key |
| `FLASK_ENV` | No | development | Environment mode |

## Troubleshooting

### Database API Issues

**Problem**: API returns 404
- **Solution**: Check that routes are registered in `app.py`
- **Solution**: Verify the endpoint path

**Problem**: Database not persisting
- **Solution**: Check Vercel storage limits
- **Solution**: Consider using external database for production

**Problem**: CORS errors
- **Solution**: Update CORS configuration in `database-api/app.py`

### Main Application Issues

**Problem**: Can't connect to database API
- **Solution**: Verify `DATABASE_API_URL` is set correctly
- **Solution**: Check API is accessible (test with curl)

**Problem**: 500 errors
- **Solution**: Check application logs
- **Solution**: Verify all environment variables are set

## Production Considerations

### Security

1. **Enable HTTPS**: Both applications should use HTTPS
2. **Restrict CORS**: Update CORS settings to allow only your main app
3. **Add API Authentication**: Consider adding API keys
4. **Secure Environment Variables**: Use platform secret management

### Performance

1. **CDN**: Use Vercel's CDN for static assets
2. **Caching**: Implement caching for frequently accessed data
3. **Database**: Consider PostgreSQL for high-traffic production

### Monitoring

1. **Vercel Analytics**: Enable for both applications
2. **Error Tracking**: Add Sentry or similar service
3. **Uptime Monitoring**: Use UptimeRobot or similar

### Backup

1. **Database Backup**: Regularly download `railway.db`
2. **Git Backups**: Keep code in version control
3. **Automated Backups**: Set up scheduled backups

## Scaling

### Database API Scaling

- Vercel handles scaling automatically
- Consider moving to dedicated database (PostgreSQL) for high traffic
- Implement Redis caching

### Main Application Scaling

- Use Vercel's automatic scaling
- Or configure horizontal scaling on your platform
- Implement load balancing if needed

## Cost Considerations

### Vercel Free Tier Limits
- 100 GB bandwidth/month
- 100 hours serverless function execution
- 6,000 minutes build time

### Upgrade When
- Traffic exceeds free tier
- Need custom domains
- Require team features

## Maintenance

### Regular Tasks

1. **Monitor Logs**: Check for errors weekly
2. **Update Dependencies**: Monthly security updates
3. **Database Backup**: Weekly backups
4. **Performance Review**: Monthly analysis

### Update Deployment

```bash
# Update database API
cd database-api
vercel --prod

# Update main application  
vercel --prod
```

## Rollback

### Vercel Rollback

1. Go to Vercel dashboard
2. Select your project
3. Click on "Deployments"
4. Find previous working deployment
5. Click "Promote to Production"

### Manual Rollback

1. Revert code changes in Git
2. Redeploy applications

---

**Note**: This deployment guide assumes you're using Vercel for the database API. Adjust accordingly if using other platforms.
