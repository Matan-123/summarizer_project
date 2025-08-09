@echo off
echo Pushing changes to GitHub...
echo.

echo Step 1: Adding all changes...
git add .

echo.
echo Step 2: Committing changes...
git commit -m "Add UI improvements: bigger loading screen, persistent company names, and cleaner interface"

echo.
echo Step 3: Pushing to GitHub...
git push origin main

echo.
echo Done! Changes have been pushed to GitHub.
pause
