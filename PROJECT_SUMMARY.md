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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Column Meanings:**
- `id`: Unique submission identifier
- `code`: The actual code submitted by user
- `language`: Programming language (e.g., 'python')
- `status`: Execution status ('pending', 'running', 'completed', 'error')
- `output`: Console output or error message from code execution
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
URL: http://localhost:8000/submit
Request Body: {
    "code": "print('hello')",
    "language": "python"
}
Response: {
    "id": 1,
    "code": "print('hello')",
    "language": "python",
    "status": "completed",
    "output": "hello\n",
    "created_at": "2026-05-11T10:30:00"
}
```

**Flow:**
1. Receives code submission
2. Stores in database with status "pending"
3. Executes code in subprocess
4. Captures stdout and stderr
5. Updates database with results
6. Returns response to frontend

#### 3. **GET /submissions/{submission_id}** - Fetch Results
```
URL: http://localhost:8000/submissions/1
Response: Same as above submission response
Purpose: Retrieve execution results later
```

### Code Execution
- **Function**: `execute_python_code(code: str)`
- **Security**: Uses subprocess with timeout (10 seconds)
- **Returns**: 
  - Status: "completed" or "error"
  - Output: stdout if successful
  - Error: stderr if failed

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

#### 4. **TestResults.tsx** (EXISTING)
- **Purpose**: Show if test passed or failed
- **Shows**: Pass/fail status with ✓ or ✗ icon
- **Loading State**: "Running…" while code executes

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
    created_at: string
}
```

### API Communication (`api.ts`)
```typescript
async submitCode(submission: SubmissionRequest): Promise<SubmissionResponse>
```
- Sends POST request to `http://localhost:8000/submit`
- Receives submission response with results
- Handles errors and network issues

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

## 4. NEW ADDITIONS I MADE (Today)

### Added Components

#### OutputPanel.tsx
```typescript
interface OutputPanelProps {
    submission: SubmissionResponse | null
    loading: boolean
}

export function OutputPanel({ submission, loading }: OutputPanelProps)
```

**Features:**
- Shows execution output in real-time
- Handles loading state with "Running…" message
- Displays error output in red for failed executions
- Shows "(No output)" when execution completes with no console output
- Auto-scrollable content area
- Monospace font for code-like output

**States:**
1. **Before running**: "Run your code to see output"
2. **While running**: "Running…"
3. **After completion (success)**: Displays console output
4. **After completion (error)**: Displays error in red
5. **Empty output**: "(No output)"

### Modified Files

#### App.tsx
- **Added**: Import for OutputPanel component
- **Added**: OutputPanel between TestResults and ErrorPanel
- **Passes props**: submission, loading state

#### styles.css
- **Changed**: `grid-template-rows` from `1fr 1fr` to `1fr 1fr 1fr` (3 equal panels)
- **Added**: `.output-block.error` styling for error outputs
- **Ensures**: Equal space for all 3 right-side panels

---

## 5. CURRENT WORKFLOW

### User Perspective
1. Visit http://localhost:5173
2. See code editor with sample "Two Sum" problem
3. Write or modify Python code
4. Click "▶ Run" button
5. See three panels update simultaneously:
   - **Test Results**: Pass/fail indicator
   - **Output**: Console output (NEW)
   - **Errors**: Any execution errors
6. Modify code and run again - all panels update in real-time

### Behind the Scenes
1. Frontend sends code to backend API
2. Backend validates request and stores in DB
3. Code executed in isolated subprocess (10s timeout)
4. Output/errors captured and stored in DB
5. Response sent back to frontend
6. All three panels refresh with results

---

## 6. FILES CHANGED/CREATED

### Created
- `frontend/src/components/OutputPanel.tsx` (NEW - by me)

### Modified
- `app.py` - Enhanced with CORS, code execution, endpoints
- `models.py` - Added Submission model
- `schemas.py` - Added request/response schemas
- `crud.py` - Added database operations
- `database.py` - Configured PostgreSQL connection
- `frontend/src/App.tsx` - Added OutputPanel import and usage
- `frontend/src/styles.css` - Updated grid layout for 3 panels
- `Dockerfile` - Updated for new setup
- `docker-compose.yml` - NEW - PostgreSQL container config
- `requirements.txt` - Added all Python dependencies
- `init_db.py` - NEW - Database initialization script

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
- **Backend Routes**: 3 endpoints
- **Frontend Components**: 6 (including new OutputPanel)
- **Database Tables**: 1 (submissions)
- **API Response Time**: ~100-500ms (depending on code execution time)
- **Max Code Execution**: 10 seconds
- **Code Editor**: Monaco Editor (same as VS Code)
- **UI Theme**: Dark mode (VS Code inspired)

