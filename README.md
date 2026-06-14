# Interview Lab 🎓

An online code submission and execution platform for coding interviews and practice problems.

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (npm)
- PostgreSQL running on localhost:5432
- Docker Desktop — runs the PostgreSQL container and the per-submission code-execution sandbox

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

# Build the sandbox image (one-time, and after changing anything under runner/)
docker build -t interview-executor -f Dockerfile.executor .

# Start PostgreSQL and initialize the schema
docker compose up -d
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

✅ **Sandboxed Code Execution**
- Untrusted code runs in an ephemeral, hardened Docker container (no network, read-only filesystem, CPU/memory/PID limits, dropped capabilities, non-root)
- Grading happens inside the sandbox — code never runs in the API process
- Fails closed if Docker is unavailable (set `ALLOW_UNSANDBOXED=1` for local dev)

✅ **Test Results**
- Individual pass/fail for each test case
- Test summary with count
- Detailed error messages

✅ **Multiple Problems & Languages**
- Problem registry (`problems.py`) with a picker in the UI (`GET /problems`)
- **Python** problems graded by calling the candidate's function against test cases
- **SQL** problems graded by running the query against a seeded in-memory SQLite database and comparing the result set
- Two Sum (Python) and High Earners (SQL) included

✅ **Fast Development**
- Vite dev server with proxy to backend
- Hot module reloading
- Real-time test execution

## Project Structure

```
Interview Lab/
├── app.py                      # FastAPI backend (routes only)
├── problems.py                 # Problem registry (Python + SQL)
├── sandbox.py                  # Ephemeral Docker execution + grading dispatch
├── runner/                     # Scripts that run INSIDE the sandbox
│   ├── run_python.py
│   └── run_sql.py
├── models.py                   # SQLAlchemy models
├── schemas.py                  # Pydantic schemas
├── crud.py                     # Database operations
├── database.py                 # DB connection setup
├── init_db.py                  # Database initialization + column migrations
├── requirements.txt            # Python dependencies
├── Dockerfile.executor         # Sandbox image (built as interview-executor)
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

### GET /problems
List available problems (answer-free): `id`, `title`, `language`, `prompt`, `starter_code`.

### POST /submit
Submit a solution for a given problem. The request takes a `problem_id` and the
`code`; the language is derived from the problem.
```bash
curl -X POST http://localhost:8000/submit \
  -H "Content-Type: application/json" \
  -d '{
    "problem_id": "two-sum",
    "code": "def two_sum(nums, target):\n    ..."
  }'
```

Response:
```json
{
  "id": 1,
  "problem_id": "two-sum",
  "code": "...",
  "language": "python",
  "status": "completed",
  "output": "Test Results:\n  Test 1: PASSED...",
  "runtime": 0.74,
  "test_passed": 3,
  "test_total": 3,
  "test_results": [true, true, true],
  "created_at": "2026-06-14T12:43:30"
}
```
Returns `404` for an unknown `problem_id`, and `503` if the sandbox is
unavailable (Docker down and `ALLOW_UNSANDBOXED` not set).

### GET /submissions/{id}
Fetch execution results by submission ID

### GET /
Health check; reports the active sandbox mode (`docker` / `host-unsandboxed` / `unavailable`)

## Configuration

### Environment Variables
| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | see `database.py` | Postgres connection string |
| `EXECUTOR_IMAGE` | `interview-executor` | Sandbox image used to run submissions |
| `SANDBOX_TIMEOUT` | `10` | Per-submission execution timeout (seconds) |
| `ALLOW_UNSANDBOXED` | unset | If `1`, run on the host when Docker is unavailable (dev only) |

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
Add an entry to the registry in `problems.py`:
- **Python**: a `PythonProblem` with `entrypoints` (accepted function names) and `test_cases`
- **SQL**: a `SqlProblem` with `setup_sql` (schema + seed), `expected_rows`, and `order_matters`

The UI problem picker and grading pick it up automatically — no frontend or `app.py` changes needed.

### Sandboxed Code Execution
Each submission runs in its own ephemeral Docker container (`sandbox.py`):
- Image: `interview-executor` (built from `Dockerfile.executor`)
- Hardening: `--network none`, `--read-only`, `--memory 256m`, `--cpus 0.5`, `--pids-limit 64`, `--cap-drop ALL`, `--security-opt no-new-privileges`, `--user nobody`
- Timeout: 10s (configurable via `SANDBOX_TIMEOUT`), enforced both inside the container and by the host
- Fails closed when Docker is unavailable; `ALLOW_UNSANDBOXED=1` permits a host fallback for local dev only

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

- [x] Docker sandboxing for safe, isolated code execution
- [x] SQL problems (in-memory SQLite)
- [x] Problem library with multiple problems
- [ ] Support more programming languages (Java, JavaScript, etc.)
- [ ] User authentication and submission history
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
