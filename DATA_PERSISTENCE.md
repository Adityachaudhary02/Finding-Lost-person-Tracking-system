# Data Persistence & Backup Guide

## Understanding Data Deletion

Your data should **NOT be deleted** when you shut down your laptop. Here's what you need to know:

### 1. **MySQL Database (Primary Storage)**
- All case data is stored in MySQL database: `findthem_db`
- Data persists on disk even when your laptop is shut down
- Database files are stored in: `C:\ProgramData\MySQL\MySQL Server 8.0\Data\findthem_db\`

### 2. **Upload Folder (Image Storage)**
- All uploaded images are stored in: `backend/uploads/`
- These are regular files on disk and persist when you shut down

### 3. **Automatic Backups**
- System automatically backs up all cases every time you start the backend
- Backups are saved in: `backend/database_backups/backup_YYYYMMDD_HHMMSS.json`
- Each backup is a JSON file containing all case data

---

## If Data Gets Deleted

If you find that your data is missing after shutting down your laptop:

### Option 1: Restore from Automatic Backup
```bash
cd backend
python backup.py restore
```

### Option 2: Restore from a Specific Backup
```bash
cd backend
python backup.py list              # See all backups
python backup.py restore backup_20260122_191902.json
```

### Option 3: Use Admin Panel
1. Open your website
2. Go to Admin Panel
3. Use the "Restore Database" section (with admin password)

---

## How to Ensure Data Persistence

### 1. **Always Stop Server Gracefully**
```bash
# Press Ctrl+C in the terminal running the backend
# OR use the admin endpoint to properly close connections
```

### 2. **Regular Manual Backups**
```bash
# Create a backup anytime
cd backend
python backup.py backup
```

### 3. **Check MySQL Service**
```powershell
# Verify MySQL is running
Get-Service MySQL80 | Format-Table Status

# If it's not running, start it
Start-Service MySQL80
```

### 4. **Enable Auto-Start for MySQL**
```powershell
# MySQL will auto-start when Windows starts
Set-Service -Name MySQL80 -StartupType Automatic
```

---

## Troubleshooting

### Problem: "Cannot connect to database" error
**Solution:**
```powershell
# Start MySQL service
Start-Service MySQL80

# Then restart the backend
cd backend
python main.py
```

### Problem: "Data disappeared after restart"
**Solution 1: Check if MySQL is running**
```powershell
Get-Service MySQL80
```

**Solution 2: Restore from backup**
```bash
cd backend
python backup.py restore
```

**Solution 3: Verify data exists**
```bash
cd backend
python check_db.py  # Created earlier
```

### Problem: "Backup files not found"
**Solution:**
```bash
cd backend
python backup.py list
```

---

## Backup File Location

All backups are automatically saved in:
```
Findthem2/backend/database_backups/
```

Example structure:
```
database_backups/
├── backup_20260122_191902.json  (auto-backup on startup)
├── backup_20260122_192145.json  (manual backup)
└── backup_20260122_195034.json  (auto-backup on next startup)
```

---

## REST API Backup Endpoints

### Create a Backup
```bash
curl -X POST http://localhost:8000/api/backup \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "admin_password=admin123"
```

### List Available Backups
```bash
curl "http://localhost:8000/api/backups?admin_password=admin123"
```

### Restore from Backup
```bash
curl -X POST http://localhost:8000/api/restore \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "backup_filename=backup_20260122_191902.json&admin_password=admin123"
```

---

## Important Notes

1. **Uploaded Images**: Make sure the `backend/uploads/` folder is backed up separately if needed
2. **Database Configuration**: Don't change the admin password without updating `config.py`
3. **MySQL Credentials**: Keep `config.py` credentials secure
4. **Regular Backups**: Create manual backups before making major changes

---

## Data Location Summary

| Data Type | Location | Persistence |
|-----------|----------|-------------|
| Case Information | MySQL Database | Persistent (disk) |
| Embeddings | MySQL Database | Persistent (disk) |
| Uploaded Images | `backend/uploads/` | Persistent (disk) |
| Backups | `backend/database_backups/` | Persistent (disk) |

All data is stored on disk and should survive laptop shutdowns if MySQL is properly configured.
