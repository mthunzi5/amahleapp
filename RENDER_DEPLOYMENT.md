# Amahle Render Deployment Guide

## Deployment Steps

### 1. Prerequisites
- GitHub account (push your code to GitHub)
- Render account (https://render.com)

### 2. Prepare Your GitHub Repository
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 3. Connect Render to GitHub
1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Select "Build and deploy from a Git repository"
4. Connect your GitHub account
5. Select your Amahle repository

### 4. Configure Environment Variables on Render

In the Render dashboard, add these environment variables:

#### Required:
- `SECRET_KEY`: Generate a secure key (recommended: 32+ character random string)
- `FLASK_ENV`: `production`
- `DATABASE_URL`: (Auto-populated by Render if you use their PostgreSQL)

#### Payment Processing:
- `STRIPE_SECRET_KEY`: Your Stripe secret key
- `STRIPE_PUBLISHABLE_KEY`: Your Stripe publishable key
- `PAYPAL_CLIENT_ID`: Your PayPal client ID
- `PAYPAL_CLIENT_SECRET`: Your PayPal secret

#### Email Configuration:
- `MAIL_SERVER`: SMTP server (e.g., smtp.gmail.com)
- `MAIL_PORT`: Port number (usually 587)
- `MAIL_USERNAME`: Email address for sending emails
- `MAIL_PASSWORD`: Email password or app-specific password
- `MAIL_DEFAULT_SENDER`: Default sender email

#### Maps & Geolocation:
- `GOOGLE_MAPS_API_KEY`: Your Google Maps API key

#### Optional (for real-time features):
- `CELERY_BROKER_URL`: Redis URL (can use Render Redis add-on)
- `CELERY_RESULT_BACKEND`: Redis URL for results
- `SOCKETIO_MESSAGE_QUEUE`: Redis URL for WebSocket messaging

#### Admin/Company:
- `ADMIN_EMAIL`: Admin email address

### 5. Add PostgreSQL Database on Render
1. On your Render web service config page
2. Scroll down to "Database"
3. Click "Create Database" or link an existing one
4. Select PostgreSQL
5. The `DATABASE_URL` environment variable will be automatically set

### 6. Deploy
1. Make sure your `render.yaml` file is in the root directory
2. Click "Deploy service"
3. Render will:
   - Build your app
   - Install dependencies from `requirements.txt`
   - Run `init_db.py` to initialize the database
   - Start the web server with Gunicorn

### 7. Verify Deployment
- Check Render dashboard for deployment status
- Visit your app URL: `https://your-app-name.onrender.com`
- Check logs for any errors

## Troubleshooting

### Database Connection Issues
- Ensure `DATABASE_URL` is set correctly
- Check that PostgreSQL database is created on Render
- Verify firewall/IP allowlist settings

### Email Not Sending
- Verify MAIL credentials are correct
- For Gmail, use an App Password (not your regular password)
- Check SMTP settings (server, port, TLS)

### Payment Integration Not Working
- Verify API keys are correct
- Check that keys match your test/production environment
- Review payment service dashboard for errors

### Static Files Not Loading
- Flask will serve static files from `app/static/`
- Ensure CSS/JS files are included in git
- Check file permissions

## File Structure Created for Deployment

- `Procfile` - Tells Render how to run your app
- `runtime.txt` - Specifies Python version
- `render.yaml` - Render infrastructure configuration
- Updated `requirements.txt` - Added gunicorn, eventlet, psycopg2
- Updated `config.py` - PostgreSQL URL handling for Render

## Next Steps

1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Test locally: `python run.py`
3. Commit all changes to Git
4. Follow the deployment steps above
5. Monitor your app on Render dashboard
