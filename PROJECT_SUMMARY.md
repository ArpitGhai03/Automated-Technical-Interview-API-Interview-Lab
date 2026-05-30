# Interview Lab - Complete Project Summary

## Project Overview
**Interview Lab** is an **Online Code Submission & Execution Platform** where users can write code, submit it for execution, and see test results and output in real-time.

**Tech Stack:**
- Backend: FastAPI (Python)
- Frontend: React + TypeScript + Vite
- Database: PostgreSQL
- ORM: SQLAlchemy

---
  
## 1. DATABASE (PostgreSQL)

### Connection Details
- **Host**: localhost
- **Port**: 5432
- **Username**: postgres
- **Password**: Arpit_123
- **Database**: code_db

### Database Schema

#### Table: `submissions`
```sql
CREATE TABLE submissions (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    code TEXT NOT NULL,
    language VARCHAR(20),
    status VARCHAR(20) DEFAULT 'pending',
    output TEXT,
    runtime FLOAT,
    test_passed INTEGER,
    test_total INTEGER,
    test_results JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Column Meanings:**
- `id`: Unique submission identifier
- `code`: The actual code submitted by user
- `language`: Programming language (e.g., 'python')
- `status`: Execution status ('pending', 'running', 'completed', 'error')
- `output`: Console output or error message from code execution
- `runtime`: Execution time in seconds
- `test_passed`: Number of tests passed
- `test_total`: Total number of tests
- `test_results`: JSON array of individual test results (booleans: `[true, false, true]`)
- `created_at`: Timestamp when submission was created

---

## 2. BACKEND (FastAPI)

### Location
- Main file: `app.py`
- Dependencies: `requirements.txt` with FastAPI, Uvicorn, SQLAlchemy, Pydantic, psycopg2-binary
- Running on: **http://localhost:8000**

### Key Files

#### `app.py` - Main Application
**Imports:**
- FastAPI for API framework
- CORS middleware for frontend communication
- SQLAlchemy for database
- subprocess for code execution

**Key Features:**
1. **CORS Middleware**: Allows frontend (http://localhost:5173) to communicate with backend
2. **Database Initialization**: Creates tables on startup
3. **Code Execution Engine**: Runs Python code in subprocess with 10-second timeout

#### `models.py` - Database Schema
Defines the `Submission` SQLAlchemy model:
```python
class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True)
    code = Column(Text, nullable=False)
    language = Column(String(20))
    status = Column(String(20), default="pending")
    output = Column(Text)
    runtime = Column(Float, nullable=True)
    test_passed = Column(Integer, nullable=True)
    test_total = Column(Integer, nullable=True)
    test_results = Column(JSON, nullable=True)  # Array of booleans
    created_at = Column(TIMESTAMP, server_default=func.now())
