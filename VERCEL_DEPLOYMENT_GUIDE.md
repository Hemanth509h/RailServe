# Vercel Deployment Guide for RailServe

## Prerequisites
- Vercel account (sign up at https://vercel.com)
- GitHub account (recommended for automatic deployments)
- PostgreSQL database (or the app will use SQLite automatically)

## Step-by-Step Deployment Instructions

### Option 1: Deploy via Vercel CLI (Recommended)

#### 1. Install Vercel CLI
```bash
npm install -g vercel
```

#### 2. Login to Vercel
```bash
vercel login
```

#### 3. Deploy from Project Directory
```bash
# Navigate to your project directory
cd /path/to/railserve

# Deploy to Vercel
vercel
```

#### 4. Follow the prompts:
- Set up and deploy? **Yes**
- Which scope? **Select your account**
- Link to existing project? **No**
- Project name? **railserve** (or your preferred name)
- In which directory is your code located? **./

#### 5. Set Environment Variables (Important!)
After deployment, add these environment variables in Vercel Dashboard:

Go to: **Project Settings → Environment Variables**

Add these variables:
```
DATABASE_URL = your_postgresql_connection_string
SESSION_SECRET = generate_a_random_secret_key_here
FLASK_ENV = production
```

**Note:** If you don't set `DATABASE_URL`, the app will automatically use SQLite (which works but is not recommended for production).

#### 6. Initialize the Database
After deployment, you need to run the database initialization:

```bash
# SSH into Vercel or run locally pointing to production DB
python init_db.py
```

OR use Vercel's serverless function to initialize (create a route for it).

#### 7. Deploy Production Version
```bash
vercel --prod
```

---

### Option 2: Deploy via GitHub Integration

#### 1. Push Code to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin your-github-repo-url
git push -u origin main
```

#### 2. Import Project in Vercel
- Go to https://vercel.com/new
- Click **Import Git Repository**
- Select your GitHub repository
- Click **Import**

#### 3. Configure Build Settings
Vercel will automatically detect Python and use the configuration from `vercel.json`.

#### 4. Add Environment Variables
Before deploying, add these in the **Environment Variables** section:
```
DATABASE_URL = your_postgresql_connection_string
SESSION_SECRET = random_secret_key_minimum_32_characters
FLASK_ENV = production
```

#### 5. Click Deploy
Vercel will build and deploy your application.

#### 6. Initialize Database
After first deployment, you need to initialize the database:
- Option A: Run `python init_db.py` locally with your production DATABASE_URL
- Option B: Create a temporary admin route to trigger initialization (remove after use)

---

## Database Options

### Option 1: External PostgreSQL (Recommended)
Use a managed PostgreSQL service:
- **Neon** (https://neon.tech) - Free tier available
- **Supabase** (https://supabase.com) - Free tier available
- **Railway** (https://railway.app) - Free tier available
- **ElephantSQL** (https://www.elephantsql.com) - Free tier available

Get the connection string and add it as `DATABASE_URL` environment variable.

### Option 2: SQLite Fallback (Built-in)
If no `DATABASE_URL` is provided, the app automatically falls back to SQLite.
**Note:** SQLite on Vercel is ephemeral (resets on deployments).

### Option 3: Vercel Postgres (Paid)
Vercel offers managed PostgreSQL:
- Go to your project in Vercel
- Click **Storage** tab
- Create a **Postgres** database
- It will automatically set the `DATABASE_URL` environment variable

---

## Important Configuration Notes

### 1. Database Fallback System
The app has automatic database fallback:
```
PostgreSQL (DATABASE_URL) → SQLite (if connection fails)
```

This ensures your app always runs, even without a database connection.

### 2. Static Files
Static files are served from `/static` directory. Vercel handles this automatically via the route configuration in `vercel.json`.

### 3. Security Settings
- `SESSION_SECRET`: Must be set in production (automatically falls back to generated key in dev)
- `FLASK_ENV=production`: Enables secure cookies and production optimizations
- CSRF protection is enabled by default

### 4. Database Initialization
After deployment, initialize the database with:
```bash
python init_db.py
```

This creates:
- 1,000 railway stations
- 1,500 trains
- Train routes
- Seat availability data
- Admin user (username: `admin`, password: `admin123`)

**Remember to change the admin password after first login!**

---

## Troubleshooting

### Issue: App shows 500 error
**Solution:** Check environment variables are set correctly, especially `DATABASE_URL`

### Issue: Database connection timeout
**Solution:** App will automatically fall back to SQLite. Check your PostgreSQL connection string.

### Issue: Static files not loading
**Solution:** Ensure `vercel.json` routes are configured correctly (already done in this project)

### Issue: Database tables don't exist
**Solution:** Run `python init_db.py` to initialize the database

---

## Post-Deployment Checklist

- [ ] App is accessible at your Vercel URL
- [ ] Environment variables are set (`DATABASE_URL`, `SESSION_SECRET`)
- [ ] Database is initialized (`python init_db.py`)
- [ ] Admin login works (username: `admin`, password: `admin123`)
- [ ] Change admin password after first login
- [ ] Test train search functionality
- [ ] Test booking flow
- [ ] Configure custom domain (optional)

---

## Custom Domain Setup (Optional)

1. Go to your Vercel project dashboard
2. Click **Settings** → **Domains**
3. Add your custom domain
4. Update your domain's DNS records as instructed by Vercel

---

## Monitoring and Logs

View application logs in Vercel Dashboard:
- Go to your project
- Click **Deployments** → Select deployment → **Function Logs**

---

## Support Resources

- Vercel Documentation: https://vercel.com/docs
- Flask on Vercel Guide: https://vercel.com/guides/deploying-flask-to-vercel
- RailServe Admin Panel: `/admin` (after deployment)

---

**Your RailServe app is now ready for deployment! 🚀**
