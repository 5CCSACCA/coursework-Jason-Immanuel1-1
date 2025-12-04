# run_all_tests.py
import subprocess
import sys

def run_tests():
    """Run all pytest tests in the project."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-v", "."],
            check=False
        )
        if result.returncode == 0:
            print("All tests passed!")
        else:
            print(f"Some tests failed. Exit code: {result.returncode}")
    except Exception as e:
        print(f"Error running tests: {e}")

if __name__ == "__main__":
    run_tests()
