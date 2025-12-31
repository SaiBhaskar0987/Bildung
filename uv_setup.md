Step 0: Sync the Repository

Ensure your local repository is synced with the develop branch.

Step 1: Clone the Repository
git clone https://github.com/SaiBhaskar0987/Bildung.git

Step 2: Navigate to the Bildung Folder
cd Bildung


✔️ Ensure pyproject.toml exists in this directory.

Step 3: Switch to the develop Branch
git checkout develop
git branch

Step 4: Create Your Own Branch
git checkout -b <your-branch-name>

Step 5: Create a Virtual Environment

(Open VS Code → open the Bildung folder)

python -m venv .uvenu


.uvenu is the virtual environment name.
You may choose a different name if required.

Step 6: Activate the Virtual Environment
Git Bash
source .uvenu/Scripts/activate

PowerShell (VS Code Terminal)
.uvenu\Scripts\Activate.ps1

Step 7: Install UV Inside the Virtual Environment
pip install uv


Verify installation:

pip list

Step 8: Install Dependencies from pyproject.toml

✅ Recommended

uv sync


🔹 Alternative

uv pip install .


uv sync installs all dependencies defined in pyproject.toml.

Global Setup (System-Wide UV Installation)
Steps 0–4

Same as Local Setup.

Step 5: Install UV Globally
pip install uv

Step 6: Install Project Dependencies
uv sync

Troubleshooting Dependency Issues

If any module is missing or causes import errors:

uv add <package-name> --active

Example
uv add validate_email --active


This installs the package and updates pyproject.toml.