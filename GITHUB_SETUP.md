# How to put this code on GitHub

A 5-minute guide. Do this when you're ready to start pushing the code.

## One-time setup (if you've never used GitHub before)

1. Make a GitHub account: https://github.com/signup
2. Install Git on your laptop:
   - **Mac:** Open Terminal, run `git --version`. If not installed, it'll prompt you.
   - **Windows:** Download from https://git-scm.com/download/win
3. Tell git who you are (replace with your info):
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your@email.com"
   ```

## Create the repo

1. Go to https://github.com/new
2. Name it something like `predictive-maintenance-mvp` or `sep-digital-twin`
3. Make it **Private** (you don't want competitors finding it yet)
4. Don't initialize with README (we already have one)
5. Click "Create repository"
6. Copy the URL it shows (looks like `git@github.com:yourusername/repo-name.git`)

## Push the code

Open Terminal in the folder where you saved these files, then:

```bash
# Initialize git in the folder
git init

# Add all files to be tracked
git add .

# First commit
git commit -m "Initial commit: predictive maintenance MVP"

# Connect to your GitHub repo (use the URL you copied)
git remote add origin https://github.com/yourusername/your-repo-name.git

# Push it up
git branch -M main
git push -u origin main
```

That's it. Done.

## After this, your workflow each time you make changes

```bash
# See what changed
git status

# Stage your changes
git add .

# Commit them with a message
git commit -m "Brief description of what you changed"

# Push to GitHub
git push
```

## When you get real customer data from Umasons

1. Save the CSV in the `data/` folder
2. Create a new script `load_umasons_data.py` that reads it and maps the columns to match what `analyze.py` expects
3. Commit and push the changes
4. The dashboard works on the real data immediately

## Helpful Claude prompts when you get stuck

- "I'm getting [error message]. Here's the code: [paste]. What's wrong?"
- "Explain this line of code to me: [paste]"
- "How do I [task] in Python? Give me a small example."
- "My CSV has columns named X, Y, Z. How do I map them to what `analyze.py` expects?"

You don't need to know everything. You need to know how to ask.
