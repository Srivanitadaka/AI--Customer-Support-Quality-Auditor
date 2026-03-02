"""
cleanup_results.py
──────────────────────────────────────────
Deletes all scored JSON files from analysis_results/
so your dashboard starts fresh and clean.

Run from project root:
    python cleanup_results.py
"""

from pathlib import Path

BASE        = Path(__file__).resolve().parent
RESULTS_DIR = BASE / "analysis_results"

def main():
    print("\n" + "="*50)
    print("  CallAudit Pro — Results Cleanup")
    print("="*50)

    if not RESULTS_DIR.exists():
        print("\n  analysis_results/ folder not found. Nothing to clean.")
        return

    # Find all scored JSON files
    all_files  = list(RESULTS_DIR.glob("*.json"))

    if not all_files:
        print("\n  No scored files found. Already clean!")
        return

    print(f"\n  Found {len(all_files)} scored files:\n")
    for f in sorted(all_files):
        print(f"    {f.name}")

    # Confirm
    print(f"\n  This will permanently delete all {len(all_files)} files.")
    confirm = input("  Type YES to confirm: ").strip()

    if confirm.upper() != "YES":
        print("\n  Cancelled. Nothing was deleted.")
        return

    # Delete
    deleted = 0
    for f in all_files:
        try:
            f.unlink()
            deleted += 1
        except Exception as e:
            print(f"  Could not delete {f.name}: {e}")

    print(f"\n  Deleted {deleted} files.")
    print(f"  Dashboard is now clean.")
    print(f"\n  Next: run batch_scorer.py to rescore fresh files.")
    print("="*50 + "\n")


if __name__ == "__main__":
    main()