# VillageBid Deployment Checklist

**Use this checklist when preparing to deploy to production**

---

## 📋 Pre-Deployment Phase (1-2 weeks before)

### Code Preparation
- [ ] All tests passing (`python manage.py test`)
- [ ] No Django warnings (`python manage.py check --deploy`)
- [ ] Code reviewed and approved
- [ ] All features documented
- [ ] Changelog updated
- [ ] Version number bumped

### Security Review
- [ ] ALLOWED_HOSTS configured
- [ ] SECRET_KEY changed
- [ ] DEBUG = False set
- [ ] SECURE_SSL_REDIRECT = True
- [ ] SESSION_COOKIE_SECURE = True
- [ ] CSRF_COOKIE_SECURE = True
- [ ] Security headers configured
- [ ] CORS settings reviewed
- [ ] Razorpay keys secure
- [ ] Cloudinary keys secure

### Documentation Review
- [ ] DEPLOYMENT_GUIDE.md read
- [ ] Environment variables prepared
- [ ] Database setup documented
- [ ] Backup procedures tested
- [ ] Rollback plan documented

---

## 🗄️ Database Phase (1 week before)

### PostgreSQL Setup
- [ ] PostgreSQL installed
- [ ] Database created: `createdb villagebid`
- [ ] User created: `createuser villagebid_user`
- [ ] User permissions granted
- [ ] Database backups configured
- [ ] Test connection successful

### Migration Testing
- [ ] All migrations run: `python manage.py migrate`
- [ ] No errors in migration log
- [ ] Database tables created
- [ ] Constraints verified
- [ ] Indexes created
- [ ] Backup taken

### Superuser Setup
- [ ] Superuser created: `python manage.py createsuperuser`
- [ ] Admin login tested
- [ ] Admin interface working
- [ ] Sample data loaded (optional)

---

## 📁 Static Files Phase (1 week before)

### File Configuration
- [ ] STATIC_ROOT configured
- [ ] MEDIA_ROOT configured
- [ ] Cloudinary account set up (if using)
- [ ] AWS S3 configured (if using)
- [ ] Permissions verified

### Collection
- [ ] `python manage.py collectstatic --noinput` successful
- [ ] Static files compressed
- [ ] No missing files
- [ ] CDN configured (if using)
- [ ] Cache headers set

---

## 🔐 Security Phase (1 week before)