```

#### `crud.py` - Database Operations
Three main CRUD functions:
1. **create_submission(db, submission)**: Store new code submission in DB
2. **update_submission(db, submission, status, output)**: Update status and output after execution
3. **get_submission(db, submission_id)**: Retrieve a submission by ID

#### `schemas.py` - Request/Response Models (Pydantic)
- **SubmissionCreate**: Input model (code + language)
- **SubmissionResponse**: Output model (includes id, status, output, timestamps)

#### `database.py` - Database Connection
- Establishes PostgreSQL connection using SQLAlchemy
- Creates SessionLocal for DB operations
- Creates declarative base for ORM models

#### `init_db.py` - Database Initialization
Script to create database tables. Run once after setup:
```bash
python init_db.py
```

### API Endpoints

#### 1. **GET /** - Health Check
```
URL: http://localhost:8000/
Response: {"status": "healthy"}
Purpose: Verify backend is running
```

#### 2. **POST /submit** - Submit Code
```
URL: http://localhost:8000/submit (proxied via Vite to /submit)
Request Body: {
    "code": "def twoSum(nums, target): ...",
    "language": "python"
}
Response: {
    "id": 1,
    "code": "def twoSum(nums, target): ...",
    "language": "python",
    "status": "completed",
    "output": "Test Results:\nTest 1: PASSED\nTest 2: PASSED\nTest 3: PASSED",
    "runtime": 0.047,
    "test_passed": 3,
    "test_total": 3,
    "test_results": [true, true, true],
    "created_at": "2026-05-30T12:43:30"
}
```

**Flow:**
1. Receives code submission from frontend (via Vite proxy)
2. Stores in database with status "pending"
3. Executes code in Docker container or subprocess
4. Runs test cases against user code
5. Captures stdout, stderr, and test results
6. Updates database with results, runtime, and individual test results
7. Returns response to frontend

#### 3. **GET /submissions/{submission_id}** - Fetch Results
```
URL: http://localhost:8000/submissions/1
Response: Same as above submission response
Purpose: Retrieve execution results later
```

### Code Execution
- **Primary**: Docker container execution for maximum security (optional)
- **Fallback**: Subprocess execution when Docker unavailable
- **Function**: `execute_python_code(code: str)` orchestrates both methods
- **Timeout**: 10 seconds per execution (prevents infinite loops)
- **Test Cases**: Automatically runs against user function:
  - **Test 1**: `two_sum([2, 7, 11, 15], 9)` → expects `[0, 1]`
  - **Test 2**: `two_sum([3, 2, 4], 6)` → expects `[1, 2]`
  - **Test 3**: `two_sum([3, 3], 6)` → expects `[0, 1]`
- **Function Names**: Supports both `two_sum` and `twoSum` naming conventions
- **Returns**: 
  - Status: "completed" or "error"
  - Output: stdout if successful
  - Error: stderr if failed
  - Runtime: execution time in seconds
  - Test results: array of booleans for each test case

---

## 3. FRONTEND (React + TypeScript)

### Location
- Folder: `frontend/`
- Running on: **http://localhost:5173**
- Build tool: Vite

### Project Structure
```
frontend/
├── src/
│   ├── App.tsx              # Main app component
│   ├── api.ts               # API communication
│   ├── types.ts             # TypeScript interfaces
│   ├── styles.css           # Global styles
│   ├── main.tsx             # Entry point
│   └── components/
│       ├── Toolbar.tsx      # Header with language selector & Run button
│       ├── ProblemPrompt.tsx # Problem description display
│       ├── Editor.tsx       # Code editor using Monaco
│       ├── TestResults.tsx  # Test results panel
│       ├── ErrorPanel.tsx   # Error display
│       └── OutputPanel.tsx  # Output display (NEW - ADDED BY ME)
├── package.json
├── vite.config.ts
└── tsconfig.json
```

### Key Components

#### 1. **Toolbar.tsx**
- **Purpose**: Header section with controls
- **Features**:
  - Language selector (dropdown) - currently shows "Python"
  - Run button (▶ Run) - triggers code submission
  - Loading state feedback

#### 2. **ProblemPrompt.tsx**
- **Purpose**: Display the coding challenge/problem statement
- **Content**: "Two Sum" problem description
- **Shows**: Problem title and requirements

#### 3. **Editor.tsx**
- **Purpose**: Code input area
- **Details**: Uses Monaco Editor (VS Code editor)
- **Supports**: Syntax highlighting, line numbers, code formatting
- **State**: Controlled by parent component (App.tsx)

#### 4. **TestResults.tsx** (ENHANCED)
- **Purpose**: Show individual test pass/fail results
- **Shows**: 
  - ✓ for each passing test case
  - ✗ for each failing test case
  - Test description and call signature
  - Summary: "X/3 tests passed"
- **Loading State**: "Running…" while code executes
- **Data Source**: `submission.test_results` array of booleans

#### 5. **ErrorPanel.tsx** (EXISTING)
- **Purpose**: Display execution errors
- **Shows**: Error messages from code execution
- **Default**: "No errors" if code runs successfully

#### 6. **OutputPanel.tsx** (NEW - I ADDED THIS)
- **Purpose**: Display console output from code execution
- **Shows**: 
  - Print statements output
  - Function return values
  - Console logs
- **Loading State**: "Running…" while executing
- **Error Display**: Red-colored error output if code fails
- **Default**: "Run your code to see output" initially

### Types (`types.ts`)
```typescript
type SubmissionStatus = "pending" | "running" | "completed" | "error"

interface SubmissionRequest {
    code: string
    language: string
}

