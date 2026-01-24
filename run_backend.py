"""
Simple Backend Launcher
Run from project root with: backend/venv/Scripts/python.exe run_backend.py
"""
import sys
import os

# Add project directories to path
project_root = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(project_root, 'backend')
ai_dir = os.path.join(project_root, 'ai')

sys.path.insert(0, project_root)
sys.path.insert(0, backend_dir)
sys.path.insert(0, ai_dir)

# Change to backend directory
os.chdir(backend_dir)

# Now import and run
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting IntelliDesk AI Backend...")
    print(f"📁 Backend directory: {backend_dir}")
    print(f"🐍 Python: {sys.executable}")
    print(f"📊 API will be available at: http://localhost:8000")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print("")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