### HTTPS/SSL
- [ ] Domain purchased and configured
- [ ] SSL certificate obtained (Let's Encrypt)
- [ ] Certificate installed
- [ ] HTTPS redirect working
- [ ] SSL test passed (qualys.com)

### Authentication
- [ ] First admin user created
- [ ] Additional admin users created
- [ ] Staff permissions set correctly
- [ ] Superuser password strong
- [ ] 2FA enabled (if available)

### Secrets Management
- [ ] All secrets in environment variables
- [ ] .env file not in git repo
- [ ] .env.example in repo (without secrets)
- [ ] Secrets rotation scheduled
- [ ] Access logs configured

---

## 🖥️ Server Setup Phase (3-5 days before)

### Web Server (Gunicorn)
- [ ] Gunicorn installed
- [ ] Gunicorn configuration created
- [ ] Worker count calculated
- [ ] Timeout values set
- [ ] Systemd service created
- [ ] Auto-restart configured

### Reverse Proxy (Nginx)
- [ ] Nginx installed
- [ ] Nginx configuration created
- [ ] Static files path correct
- [ ] Proxy settings configured
- [ ] Gzip compression enabled
- [ ] Cache headers set
- [ ] Security headers added

### Process Management
- [ ] Systemd service for Gunicorn
- [ ] Systemd service for Celery (if used)
- [ ] Systemd service for Redis (if used)
- [ ] Auto-start on reboot enabled
- [ ] Process monitoring configured

---

## 🔧 Dependencies Phase (3-5 days before)

### System Packages
- [ ] Python 3.13+ installed
- [ ] PostgreSQL installed
- [ ] Redis installed (if using)
- [ ] Nginx installed
- [ ] Git installed

### Python Packages
- [ ] Virtual environment created
- [ ] `pip install -r requirements.txt` successful
- [ ] No conflicting versions
- [ ] Security scan passed (safety)
- [ ] Licenses reviewed

### Third-Party Services
- [ ] Razorpay account set up
- [ ] Razorpay test keys working
- [ ] Razorpay production keys obtained
- [ ] Cloudinary account set up
- [ ] Cloudinary API keys obtained
- [ ] Redis connection working (if using)

---

## 📊 Monitoring Setup Phase (2-3 days before)

### Logging
- [ ] Django logging configured
- [ ] Gunicorn logging configured
- [ ] Nginx logging configured
- [ ] Log rotation configured
- [ ] Log files writable

### Monitoring Tools
- [ ] Sentry configured for error tracking
- [ ] Application insights/monitoring tool set up
- [ ] Uptime monitoring configured
- [ ] Alert emails configured
- [ ] Slack/Discord notifications (optional)

### Metrics
- [ ] CPU usage monitoring
- [ ] Memory usage monitoring
- [ ] Disk space monitoring
- [ ] Database monitoring
- [ ] Network monitoring

---

## 🧪 Testing Phase (1-2 days before)

### Functionality Testing
- [ ] User registration works
- [ ] Login/logout works
- [ ] Product creation works
- [ ] Product listing works
- [ ] Auction bidding works
- [ ] Payment processing works (test mode)
- [ ] Admin interface works
- [ ] All pages load correctly

### Performance Testing
- [ ] Page load time < 2 seconds
- [ ] Database queries optimized
- [ ] No N+1 query problems
- [ ] Static files cached properly
- [ ] Compression working

### Security Testing
- [ ] HTTPS redirects working
- [ ] SSL certificate valid
- [ ] CSRF protection active
- [ ] SQL injection prevention verified
- [ ] XSS protection verified
- [ ] No hardcoded secrets
- [ ] Security headers present

### Mobile Testing
- [ ] Responsive design on mobile
- [ ] Touch interactions work
- [ ] Forms usable on small screens
- [ ] Images load properly
- [ ] Performance acceptable

---

## 🚀 Deployment Day

### Pre-Deployment
- [ ] Full database backup taken
- [ ] Current version tagged in Git
- [ ] Deployment plan reviewed
- [ ] Team communication sent
- [ ] Maintenance window scheduled (if needed)

### Deployment Steps
- [ ] Pull latest code from Git
- [ ] Install new dependencies
- [ ] Run new migrations: `python manage.py migrate`
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Restart Gunicorn/web server
- [ ] Clear cache (if applicable)
- [ ] Verify services starting

### Verification
- [ ] Check server status
- [ ] Verify application running
- [ ] Test home page loads
- [ ] Check admin interface
- [ ] Monitor error logs
- [ ] Check monitoring dashboards
- [ ] Verify backup completed

### Post-Deployment (First Hour)
- [ ] Error rate normal
- [ ] Page load times acceptable
- [ ] No critical errors in logs
- [ ] Admin operations working
- [ ] Payment processing tested
- [ ] Email notifications working (if any)

---

## 📈 Post-Deployment Phase (24-72 hours)

### Monitoring
- [ ] Error logs reviewed hourly
- [ ] Performance metrics normal
- [ ] Database performance acceptable
- [ ] No unexpected resource usage
- [ ] Security logs normal
- [ ] User feedback positive

### Testing
- [ ] User registration tested
- [ ] Product lifecycle tested
- [ ] Auction functionality tested
- [ ] Payment flow tested end-to-end
- [ ] Admin operations tested
- [ ] Email/notifications tested
- [ ] Mobile access tested

### Fixes
- [ ] Any bugs identified and logged
- [ ] Hotfixes deployed if critical
- [ ] Minor issues scheduled for next release
- [ ] Performance optimizations noted

### Announcement
- [ ] Team notified of successful deployment
- [ ] Status page updated
- [ ] Users notified of new features (if any)
- [ ] Documentation updated

---

## 🔄 Rollback Plan (If Needed)

### Immediate Rollback
- [ ] Kill current Gunicorn process
- [ ] Revert code to previous version: `git revert <commit>`
- [ ] Revert database (if needed): `python manage.py migrate <previous>`
- [ ] Restart Gunicorn
- [ ] Verify previous version working
- [ ] Monitor for issues

### Communication
- [ ] Notify users of rollback
- [ ] Document issue
- [ ] Schedule fix for next deployment
- [ ] Post-mortem meeting scheduled

---

## ✅ Sign-Off

- [ ] Deployment completed successfully
- [ ] All tests passing
- [ ] Monitoring alerts configured
- [ ] Team trained on new features
- [ ] Documentation updated
- [ ] Project marked as deployed

**Deployment Date**: ________________  
**Deployed By**: ________________  
**Verified By**: ________________  
**Issues Found**: ________________  
**Rollback Needed**: [ ] Yes [ ] No

---

## 📞 Support Contacts

**In case of emergency during/after deployment:**

- **Lead Developer**: _________________
- **DevOps Engineer**: _________________
- **Database Admin**: _________________
- **System Admin**: _________________
- **On-Call Support**: _________________

---

## 📚 Documentation Links

- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [README](README.md)
- [Quick Reference](QUICK_REFERENCE.md)
- [Completion Report](COMPLETION_REPORT.md)

---

**Last Updated**: June 19, 2026  
**Version**: 1.0
