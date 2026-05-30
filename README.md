# Interview Lab 🎓

An online code submission and execution platform for coding interviews and practice problems.

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (npm)
- PostgreSQL running on localhost:5432

### Setup & Run

#### Option 1: Automated PowerShell Script (Windows)
```powershell
# In PowerShell, from project root:
.\start-lab.ps1
```

#### Option 2: Manual Setup

**Terminal 1 - Backend:**
```bash
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Start backend
uvicorn app:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Access
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Features

✅ **Code Execution**
- Write Python code directly in Monaco Editor
- Execute code against built-in test cases
- Real-time output display

✅ **Test Results**
- Individual pass/fail for each test case
- Test summary with count
- Detailed error messages

✅ **Two Sum Problem**
- Classic LeetCode problem included
- 3 test cases with varying difficulty
- Support for both `two_sum()` and `twoSum()` function names

✅ **Fast Development**
- Vite dev server with proxy to backend
- Hot module reloading
- Real-time test execution

## Project Structure

```
Interview Lab/
├── app.py                      # FastAPI backend
├── models.py                   # SQLAlchemy models
├── schemas.py                  # Pydantic schemas
├── crud.py                     # Database operations
├── database.py                 # DB connection setup
├── init_db.py                  # Database initialization
├── requirements.txt            # Python dependencies
│
├── frontend/                   # React + TypeScript + Vite
│   ├── src/
│   │   ├── App.tsx            # Main app component
│   │   ├── api.ts             # API client
│   │   ├── types.ts           # TypeScript types
│   │   ├── styles.css         # Global styles
│   │   └── components/
│   │       ├── Toolbar.tsx
│   │       ├── Editor.tsx
│   │       ├── TestResults.tsx
│   │       ├── OutputPanel.tsx
│   │       └── ErrorPanel.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── docker-compose.yml          # PostgreSQL container
├── Dockerfile                  # Backend image
└── start-lab.ps1              # Launch script
```

## How It Works

1. **Write Code**: Use Monaco Editor to write your solution
2. **Run Tests**: Click "Run" button
3. **Get Results**: 
   - ✓ Pass/fail for each test case
   - Execution output
   - Runtime statistics
   - Error messages if any

## Test Cases (Two Sum Problem)

| Test # | Input | Expected | Description |
|--------|-------|----------|-------------|
| 1 | `two_sum([2, 7, 11, 15], 9)` | `[0, 1]` | Basic case |
| 2 | `two_sum([3, 2, 4], 6)` | `[1, 2]` | Middle indices |
| 3 | `two_sum([3, 3], 6)` | `[0, 1]` | Duplicate values |

## API Endpoints

### POST /submit
Submit code for execution
```bash
curl -X POST http://localhost:8000/submit \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def twoSum(nums, target):\n    ...",
    "language": "python"
  }'
```

Response:
```json
{
  "id": 1,
  "code": "...",
  "language": "python",
  "status": "completed",
  "output": "Test Results: Test 1: PASSED...",
  "runtime": 0.047,
  "test_passed": 3,
  "test_total": 3,
  "test_results": [true, true, true],
  "created_at": "2026-05-30T12:43:30"
}
```

### GET /submissions/{id}
Fetch execution results by submission ID

### GET /
Health check endpoint

## Configuration

### Environment Variables
None required - uses defaults for local development

### Database
```
Host: localhost
Port: 5432
Username: postgres
Password: Arpit_123
Database: code_db
```

### Vite Proxy (Frontend)
Routes `/submit` and `/submissions` requests to backend
```typescript
proxy: {
  "/submit": { target: "http://localhost:8000", changeOrigin: true },
  "/submissions": { target: "http://localhost:8000", changeOrigin: true }
}
```

## Technology Stack

**Backend**
- FastAPI - Web framework
- SQLAlchemy - ORM
- Pydantic - Data validation
- Docker - Code execution sandbox
- PostgreSQL - Database

**Frontend**
- React 18 - UI framework
- TypeScript - Type safety
- Vite - Build tool
- Monaco Editor - Code editor (VS Code style)
- CSS - Dark theme styling

## Development

### Adding a New Problem
1. Add test cases to `TEST_CASES` in `app.py`
2. Update `run_test_cases()` to check for your function
3. Create frontend components if needed

### Docker Code Execution
The platform supports Docker for isolated code execution:
- Primary: Docker container execution (safest)
- Fallback: Subprocess execution (if Docker unavailable)
- Timeout: 10 seconds per execution

## Troubleshooting

### "Cannot connect to PostgreSQL"
- Ensure PostgreSQL is running on localhost:5432
- Check credentials match `database.py`
- Run `python init_db.py` to initialize

### "CORS Error"
- Vite proxy should handle this automatically
- If error persists, restart frontend with `npm run dev`

### Tests not running
- Ensure your function is named `twoSum()` or `two_sum()`
- Check function signature: `def twoSum(nums, target) -> list[int]:`
- Verify return type is a list of integers

### Code execution timeout
- Check for infinite loops in code
- 10-second limit prevents resource exhaustion

## Performance Notes

- **API Response**: 50-150ms typical (excludes code execution)
- **Code Execution**: 10ms-10000ms (depends on code complexity)
- **Test Execution**: Runs 3 test cases automatically
- **Database**: Single table, optimized queries

## Future Enhancements

- [ ] Support more programming languages (Java, JavaScript, etc.)
- [ ] User authentication and submission history
- [ ] Problem library with multiple problems
- [ ] Real-time collaborative coding
- [ ] Advanced test framework integration
- [ ] Code templates and hints
- [ ] Leaderboard and rankings

## License

MIT

## Support

For issues or questions, check `PROJECT_SUMMARY.md` for detailed documentation.

---

**Happy Coding!** 🚀
