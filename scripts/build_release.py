#!/usr/bin/env python3
"""
Build script for Jungle / Dou Shou Qi Windows release.
Runs tests, bundles with PyInstaller, copies README and prompt.md,
and performs a smoke test on the packaged executable.
"""
import os
import sys
import shutil
import subprocess
import tempfile
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RELEASE_DIR = os.path.join(PROJECT_ROOT, "release")
EXE_NAME = "JungleGame.exe"


def run_tests() -> bool:
    print("=== Running test suite ===")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q"],
        cwd=PROJECT_ROOT,
    )
    if result.returncode != 0:
        print("ERROR: Tests failed. Aborting build.")
        return False
    print("Tests passed.\n")
    return True


def build_exe() -> bool:
    print("=== Building executable with PyInstaller ===")
    # Clean previous build artifacts
    dist_dir = os.path.join(PROJECT_ROOT, "dist")
    build_dir = os.path.join(PROJECT_ROOT, "build")
    for d in (dist_dir, build_dir):
        if os.path.isdir(d):
            shutil.rmtree(d)

    # Ensure release dir exists and is clean
    if os.path.isdir(RELEASE_DIR):
        shutil.rmtree(RELEASE_DIR)
    os.makedirs(RELEASE_DIR)

    # Delete any leftover spec file so PyInstaller uses our CLI arguments
    spec_file = os.path.join(PROJECT_ROOT, "JungleGame.spec")
    if os.path.exists(spec_file):
        os.remove(spec_file)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", "JungleGame",
        "--distpath", RELEASE_DIR,
        "--workpath", build_dir,
        os.path.join("jungle", "__main__.py"),
    ]

    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        print("ERROR: PyInstaller build failed.")
        return False

    print("Build complete.\n")
    return True


def copy_release_files() -> bool:
    print("=== Copying release files ===")
    for filename in ("README.md", "prompt.md"):
        src = os.path.join(PROJECT_ROOT, filename)
        dst = os.path.join(RELEASE_DIR, filename)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"Copied {filename}")
        else:
            print(f"WARNING: {filename} not found at project root.")
    print()
    return True


def smoke_test_exe() -> bool:
    print("=== Smoke testing packaged executable ===")
    exe_path = os.path.join(RELEASE_DIR, EXE_NAME)
    if not os.path.exists(exe_path):
        print(f"ERROR: {EXE_NAME} not found in release folder.")
        return False

    print(f"Launching {exe_path}...")
    proc = subprocess.Popen(
        [exe_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # Wait briefly for window to appear
    time.sleep(4)

    # Check if process is still running
    ret = proc.poll()
    if ret is not None and ret != 0:
        stdout, stderr = proc.communicate()
        print(f"ERROR: Process exited early with code {ret}")
        if stdout:
            print(stdout.decode("utf-8", errors="replace"))
        if stderr:
            print(stderr.decode("utf-8", errors="replace"))
        return False

    # Terminate gracefully
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()

    print("Smoke test passed.\n")
    return True


def main():
    if not run_tests():
        sys.exit(1)
    if not build_exe():
        sys.exit(1)
    if not copy_release_files():
        sys.exit(1)
    if not smoke_test_exe():
        sys.exit(1)

    print("=== Release build successful ===")
    print(f"Output folder: {RELEASE_DIR}")
    for item in sorted(os.listdir(RELEASE_DIR)):
        print(f"  - {item}")


if __name__ == "__main__":
    main()
