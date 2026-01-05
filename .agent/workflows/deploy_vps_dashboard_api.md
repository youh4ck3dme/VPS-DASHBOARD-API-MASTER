---
description: Deploy VPS Dashboard API to remote server
---

# Deployment Workflow for VPS-DASHBOARD-API-MASTER

This workflow automates the process of building and deploying the **VPS Dashboard API** project to a remote VPS.

## Prerequisites

- SSH access to the target VPS (`ssh-keygen` and add the public key to `~/.ssh/authorized_keys`).
- `rsync` installed locally (`brew install rsync`).
- Python 3.11+ and `pip` available.
- Node.js (LTS) and `pnpm` installed for the frontend.
- Environment variables for the remote server defined in a `.env` file at the project root:

  ```bash
  REMOTE_USER=youh4ck3dme
  REMOTE_HOST=vps.example.com
  REMOTE_PATH=/var/www/vps-dashboard-api
  ```

## Steps

1. **Install backend dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Run backend test suite**

   ```bash
   pytest
   ```

3. **Build the frontend**

   ```bash
   cd frontend && pnpm install && pnpm build
   ```

4. **Package the backend** (optional – creates a tarball for transfer)

   ```bash
   tar -czf backend.tar.gz core requirements.txt
   ```

5. **Synchronize files to the VPS**

   ```bash
   rsync -avz --exclude='.git/' --exclude='node_modules/' \
     . $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH
   ```

6. **Restart services on the VPS**

   ```bash
   ssh $REMOTE_USER@$REMOTE_HOST "\
     cd $REMOTE_PATH && \
     sudo systemctl restart vps-dashboard-api && \
     sudo systemctl restart vps-dashboard-frontend\
   "
   ```

---

## Notes

- Adjust `REMOTE_PATH` to match the directory where the API should live.
- If you use a process manager other than `systemd`, replace the `systemctl` commands accordingly.
- The workflow can be executed manually by copying each block into a terminal, or automated with a CI/CD pipeline.
