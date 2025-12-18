import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    main_file = root / "main.py"

    if not main_file.is_file():
        raise SystemExit("main.py not found next to build_exe.py")

    dist_dir = root / "dist"
    build_dir = root / "build"

    data_sep = ";" if os.name == "nt" else ":"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        "urlshortener",
        "--onefile",
        "--clean",
        "--noconfirm",
        "--add-data",
        f"{(root / 'templates' / 'index.html')}{data_sep}templates",
        str(main_file),
    ]

    print("Running:", " ".join(str(c) for c in cmd))
    subprocess.check_call(cmd, cwd=root)

    print()
    print("Build completed.")
    print(f"Executable is in: {dist_dir}")
    print("Run it and open http://127.0.0.1:11000 in your browser.")


if __name__ == "__main__":
    main()
