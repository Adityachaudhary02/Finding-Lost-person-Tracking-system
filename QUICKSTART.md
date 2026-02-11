# Quick Start Guide

Get FindThem up and running in 5 minutes!

## Windows Quick Start

### 1. Install MySQL
If you don't have MySQL installed:
- Download from https://dev.mysql.com/downloads/mysql/
- Install with default settings
- Note your password (or leave blank if no password set)

### 2. Initialize Database

Open PowerShell in the project root:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install mysql-connector-python python-dotenv
cd ..\database
python init_db.py
```

### 3. Install Backend Dependencies

```powershell
cd ..\backend
pip install -r requirements.txt
```

This will take 5-10 minutes on first installation (downloading face recognition models).

### 4. Create .env File

```powershell
copy .env.example .env
notepad .env
```

Update with your MySQL credentials:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
```

### 5. Start Backend

```powershell
cd backend
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 6. Start Frontend (New PowerShell Window)

```powershell
cd frontend
python -m http.server 8080
```

### 7. Access the Application

- **Main Website**: http://localhost:8080
- **Admin Panel**: http://localhost:8080/admin.html
- **API Documentation**: http://localhost:8000/docs

## Testing the Application

### Test Case Upload

1. Go to http://localhost:8080
2. Click "Report Missing Person"
3. Fill in the form:
   - Name: Test Person
   - Status: Missing Person
   - Description: Test case
   - Contact: test@example.com
   - Upload a clear face image (JPG/PNG)
4. Click "Submit Report"

### Test Search

1. Go to "Search" section
2. Upload a similar or same face image
3. Click "Search"
4. View matching results with similarity scores

## Troubleshooting

### MySQL Connection Error
```
Error while connecting to MySQL: [Errno 2003]
```
Solution: Ensure MySQL service is running
```powershell
# Check if MySQL is running
Get-Service MySQL*

# Or start MySQL Server
net start MySQL80
```

### Port Already in Use
```
Address already in use
```
Solution: Use different ports
```powershell
# Backend (different port)
python main.py  # Change port in main.py

# Frontend (different port)
python -m http.server 8081
```

### Module Not Found Errors
```
ModuleNotFoundError: No module named 'deepface'
```
Solution: Reinstall dependencies
```powershell
pip install --upgrade --force-reinstall -r requirements.txt
```

### Face Detection Issues
- Ensure image is clear and shows a visible face
- Minimum resolution: 100x100 pixels
- Best results: frontal face view

## Development Workflow

### Making Changes

1. Backend changes: Stop server, modify file, restart
2. Frontend changes: Refresh browser (changes auto-apply)
3. Database changes: Run migration scripts

### Adding New Endpoints

Edit `backend/main.py`:

```python
@app.post("/api/my-endpoint")
async def my_endpoint(param: str):
    return {"message": "Success"}
```

### Styling Changes

Edit `frontend/styles.css` or `frontend/admin-styles.css`

### Adding Database Fields

1. Edit `database/schema.sql`
2. Run migration: `python database/init_db.py`
3. Update models in `backend/database.py`

## Performance Tips

1. **Optimize Images**: Compress images before upload
2. **Database Indexing**: Already configured for fast queries
3. **Caching**: Results are calculated fresh each search
4. **Concurrency**: Backend handles multiple simultaneous requests

## Common Tasks

### View Database

```powershell
mysql -u root -p
use findthem_db;
select * from cases;
```

### Clear All Cases

```sql
TRUNCATE TABLE cases;
TRUNCATE TABLE search_history;
```

### Export Data

```sql
SELECT * FROM cases INTO OUTFILE 'export.csv' FIELDS TERMINATED BY ',';
```

### Check API Health

Open browser: http://localhost:8000/health

## Next Steps

1. ✅ Get the basic setup running
2. 📸 Upload some test cases
3. 🔍 Test the search functionality
4. ⚙️ Explore the admin panel
5. 🚀 Deploy to production

## Production Deployment

For production use:

1. Use a proper web server (Nginx, Apache)
2. Configure HTTPS/SSL
3. Use managed database service
4. Implement authentication
5. Set up monitoring and logging
6. Use environment variables for secrets
7. Enable database backups
8. Implement rate limiting

See README.md for detailed deployment instructions.

## Support Resources

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **README**: See README.md for comprehensive documentation
- **Issues**: Check console logs for error messages

## Contact

Questions or issues? Refer to the README.md file for troubleshooting section.

---

**Pro Tip**: Keep both backend and frontend running during development. Use separate PowerShell windows for easier management.
