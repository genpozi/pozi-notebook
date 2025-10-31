# Production Deployment Checklist

This checklist ensures your Open Notebook deployment is secure, performant, and production-ready.

## 🔐 Security

### Authentication & Access Control

- [ ] **Change default admin password immediately**
  - Default: `admin@localhost` / `change-me-immediately`
  - Update via database or wait for profile UI (coming soon)

- [ ] **Create individual user accounts**
  - Use `/signup` page for each team member
  - Avoid sharing admin credentials

- [ ] **Review user permissions**
  - Verify each user has appropriate role (user/admin)
  - Remove unused accounts

- [ ] **Enable HTTPS/SSL**
  - Use reverse proxy (nginx, Caddy, Traefik)
  - Obtain SSL certificate (Let's Encrypt recommended)
  - Force HTTPS redirects

- [ ] **Configure secure environment variables**
  - Never commit secrets to Git
  - Use platform secret management
  - Rotate API keys regularly

### Database Security

- [ ] **Change default database credentials**
  ```env
  SURREAL_USER=your_secure_username
  SURREAL_PASSWORD=your_secure_password
  ```

- [ ] **Restrict database access**
  - Don't expose SurrealDB port (8000) publicly
  - Use internal networking only

- [ ] **Enable database backups**
  - Automated daily backups
  - Test restore procedures
  - Store backups securely off-site

### Network Security

- [ ] **Configure firewall rules**
  - Allow only necessary ports (80, 443, 8502, 5055)
  - Block direct database access
  - Use security groups/network policies

- [ ] **Set up rate limiting**
  - Protect against brute force attacks
  - Limit API request rates
  - Configure at reverse proxy level

- [ ] **Enable monitoring and alerts**
  - Failed login attempts
  - Unusual API usage
  - Resource exhaustion

---

## ⚙️ Configuration

### Environment Variables

- [ ] **Set production API URL**
  ```env
  API_URL=https://your-domain.com
  ```

- [ ] **Configure AI provider keys**
  ```env
  OPENAI_API_KEY=sk-...
  ANTHROPIC_API_KEY=sk-ant-...
  GOOGLE_API_KEY=AIzaSy...
  ```

- [ ] **Set database connection**
  ```env
  SURREAL_URL=ws://localhost:8000/rpc
  SURREAL_NAMESPACE=open_notebook
  SURREAL_DATABASE=production
  ```

- [ ] **Configure timeouts for your setup**
  ```env
  # Increase for slow AI providers or large documents
  API_CLIENT_TIMEOUT=300
  ESPERANTO_LLM_TIMEOUT=60
  ```

### Application Settings

- [ ] **Verify port configuration**
  - Frontend: 8502
  - API: 5055
  - Both must be accessible

- [ ] **Test API connectivity**
  ```bash
  curl https://your-domain.com/api/health
  ```

- [ ] **Configure CORS if needed**
  - Set allowed origins in `api/main.py`
  - Restrict to your domain only

---

## 🚀 Performance

### Resource Allocation

- [ ] **Allocate sufficient memory**
  - Minimum: 2GB RAM
  - Recommended: 4GB+ RAM
  - Increase for heavy usage

- [ ] **Allocate sufficient CPU**
  - Minimum: 2 cores
  - Recommended: 4+ cores
  - More cores = faster processing

- [ ] **Allocate sufficient storage**
  - Minimum: 10GB
  - Recommended: 50GB+
  - Monitor usage regularly

### Optimization

- [ ] **Enable persistent storage**
  - Mount volumes for `/app/data`
  - Mount volumes for `/mydata` (database)
  - Verify data persists across restarts

- [ ] **Configure caching**
  - Enable browser caching
  - Configure CDN if using one
  - Cache static assets

- [ ] **Optimize AI provider selection**
  - Use faster providers for real-time chat
  - Use cheaper providers for batch processing
  - Consider local models (Ollama) for privacy

---

## 📊 Monitoring

### Health Checks

- [ ] **Configure health check endpoint**
  - Endpoint: `/api/health`
  - Check interval: 30-60 seconds
  - Restart on failure

- [ ] **Monitor application logs**
  ```bash
  docker logs -f open-notebook
  ```

- [ ] **Set up log aggregation**
  - Centralized logging (ELK, Loki, etc.)
  - Log retention policy
  - Alert on errors

### Metrics

- [ ] **Monitor resource usage**
  - CPU utilization
  - Memory usage
  - Disk space
  - Network bandwidth

- [ ] **Track application metrics**
  - Request rates
  - Response times
  - Error rates
  - Active users

- [ ] **Set up alerts**
  - High CPU/memory usage
  - Disk space low
  - Application errors
  - Failed health checks

---

## 🔄 Backup & Recovery

### Backup Strategy

- [ ] **Automated database backups**
  ```bash
  # Example backup script
  docker exec open-notebook tar -czf /backup/surreal-$(date +%Y%m%d).tar.gz /mydata
  ```

- [ ] **Backup user data**
  ```bash
  # Backup notebooks and sources
  tar -czf notebook-data-$(date +%Y%m%d).tar.gz ./notebook_data
  ```

- [ ] **Backup configuration**
  - Save `docker-compose.yml`
  - Save `.env` file (securely!)
  - Document custom configurations

- [ ] **Test restore procedures**
  - Restore to test environment
  - Verify data integrity
  - Document restore steps

### Disaster Recovery

- [ ] **Document recovery procedures**
  - Step-by-step restore guide
  - Contact information
  - Escalation procedures

- [ ] **Store backups off-site**
  - Cloud storage (S3, GCS, etc.)
  - Different geographic region
  - Encrypted backups

- [ ] **Define RTO/RPO**
  - Recovery Time Objective
  - Recovery Point Objective
  - Test regularly

---

## 🔧 Maintenance

### Regular Tasks

- [ ] **Update Docker images**
  ```bash
  docker pull lfnovo/open_notebook:v1-latest-single
  docker-compose up -d
  ```

- [ ] **Review and rotate secrets**
  - API keys every 90 days
  - Database passwords every 180 days
  - SSL certificates (auto-renew)

- [ ] **Clean up old data**
  - Archive old notebooks
  - Remove unused sources
  - Prune Docker images/volumes

- [ ] **Review user accounts**
  - Remove inactive users
  - Audit admin access
  - Update permissions

### Updates

- [ ] **Subscribe to release notifications**
  - Watch GitHub repository
  - Join Discord for announcements
  - Check changelog regularly

- [ ] **Test updates in staging**
  - Deploy to test environment first
  - Verify functionality
  - Check for breaking changes

- [ ] **Plan maintenance windows**
  - Schedule during low usage
  - Notify users in advance
  - Have rollback plan ready

---

## 📚 Documentation

### Internal Documentation

- [ ] **Document deployment architecture**
  - Infrastructure diagram
  - Network topology
  - Service dependencies

- [ ] **Document configuration**
  - Environment variables
  - Custom settings
  - Integration details

- [ ] **Create runbooks**
  - Common operations
  - Troubleshooting steps
  - Emergency procedures

### User Documentation

- [ ] **Create user onboarding guide**
  - How to sign up
  - How to create notebooks
  - How to use key features

- [ ] **Document AI provider setup**
  - Which providers are available
  - How to get API keys
  - Cost considerations

- [ ] **Provide support channels**
  - Internal support contact
  - Discord community
  - GitHub issues

---

## ✅ Pre-Launch Checklist

### Final Verification

- [ ] **Test all core features**
  - User registration and login
  - Create notebook
  - Add sources (PDF, web, etc.)
  - Generate notes
  - Search functionality
  - Chat with AI
  - Generate podcast

- [ ] **Test from different devices**
  - Desktop browser
  - Mobile browser
  - Different networks
  - Different user accounts

- [ ] **Load testing**
  - Simulate multiple users
  - Test with large documents
  - Verify performance under load

- [ ] **Security audit**
  - Run security scanner
  - Check for exposed secrets
  - Verify SSL configuration
  - Test authentication

### Launch Preparation

- [ ] **Prepare rollback plan**
  - Document rollback steps
  - Keep previous version available
  - Test rollback procedure

- [ ] **Notify stakeholders**
  - Announce launch date
  - Provide access instructions
  - Share documentation

- [ ] **Monitor closely after launch**
  - Watch logs for errors
  - Monitor resource usage
  - Be ready to respond quickly

---

## 🆘 Troubleshooting

### Common Issues

**Can't access after deployment**
- Check firewall rules
- Verify ports are exposed
- Check API_URL configuration
- Review reverse proxy config

**Authentication not working**
- Verify JWT secret is set
- Check database connection
- Review user creation logs
- Test with default admin account

**Performance issues**
- Increase memory allocation
- Check AI provider response times
- Review database performance
- Monitor resource usage

**Database connection errors**
- Verify SurrealDB is running
- Check connection string
- Review credentials
- Check network connectivity

### Getting Help

- **Documentation**: [Full docs](../index.md)
- **Discord**: [Community support](https://discord.gg/37XJPXfz2w)
- **GitHub**: [Report issues](https://github.com/lfnovo/open-notebook/issues)

---

## 📋 Checklist Summary

Print this summary and check off as you complete each section:

- [ ] Security configured (authentication, HTTPS, firewall)
- [ ] Environment variables set correctly
- [ ] Resources allocated appropriately
- [ ] Monitoring and alerts configured
- [ ] Backup strategy implemented
- [ ] Maintenance procedures documented
- [ ] All features tested
- [ ] Users notified and trained
- [ ] Rollback plan ready
- [ ] Post-launch monitoring active

---

**Ready for production?** If you've completed this checklist, your Open Notebook deployment should be secure, performant, and ready for your team!

**Questions?** Join our [Discord community](https://discord.gg/37XJPXfz2w) for help from the team and other users.
