Write-Host "Removing requirements-dev.txt from Git tracking and GitHub..." -ForegroundColor Green
Write-Host ""

Write-Host "Step 1: Checking if file is tracked..." -ForegroundColor Yellow
$tracked = git ls-files | Select-String "requirements-dev.txt"
if ($tracked) {
    Write-Host "File is tracked. Removing from Git..." -ForegroundColor Yellow
    git rm --cached requirements-dev.txt
    git commit -m "Remove requirements-dev.txt from tracking"
} else {
    Write-Host "File is not currently tracked." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 2: Checking Git history for the file..." -ForegroundColor Yellow
$inHistory = git log --oneline -- requirements-dev.txt 2>$null
if ($inHistory) {
    Write-Host "File found in history. Removing from all history..." -ForegroundColor Yellow
    git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch requirements-dev.txt' --prune-empty --tag-name-filter cat -- --all
    Write-Host "History cleaned." -ForegroundColor Green
} else {
    Write-Host "File not found in history." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 3: Pushing changes to GitHub..." -ForegroundColor Yellow
git push origin --force

Write-Host ""
Write-Host "Done! requirements-dev.txt should now be removed from GitHub." -ForegroundColor Green
Read-Host "Press Enter to continue"