interface SubmissionResponse {
    id: number
    code: string
    language: string
    status: SubmissionStatus
    output: string | null
    runtime: number | null
    test_passed: number | null
    test_total: number | null
    test_results: boolean[] | null
    created_at: string
}
```

### API Communication (`api.ts`)
```typescript
async submitCode(submission: SubmissionRequest): Promise<SubmissionResponse>
```
- Sends POST request to `/submit` (proxied through Vite dev server)
- Receives submission response with test results
- Handles errors and network issues
- API URL defaults to empty string (uses Vite proxy configuration)

### Vite Proxy Configuration (`vite.config.ts`)
```typescript
server: {
  port: 5173,
  proxy: {
    "/submit": {
      target: "http://localhost:8000",
      changeOrigin: true,
    },
    "/submissions": {
      target: "http://localhost:8000",
      changeOrigin: true,
    },
  },
}
```
- Eliminates CORS issues during development
- Routes `/submit` and `/submissions` requests through Vite to backend
- Request goes: frontend → Vite dev server → backend (localhost:8000)

### Main App Flow (`App.tsx`)
1. User enters code in editor
2. User clicks "Run" button
3. Code sent to backend via API
4. Backend executes code
5. Results returned to frontend
6. All 3 panels update:
   - Test Results panel
   - Output panel (NEW)
   - Error panel
7. User sees output immediately

### Styling (`styles.css`)
- **Color Scheme**: Dark theme (VS Code style)
- **Layout**: 
  - Header (toolbar)
  - Problem prompt section
  - Main workspace grid:
    - Left: Editor (70%)
    - Right: 3 panels (30%)
      - Test Results (1/3)
      - Output (1/3) - NEW
      - Errors (1/3)
- **Key Colors**:
  - Background: #1e1e1e (dark)
  - Text: #d4d4d4 (light gray)
  - Pass: #4ec9b0 (green)
  - Fail: #f48771 (red)
  - Accent: #007acc (blue)

---

## 4. LATEST ENHANCEMENTS (Session 2)

### Major Fixes & Features Added

#### 1. CORS Issue Resolution ✅
- **Problem**: "Access to fetch has been blocked by CORS policy" error
- **Root Cause**: Frontend and backend on different origins during development
- **Solution**: Added Vite proxy configuration
  - Routes `/submit` and `/submissions` through Vite dev server
  - Eliminates cross-origin requests during development
  - No need for overly permissive CORS middleware

#### 2. Function Name Flexibility ✅
- **Problem**: Tests only looked for `two_sum` (snake_case)
- **Solution**: Updated `run_test_cases()` to accept both:
  - `two_sum` (Python convention)
  - `twoSum` (JavaScript/camelCase convention)
- **Impact**: Users can write functions in their preferred style

#### 3. Schema Migration ✅
- **Problem**: New `test_results` column didn't exist in existing database
- **Solution**: Enhanced `init_db.py` with automatic schema migration
  - Detects missing columns
  - Adds `test_results JSON` column if missing
  - Runs on startup without manual SQL

#### 4. Test Results Tracking ✅
- **Added**: Individual test result tracking
  - Backend: Returns `test_results: [true, false, true]` array
  - Database: Stores as JSON in `test_results` column
  - Frontend: Displays pass/fail for each test case
- **Display**: "Test 1: PASSED", "Test 2: FAILED", etc.

#### 5. Enhanced Error Handling ✅
- **Added**: Try-catch wrapper in `/submit` endpoint
- **Benefit**: Shows actual error messages instead of generic 500 error
- **Debug Output**: Traceback included for development

### Files Created/Modified

#### Created
- `frontend/src/components/OutputPanel.tsx` (NEW - displays execution output)

#### Modified
- `frontend/vite.config.ts` - Added proxy configuration for backend routes
- `frontend/src/api.ts` - Changed API_URL default to empty string for proxy
- `app.py` - Enhanced error handling, added function name flexibility
- `init_db.py` - Added schema migration for missing columns
- `models.py` - Updated with test tracking fields
- `schemas.py` - Updated with test results fields
- `crud.py` - Updated to handle test results parameter

---

## 5. CURRENT WORKFLOW

### User Perspective
1. Visit http://localhost:5173
2. See code editor with "Two Sum" problem template
3. Write Python code with function `twoSum()` or `two_sum()` 
   - Takes `nums` (list of integers) and `target` (integer)
   - Should return list of two indices that sum to target
4. Click "▶ Run" button
5. See three panels update simultaneously:
   - **Test Results**: Individual pass/fail for each test case (✓ or ✗)
   - **Output**: Execution output and test summary
   - **Errors**: Any runtime errors
6. Summary shows: "X/3 tests passed" and runtime in milliseconds
7. Modify code and run again - all panels update in real-time

### Behind the Scenes (Complete Flow)
1. Frontend captures code from editor
2. Sends POST to `/submit` (proxied through Vite)
3. Vite dev server forwards to backend at localhost:8000
4. Backend validates request and stores in PostgreSQL
5. Code executed in Docker container (or subprocess fallback)
6. Backend runs 3 test cases against user function
7. Captures: output, errors, runtime, individual test results
8. Stores in database with all metadata
9. Returns response with test_results array: `[true, true, false]`
10. Frontend receives response and updates all 3 panels
11. User sees results: test status, runtime, individual pass/fail

---

## 6. FILES CHANGED/CREATED

### Created
- `frontend/src/components/OutputPanel.tsx` - Displays execution output
- `docker-compose.yml` - PostgreSQL container configuration
- `init_db.py` - Database initialization with schema migration
- `PROJECT_SUMMARY.md` - This comprehensive project documentation
- `README.md` - Quick start guide

### Modified (This Session)
- `frontend/vite.config.ts` - **Added proxy configuration for CORS fix**
- `frontend/src/api.ts` - **Updated API_URL to use proxy**
- `app.py` - **Enhanced error handling, function name flexibility**
- `init_db.py` - **Added schema migration for missing columns**

### Existing Core Files
- `app.py` - FastAPI backend with all endpoints
- `models.py` - SQLAlchemy Submission model
- `schemas.py` - Pydantic request/response validation
- `crud.py` - Database CRUD operations
- `database.py` - PostgreSQL connection setup
- `requirements.txt` - Python dependencies
- `Dockerfile` - Docker image for backend
- `frontend/src/App.tsx` - Main React component
- `frontend/src/styles.css` - VS Code-inspired dark theme
- `frontend/package.json` - Node dependencies

---

## 7. KEY TECHNICAL DETAILS

### Error Handling
- Subprocess timeout: 10 seconds (prevents infinite loops)
- Database connection pooling with SQLAlchemy
- CORS enabled for cross-origin requests
- Input validation with Pydantic schemas

### Security Considerations
- Code runs in isolated subprocess (not in main process)
- 10-second timeout prevents resource exhaustion
- Database queries use parameterized queries (SQLAlchemy ORM)
- Only Python code execution supported currently

### Future Enhancements (Possible)
- Support more languages (JavaScript, Java, etc.)
- Docker sandboxing for safer code execution
- User authentication and submission history
- Advanced test framework integration
- Real-time collaborative coding

---

## 8. HOW TO RUN

### Prerequisites
- Python 3.11+
- Node.js 18+ (npm)
- PostgreSQL running on localhost:5432

### Setup
```bash
# Terminal 1: Backend
cd d:\Sandbox_Project
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python init_db.py
uvicorn app:app --reload

