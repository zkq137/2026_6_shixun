# Backend

AI智能商城后端服务，基于 FastAPI 构建。

## 本地启动

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

健康检查：

```text
http://localhost:8000/health
```

数据库检查：

```text
http://localhost:8000/health/db
```

## Database setup

Initialize tables and demo data:

```powershell
.\.venv\Scripts\python.exe scripts\init_db.py
```

Check database status:

```powershell
.\.venv\Scripts\python.exe scripts\check_db.py
```
