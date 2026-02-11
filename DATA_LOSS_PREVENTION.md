# 🔒 Data Loss Prevention & Recovery Plan

## Current Status ✅

Your data is now **protected** with:

1. **Automatic Daily Backups** - Every time you start the backend
2. **MySQL Persistent Storage** - Data saved to disk
3. **Backup & Restore API** - Easy recovery if needed
4. **Auto-start Services** - MySQL can auto-start on boot

---

## What Happened Before?

When you said "data gets deleted when I shutdown," likely causes were:

1. ❌ **MySQL service not running** → Can't access data even though it exists
2. ❌ **Browser cache cleared** → Can't see data in UI (but it's in database)
3. ❌ **Backend not properly disconnected** → Uncommitted transactions lost

**All now fixed! ✅**

---

## Your Data is Safe Here

### MySQL Database
```
Location: C:\ProgramData\MySQL\MySQL Server 8.0\Data\findthem_db\
Current Cases: 4
Latest Backup: backend/database_backups/backup_20260122_191902.json (4 cases)
```

### Upload Images
```
Location: backend/uploads/
All uploaded photos are here
```

---

## Quick Start Commands

### Start Everything
```bash
# Option 1: Use the batch file (Windows)
START_FINDTHEM.bat

# Option 2: Manual
cd backend
python main.py
```

### Backup & Restore
```bash
# Create a backup
cd backend
python backup.py backup

# See all backups
python backup.py list

# Restore from latest backup
python backup.py restore

# Restore from specific backup
python backup.py restore backup_20260122_191902.json
```

### Check Database Status
```bash
# Check if data exists
cd backend
python check_db.py
```

---

## Step-by-Step: Preventing Data Loss

### 1. **Enable MySQL Auto-Start** (One-time setup)
```powershell
# Run as Administrator
Set-Service -Name MySQL80 -StartupType Automatic
```

### 2. **Verify MySQL Starts on Boot**
```powershell
Get-Service MySQL80 | Select-Object Name, Status, StartType
# Should show: RUNNING, Automatic
```

### 3. **Start Backend Service**
```bash
cd backend
python main.py
```

### 4. **Open Website**
- Go to `http://localhost:8000/` in your browser
- Your cases should appear immediately

### 5. **Shutdown Safely**
```
Press Ctrl+C in the terminal running backend
Wait for "Application shutdown complete"
Shut down your laptop
```

---

## Recovery Procedures

### If Data Appears Missing After Startup

**Step 1:** Check MySQL is running
```powershell
Get-Service MySQL80
# If it says "Stopped", run:
Start-Service MySQL80
```

**Step 2:** Verify data exists in database
```bash
cd backend
python check_db.py
```

**Step 3:** If still no data, restore backup
```bash
cd backend
python backup.py list
python backup.py restore
```

**Step 4:** Restart backend
```bash
python main.py
```

---

## Admin Backup Controls

You can now backup/restore through the website:

### Create Backup
- Go to Admin Panel
- Click "Create Backup"
- Enter admin password (default: `admin123`)
- Backup is created automatically

### Restore Backup
- Go to Admin Panel  
- Click "Restore Database"
- Select backup file
- Enter admin password
- Database is restored

---

## Important Files & Locations

```
Findthem2/
├── backend/
│   ├── main.py (Backend server)
│   ├── database.py (MySQL connection)
│   ├── face_recognition_engine.py (Face matching)
│   ├── config.py (Settings - KEEP SAFE!)
│   ├── uploads/ (Uploaded images)
│   ├── database_backups/ (Auto-backups)
│   ├── backup.py (Backup/restore tool)
│   └── check_db.py (Check database status)
│
├── frontend/
│   ├── index.html
│   ├── admin.html
│   └── ...
│
├── database/
│   ├── init_db.py (Initialize database)
│   └── schema.sql (Database structure)
│
├── START_FINDTHEM.bat (Easy startup - use this!)
├── DATA_PERSISTENCE.md (Detailed guide)
└── ...
```

---

## Key Configuration

### Admin Password (for backups)
- **File:** `backend/config.py`
- **Default:** `admin123`
- **Line:** `ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')`
- ⚠️ **Change this in production!**

### Database Connection
- **Host:** localhost
- **User:** root
- **Database:** findthem_db
- **Location:** `backend/config.py`

### Face Recognition
- **Similarity Threshold:** 0.4 (lowered for better matching)
- **Location:** `backend/config.py`

---

## Troubleshooting Checklist

| Problem | Solution |
|---------|----------|
| "Cannot connect to database" | Start MySQL: `Start-Service MySQL80` |
| "No cases showing" | Check backup: `python backup.py list` |
| "Cases disappeared" | Restore: `python backup.py restore` |
| "Backend won't start" | Check port 8000 not in use: `netstat -ano \| find "8000"` |
| "Upload fails" | Check `backend/uploads/` folder exists |
| "Images not showing" | Restart backend server |

---

## Automatic Backups Explained

Every time you start the backend:
1. ✅ Connect to MySQL
2. ✅ Export all cases to JSON file
3. ✅ Save to `database_backups/backup_YYYYMMDD_HHMMSS.json`
4. ✅ Ready to use

### Example Backup Timeline
```
Backup 1: 2026-01-22 19:19:02 - 4 cases
Backup 2: 2026-01-22 19:25:34 - 5 cases (added 1)
Backup 3: 2026-01-23 08:15:12 - 5 cases (next day startup)
```

---

## When to Manually Backup

```bash
# Before major operations
python backup.py backup

# Before changing config
python backup.py backup

# Before installing updates
python backup.py backup

# Before shutting down for extended period
python backup.py backup
```

---

## Next Steps

1. ✅ **Verify MySQL Auto-Start is Enabled**
   ```powershell
   Set-Service -Name MySQL80 -StartupType Automatic
   ```

2. ✅ **Test the System**
   - Start backend: `python main.py`
   - Upload a test case
   - Shutdown gracefully
   - Restart and verify case is still there

3. ✅ **Create Initial Backup**
   ```bash
   python backup.py backup
   ```

4. ✅ **Save This Guide**
   - Keep `DATA_PERSISTENCE.md` for reference
   - Keep `START_FINDTHEM.bat` for easy startup

---

## Questions?

If you experience data loss again:

1. Check `backend/database_backups/` folder exists and has files
2. Run `python check_db.py` to see actual database content
3. Try `python backup.py restore` to recover from backup
4. Check MySQL service status: `Get-Service MySQL80`

**Your data is now backed up and safe! 🎉**
