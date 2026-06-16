import sys
from pathlib import Path

# Add src to the module search path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.append(str(src_path))

try:
    from bmmini.pipeline import run_pipeline
except ImportError as e:
    print(f"[ERROR] Failed to import pipeline from bmmini: {e}")
    print(f"sys.path: {sys.path}")
    sys.exit(1)

def main():
    try:
        # Run with default config
        run_pipeline("config/query.yaml")
        print("\n[SUCCESS] One-command pipeline successfully generated all outputs!")
        return 0
    except Exception as e:
        print(f"\n[ERROR] Pipeline execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())