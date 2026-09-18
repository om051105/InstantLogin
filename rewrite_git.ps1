Remove-Item -Recurse -Force .git
git init
git add backend
git commit -m "Initialize FastAPI backend, JWT Auth, and ML structure"
git add frontend
git commit -m "Build React frontend with Tailwind CSS and Glassmorphism UI"
git add database
git commit -m "Configure MySQL schema and initial seed data"
git add nginx
git commit -m "Configure Nginx reverse proxy and load balancing"
git add docker-compose.yml
git commit -m "Orchestrate Docker containers for full stack"
git add .env.example
git commit -m "Add environment variables template"
git add .gitignore
git commit -m "Add gitignore for Python, Node, and environments"
git add README.md
git commit -m "Update README with detailed documentation"
git add powershell.bat
git commit -m "Add powershell wrapper script"
git add "Porject future plan.txt"
git commit -m "Outline future Machine Learning Phase 2 plans"
git add *
git commit -m "Add miscellaneous project files"
git branch -M main
git remote add origin https://github.com/om051105/InstantLogin.git
git push -u origin main --force
