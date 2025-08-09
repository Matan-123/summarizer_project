@echo off
echo Removing requirements-dev.txt from Git tracking and GitHub...
echo.

echo Step 1: Checking if file is tracked...
git ls-files | findstr requirements-dev.txt
if %errorlevel% equ 0 (
    echo File is tracked. Removing from Git...
    git rm --cached requirements-dev.txt
    git commit -m "Remove requirements-dev.txt from tracking"
) else (
    echo File is not currently tracked.
)

echo.
echo Step 2: Checking Git history for the file...
git log --oneline -- requirements-dev.txt
if %errorlevel% equ 0 (
    echo File found in history. Removing from all history...
    git filter-branch --force --index-filter "git rm --cached --ignore-unmatch requirements-dev.txt" --prune-empty --tag-name-filter cat -- --all
    echo History cleaned.
) else (
    echo File not found in history.
)

echo.
echo Step 3: Pushing changes to GitHub...
git push origin --force

echo.
echo Done! requirements-dev.txt should now be removed from GitHub.
pause
