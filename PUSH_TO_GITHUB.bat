@echo off
echo ========================================
echo Pushing to GitHub...
echo ========================================
cd /d "c:\Users\HP\OneDrive\Desktop\test-remote-server\test-remote-mcp-server"
git init
git remote remove origin 2>nul
git remote add origin https://github.com/deepakbishnoi717/test-remote-mcp-server.git
git rm --cached expenses.db 2>nul
git add .
git commit -m "Add MCP server"
git branch -M main
git push -u origin main
echo ========================================
echo SUCCESS! Your code is now on GitHub!
echo ========================================
pause