# Terminal 2: Frontend
cd d:\Sandbox_Project\frontend
$env:Path += ";C:\Program Files\nodejs"
npm install
npm run dev
```

### Access
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 9. IMPORTANT URLS & PORTS

| Component | URL | Port | Status |
|-----------|-----|------|--------|
| Frontend | http://localhost:5173 | 5173 | Running |
| Backend | http://localhost:8000 | 8000 | Running |
| API Docs | http://localhost:8000/docs | 8000 | Available |
| Database | localhost | 5432 | Running |

---

## 10. DATABASE CONNECTION STRING
```
postgresql://postgres:Arpit_123@localhost:5432/code_db
```

---

## Summary Stats
- **Backend Routes**: 3 endpoints (GET /, POST /submit, GET /submissions/{id})
- **Frontend Components**: 6 (Toolbar, ProblemPrompt, Editor, TestResults, OutputPanel, ErrorPanel)
- **Database Tables**: 1 (submissions with 10 columns)
- **Test Cases**: 3 (Two Sum variations)
- **API Response Time**: ~50-150ms (typical) + code execution time
- **Max Code Execution**: 10 seconds (with timeout)
- **Supported Functions**: `two_sum()` or `twoSum()` (both conventions)
- **Code Editor**: Monaco Editor (same as VS Code)
- **UI Theme**: Dark mode (VS Code inspired)
- **Development Setup**: Vite dev server with proxy to backend
- **Production**: Docker + Docker Compose for isolated execution

