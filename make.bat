@echo off

IF "%1"=="run" GOTO run
IF "%1"=="reindex" GOTO reindex
IF "%1"=="eval" GOTO eval
IF "%1"=="frontend" GOTO frontend

echo Usage:
echo   make.bat run       - Start backend server
echo   make.bat reindex   - Re-index all documents
echo   make.bat eval      - Run evaluation metrics
echo   make.bat frontend  - Start frontend
GOTO end

:run
echo Starting backend...
call venv\Scripts\activate.bat
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
GOTO end

:reindex
echo Re-indexing documents...
call venv\Scripts\activate.bat
cd backend
python -m core.pipeline index
GOTO end

:eval
echo Running evaluation...
call venv\Scripts\activate.bat
cd backend
python -m core.eval
GOTO end

:frontend
echo Starting frontend...
cd frontend
npm run dev
GOTO end

:end