# StickyTux - OpenShift S2I Configuration

This directory contains OpenShift Source-to-Image (S2I) configurations for the StickyTux collaborative whiteboard application.

## Project Structure

- **Backend**: Django REST API with WebSocket support
- **Frontend**: Vue.js single-page application
- **Database**: SQLite (configurable to PostgreSQL/MySQL)
- **Cache/Sessions**: Redis for WebSocket channels

## S2I Configuration Files

### Root Level (.s2i/)
- `environment` - Environment variables for backend build
- `bin/assemble` - Backend build script
- `bin/run` - Backend runtime script

### Frontend Level (frontend/.s2i/)
- `environment` - Environment variables for frontend build
- `bin/assemble` - Frontend build script
- `bin/run` - Frontend runtime script

## OpenShift Resources

### Build Configuration
- `backend-buildconfig.yaml` - S2I build for Django backend
- `frontend-buildconfig.yaml` - S2I build for Vue.js frontend
- `imagestreams.yaml` - Image stream definitions

### Storage
- `pvc.yaml` - Persistent Volume Claims for database and media files

### Deployment Resources
- `deployments.yaml` - Deployment configurations for both components
- `services.yaml` - Service definitions
- `routes.yaml` - Route configurations with TLS
- `secrets.yaml` - Secret management template
- `configmap.yaml` - Configuration data

### Utilities
- `deploy.sh` - Automated deployment script with storage class selection
- `cleanup.sh` - Complete cleanup script with data protection

## Deployment Instructions

### Prerequisites
1. OpenShift cluster access
2. `oc` CLI tool configured
3. Project/namespace created

### Quick Deploy
```bash
# Create a new project
oc new-project stickytux

# Apply all configurations
oc apply -f openshift/

# Start builds
oc start-build stickytux-backend-build
oc start-build stickytux-frontend-build
```

### Step-by-Step Deployment

1. **Create ImageStreams**:
   ```bash
   oc apply -f openshift/imagestreams.yaml
   ```

2. **Configure Secrets** (edit values first):
   ```bash
   oc apply -f openshift/secrets.yaml
   ```

3. **Create Persistent Volume Claims**:
   ```bash
   # For default storage class
   oc apply -f openshift/pvc.yaml
   
   # Or specify a storage class
   sed 's/# storageClassName will be set by deployment script/storageClassName: your-storage-class/' openshift/pvc.yaml | oc apply -f -
   ```

4. **Create BuildConfigs**:
   ```bash
   oc apply -f openshift/backend-buildconfig.yaml
   oc apply -f openshift/frontend-buildconfig.yaml
   ```

5. **Start Builds**:
   ```bash
   oc start-build stickytux-backend-build
   oc start-build stickytux-frontend-build
   ```

6. **Deploy Applications**:
   ```bash
   oc apply -f openshift/configmap.yaml
   oc apply -f openshift/deployments.yaml
   oc apply -f openshift/services.yaml
   oc apply -f openshift/routes.yaml
   ```

### Configuration Notes

#### Backend Configuration
- **Base Image**: `python:3.11-ubi9`
- **Port**: 8080
- **WSGI Server**: Gunicorn
- **Workers**: 4 (configurable via WEB_CONCURRENCY)

#### Frontend Configuration
- **Base Image**: `nodejs:20-ubi9`
- **Build**: Production Vue.js build
- **Serve**: Python HTTP server for static files
- **Port**: 8080

#### Environment Variables

**Backend**:
- `DJANGO_SETTINGS_MODULE=backend.settings`
- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - Django secret key
- `REDIS_URL` - Redis connection for WebSockets
- `WEB_CONCURRENCY` - Number of Gunicorn workers

**Frontend**:
- `NODE_ENV=production`

### Security Considerations

1. **Update Secrets**: Replace placeholder values in `secrets.yaml`
2. **TLS**: Routes are configured with TLS termination
3. **Resource Limits**: CPU and memory limits are set
4. **Health Checks**: Liveness and readiness probes configured

### Scaling

The deployment supports horizontal scaling:

```bash
# Scale backend
oc scale deployment stickytux-backend --replicas=3

# Scale frontend
oc scale deployment stickytux-frontend --replicas=2
```

### Monitoring

Health check endpoints:
- Backend: `GET /api/health/`
- Frontend: `GET /` (static files)

### Database Migration

For production deployments with external databases:

1. Update `DATABASE_URL` in secrets
2. Run migrations manually:
   ```bash
   oc exec deployment/stickytux-backend -- python manage.py migrate
   ```

### WebSocket Support

For WebSocket functionality in production:
1. Configure Redis connection via `REDIS_URL`
2. Ensure WebSocket traffic is properly routed
3. Consider using sticky sessions for multi-replica deployments

### Cleanup

To completely remove the deployment:
```bash
./openshift/cleanup.sh
```

This script will:
1. Remove all StickyTux deployments and services
2. Remove build configurations and images
3. Ask for confirmation before deleting persistent data
4. Provide option to preserve or delete PVCs

For manual cleanup:
```bash
# Remove everything except persistent data
oc delete all -l app=stickytux

# Remove secrets and config maps
oc delete secret,configmap -l app=stickytux

# Optionally remove persistent data (WARNING: irreversible)
oc delete pvc stickytux-database-pvc stickytux-media-pvc
```

### Troubleshooting

#### Check Build Logs
```bash
oc logs -f bc/stickytux-backend-build
oc logs -f bc/stickytux-frontend-build
```

#### Check Pod Logs
```bash
oc logs -f deployment/stickytux-backend
oc logs -f deployment/stickytux-frontend
```

#### Debug Pod Issues
```bash
oc describe pod -l app=stickytux
oc get events --sort-by=.metadata.creationTimestamp
```

### Customization

#### Storage Configuration
The deployment uses persistent volumes for:
- **Database Storage** (5Gi): SQLite database file in `/app/data/`
- **Media Storage** (10Gi): User uploaded images and files in `/app/media/`

To use a specific storage class:
```bash
# Interactive deployment (asks for storage class)
./openshift/deploy.sh

# Manual configuration
sed -i 's/# storageClassName will be set by deployment script/storageClassName: fast-ssd/' openshift/pvc.yaml
```

Available storage classes can be listed with:
```bash
oc get storageclass
```

#### Build Triggers
- **Git Webhooks**: Configured for automatic builds on code changes
- **Image Changes**: Rebuilds triggered by base image updates
- **Manual**: Use `oc start-build` command

#### Resource Adjustments
Modify CPU and memory limits in `deployments.yaml` based on your requirements.

#### Storage
For persistent storage, the deployment includes:
- Database data persistence via PVC
- Media files persistence via PVC  
- Configurable storage classes via deployment script