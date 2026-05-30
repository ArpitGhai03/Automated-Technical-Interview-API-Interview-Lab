import subprocess
import sys
import docker
import uuid
import os
import time
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Request
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import crud
from database import Base, SessionLocal, engine
from schemas import SubmissionCreate, SubmissionResponse

# Create app
app = FastAPI()

# Add CORS middleware BEFORE creating other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=600,
)

Base.metadata.create_all(bind=engine)

# Docker client for isolated execution
try:
    docker_client = docker.from_env()
    DOCKER_AVAILABLE = True
except Exception:
    DOCKER_AVAILABLE = False
    docker_client = None


# Test cases for Two Sum problem
TEST_CASES = [
    {
        "input": {"nums": [2, 7, 11, 15], "target": 9},
        "expected": [0, 1],
        "description": "Basic case with solution at beginning"
    },
    {
        "input": {"nums": [3, 2, 4], "target": 6},
        "expected": [1, 2],
        "description": "Solution in middle indices"
    },
    {
        "input": {"nums": [3, 3], "target": 6},
        "expected": [0, 1],
        "description": "Duplicate values"
    },
]


def run_test_cases(code: str) -> tuple:
    """
    Run user code against test cases and return (test_results, test_total).
    
    Expects user to define a function called 'two_sum' or 'twoSum' that takes (nums, target)
    and returns list of indices.
    
    Returns: (list of bool for each test, total count)
    """
    test_total = len(TEST_CASES)
    test_results = [False] * test_total  # Track each test individually
    
    try:
        # Execute the user's code to define their function
        exec_globals = {}
        exec(code, exec_globals)
        
        # Check if user defined two_sum or twoSum function (support both naming conventions)
        user_function = None
        if "two_sum" in exec_globals:
            user_function = exec_globals["two_sum"]
        elif "twoSum" in exec_globals:
            user_function = exec_globals["twoSum"]
        
        if user_function is None:
            return test_results, test_total
        
        # Run each test case
        for idx, test_case in enumerate(TEST_CASES):
            try:
                result = user_function(**test_case["input"])
                # Check if result matches expected output (order-independent for indices)
                if result == test_case["expected"] or (
                    isinstance(result, list) and 
                    isinstance(test_case["expected"], list) and
                    set(result) == set(test_case["expected"]) and
                    len(result) == len(test_case["expected"])
                ):
                    test_results[idx] = True
            except Exception:
                # Test failed - function threw an exception
                test_results[idx] = False
    
    except Exception:
        # Couldn't execute code or extract function
        pass
    
    return test_results, test_total


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def execute_python_code_docker(code: str) -> dict:
    """Execute Python code in isolated Docker container for maximum security."""
    if not DOCKER_AVAILABLE or docker_client is None:
        return execute_python_code_fallback(code)
    
    start_time = time.time()
    execution_id = str(uuid.uuid4())[:8]
    container_name = f"code-executor"
    
    try:
        # Get or create the executor container
        try:
            container = docker_client.containers.get(container_name)
        except docker.errors.NotFound:
            runtime = time.time() - start_time
            return {
                "status": "error",
                "output": "",
                "error": "Code executor container not available. Please ensure docker-compose is running.",
                "runtime": runtime,
            }
        
        # Create a unique script file for this execution
        script_path = f"/tmp/code_execution/script_{execution_id}.py"
        
        # Write code to container
        container.exec_run(
            f"sh -c 'cat > {script_path} << 'EOF'\\n{code}\\nEOF'",
            user="root"
        )
        
        # Execute the code with timeout
        exit_code, output = container.exec_run(
            f"timeout 10 python {script_path}",
            stdout=True,
            stderr=True,
        )
        
        decoded_output = output.decode('utf-8', errors='ignore')
        runtime = time.time() - start_time
        
        # Clean up the script file
        container.exec_run(f"rm -f {script_path}")
        
        if exit_code == 0:
            return {
                "status": "completed",
                "output": decoded_output,
                "error": None,
                "runtime": runtime,
            }
        elif exit_code == 124:
            return {
                "status": "error",
                "output": "",
                "error": "Code execution timed out (10 second limit)",
                "runtime": runtime,
            }
        else:
            return {
                "status": "error",
                "output": decoded_output,
                "error": f"Execution failed with exit code {exit_code}",
                "runtime": runtime,
            }
    
    except Exception as e:
        runtime = time.time() - start_time
        return {
            "status": "error",
            "output": "",
            "error": f"Docker execution error: {str(e)}",
            "runtime": runtime,
        }


def execute_python_code_fallback(code: str) -> dict:
    """Fallback: Execute Python code with subprocess when Docker is unavailable."""
    start_time = time.time()
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=10,
        )
        runtime = time.time() - start_time
        if result.returncode == 0:
            return {
                "status": "completed",
                "output": result.stdout,
                "error": None,
                "runtime": runtime,
            }
        return {
            "status": "error",
            "output": result.stdout,
            "error": result.stderr,
            "runtime": runtime,
        }
    except subprocess.TimeoutExpired:
        runtime = time.time() - start_time
        return {
            "status": "error",
            "output": "",
            "error": "Code execution timed out (10 second limit)",
            "runtime": runtime,
        }
    except Exception as e:
        runtime = time.time() - start_time
        return {
            "status": "error",
            "output": "",
            "error": str(e),
            "runtime": runtime,
        }


def execute_python_code(code: str) -> dict:
    """
    Execute Python code in isolated Docker container (primary) with fallback.
    Also runs test cases and returns results.
    """
    execution_result = execute_python_code_docker(code)
    
    # Run test cases to check solution correctness
    test_results, test_total = run_test_cases(code)
    test_passed = sum(test_results)
    execution_result["test_passed"] = test_passed
    execution_result["test_total"] = test_total
    execution_result["test_results"] = test_results  # Track individual results
    
    return execution_result


@app.get("/")
def health_check():
    return {"status": "healthy"}


@app.post("/submit", response_model=SubmissionResponse)
def submit_code(submission: SubmissionCreate, db: Session = Depends(get_db)):
    try:
        new_submission = crud.create_submission(db, submission)

        new_submission.status = "running"
        db.commit()

        if submission.language == "python":
            execution_result = execute_python_code(submission.code)
        else:
            execution_result = {
                "status": "error",
                "output": "",
                "error": f"Language '{submission.language}' not supported yet",
            }

        output = execution_result.get("output") or execution_result.get("error") or ""
        runtime = execution_result.get("runtime")
        test_passed = execution_result.get("test_passed")
        test_total = execution_result.get("test_total")
        test_results = execution_result.get("test_results", [])
        
        # Ensure test_results is a proper list of booleans
        if not isinstance(test_results, list):
            test_results = []
        
        # Include test results in output for display
        if test_results:
            test_details = "\n\nTest Results:\n"
            for idx, passed in enumerate(test_results):
                status = "PASSED" if passed else "FAILED"
                test_details += f"Test {idx + 1}: {status}\n"
            output = (output or "") + test_details
        
        result = crud.update_submission(
            db,
            new_submission,
            execution_result.get("status", "error"),
            output,
            runtime=runtime,
            test_passed=test_passed,
            test_total=test_total,
            test_results=test_results if test_results else None,
        )
        
        return result
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Server error: {str(e)}\n{error_detail}"
        )


@app.get("/submissions/{submission_id}", response_model=SubmissionResponse)
def fetch_submission(submission_id: int, db: Session = Depends(get_db)):
    submission = crud.get_submission(db, submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission
