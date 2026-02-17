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

Example SECRET_KEY: `amahle-prod-$(openssl rand -hex 16)`

#### Payment Processing:
- `STRIPE_SECRET_KEY`: Your Stripe secret key
- `STRIPE_PUBLISHABLE_KEY`: Your Stripe publishable key
- `PAYPAL_CLIENT_ID`: Your PayPal client ID
- `PAYPAL_CLIENT_SECRET`: Your PayPal secret

#### Email Configuration (REQUIRED for app to work):
- `MAIL_SERVER`: SMTP server (e.g., smtp.gmail.com)
- `MAIL_PORT`: Port number (usually 587)
- `MAIL_USE_TLS`: True
- `MAIL_USERNAME`: Email address for sending emails
- `MAIL_PASSWORD`: Email password or app-specific password
- `MAIL_DEFAULT_SENDER`: Default sender email

#### Maps & Geolocation:
- `GOOGLE_MAPS_API_KEY`: Your Google Maps API key

#### Optional (for real-time features):
- `CELERY_BROKER_URL`: Redis URL (if using background tasks)
- `CELERY_RESULT_BACKEND`: Redis URL for results
- `SOCKETIO_MESSAGE_QUEUE`: Redis URL for WebSocket messaging

#### Admin/Company:
- `ADMIN_EMAIL`: Admin email address

### 5. Database
- **No external database needed!** The app uses SQLite.
- Database file is stored on Render and persists between deployments.

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

## Environment Variables Summary

### Minimal Setup (for testing)
```
FLASK_ENV=production
SECRET_KEY=your-secure-random-key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@amahlrentals.com
ADMIN_EMAIL=admin@amahlrentals.com
```

### Full Setup (with all features)
```
FLASK_ENV=production
SECRET_KEY=your-secure-random-key
STRIPE_SECRET_KEY=sk_live_xxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxx
PAYPAL_CLIENT_ID=xxxx
PAYPAL_CLIENT_SECRET=xxxx
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@amahlrentals.com
GOOGLE_MAPS_API_KEY=AIza_xxxx
ADMIN_EMAIL=admin@amahlrentals.com
ENABLE_RECOMMENDATIONS=True
```

## Troubleshooting

### Email Not Sending
- Verify MAIL credentials are correct
- For Gmail, use an App Password (not your regular password):
  1. Go to https://myaccount.google.com/apppasswords
  2. Select Mail and Windows Computer
  3. Generate password and use it as MAIL_PASSWORD
- Check SMTP settings (server, port, TLS)

### Payment Integration Not Working
- Verify API keys are correct
- Check that keys match your test/production environment
- Review payment service dashboard for errors

### Static Files Not Loading
- Flask serves static files from `app/static/`
- Ensure CSS/JS files are included in git

### Database Issues
- SQLite database is stored in the app directory
- First deployment with `init_db.py` creates the database
- Subsequent deployments query the existing database
- To reset database, delete `rental_booking.db` and redeploy

## File Structure for Deployment

- `Procfile` - Tells Render how to run your app
- `runtime.txt` - Specifies Python version
- `render.yaml` - Render infrastructure configuration
- `requirements.txt` - Python dependencies with gunicorn, eventlet, psycopg2
- `config.py` - SQLite database configuration
- `.env.example` - Template for environment variables

## Next Steps

1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Test locally: `python run.py`
3. Commit all changes to Git: `git add . && git commit -m "Ready for Render"`
4. Push to GitHub: `git push origin main`
5. Follow the deployment steps above on Render
6. Monitor your app on Render dashboard

