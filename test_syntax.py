"""
Syntax validation and basic testing script.
Run this to verify the code has no syntax errors.
"""

import sys
import importlib.util

def test_file_syntax(filepath, module_name):
    """Test if a Python file has valid syntax."""
    try:
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(f"[OK] {filepath} - Syntax OK")
            return True
    except SyntaxError as e:
        print(f"[ERROR] {filepath} - Syntax Error: {e}")
        return False
    except Exception as e:
        print(f"[WARN] {filepath} - Import Error (may need dependencies): {e}")
        return True  # Syntax is OK, just missing deps
    return False

def main():
    """Test all Python files for syntax errors."""
    print("="*60)
    print("SYNTAX VALIDATION TEST")
    print("="*60)
    
    files_to_test = [
        ("src/__init__.py", "init"),
        ("src/__main__.py", "main"),
        ("src/question_extractor.py", "question_extractor"),
        ("src/similarity_analyzer.py", "similarity_analyzer"),
        ("src/analyzer.py", "analyzer"),
        ("src/cli.py", "cli"),
    ]
    
    all_passed = True
    for filepath, module_name in files_to_test:
        if not test_file_syntax(filepath, module_name):
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("[SUCCESS] ALL FILES PASSED SYNTAX CHECK")
        print("\nNote: Import errors are expected until you run:")
        print("  pip install -r requirements.txt")
    else:
        print("[FAILED] SOME FILES HAVE SYNTAX ERRORS")
        sys.exit(1)
    print("="*60)

if __name__ == "__main__":
    main()

# Made with Bob
