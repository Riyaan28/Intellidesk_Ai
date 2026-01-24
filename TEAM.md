# Team Collaboration Guide

## Overview

This guide helps the team of 3 work efficiently on IntelliDesk AI.

## Team Structure

### 👩‍💻 Member 1: AI & NLP Engineer

**Responsibility:** Email understanding & classification

**Your Module:** `ai/` folder

**Files You Own:**

- `ai/classifier.py` - Email classification
- `ai/urgency.py` - Urgency detection
- `ai/embeddings.py` - Vector embeddings
- `ai/deduplication.py` - Thread detection
- `ai/auto_reply.py` - Response generation
- `ai/config.py` - AI configuration

**Your Tasks:**

1. Improve classification accuracy
2. Fine-tune urgency detection
3. Optimize LLM prompts
4. Add new FAQ entries
5. Improve embedding similarity

**Branch Name:** `ai-module`

### 👨‍💻 Member 2: Backend & Logic Engineer

**Responsibility:** System logic & APIs

**Your Module:** `backend/` folder

**Files You Own:**

- `backend/main.py` - FastAPI app
- `backend/models.py` - Database models
- `backend/routers/*.py` - API endpoints
- `backend/services/*.py` - Business logic
- `backend/database.py` - Database setup

**Your Tasks:**

1. Create new API endpoints
2. Add database models
3. Implement SLA tracking
4. Add email integration (Gmail API)
5. Implement user authentication

**Branch Name:** `backend-module`

### 🎨 Member 3: Frontend & Integration Engineer

**Responsibility:** UI/UX & user experience

**Your Module:** `frontend/` folder

**Files You Own:**

- `frontend/src/pages/*.jsx` - Page components
- `frontend/src/components/*.jsx` - UI components
- `frontend/src/services/api.js` - API integration
- `frontend/src/App.jsx` - Main app

**Your Tasks:**

1. Improve dashboard design
2. Add new visualizations
3. Create ticket filters
4. Add real-time updates
5. Improve responsive design

**Branch Name:** `frontend-module`

## Git Workflow

### Initial Setup (Do Once)

```powershell
# Clone repository
git clone <repo-url>
cd IntelliDesk

# Create your branch
git checkout -b <your-branch-name>
# ai-module, backend-module, or frontend-module
```

### Daily Workflow

```powershell
# 1. Start of day - get latest changes
git checkout main
git pull origin main

# 2. Switch to your branch and update it
git checkout <your-branch>
git merge main  # Integrate latest changes

# 3. Work on your tasks
# Edit files in your module...

# 4. Test your changes
# Run tests, verify everything works

# 5. Commit your work
git add <your-files>
git commit -m "Descriptive message"

# Example commits:
# git commit -m "Add urgency detection for escalation keywords"
# git commit -m "Create ticket detail API endpoint"
# git commit -m "Add responsive design to dashboard"

# 6. Push to your branch
git push origin <your-branch>

# 7. End of day - create pull request (if ready)
# Go to GitHub and create PR from your branch to main
```

### Merging to Main

**Option 1: Pull Requests (Recommended)**

1. Push your branch
2. Create PR on GitHub
3. Request review from team
4. Merge after approval

**Option 2: Direct Merge (Quick Integration)**

```powershell
# Team lead does this:
git checkout main
git pull origin main
git merge ai-module
git merge backend-module
git merge frontend-module

# Resolve any conflicts
# Test everything
git push origin main
```

## Communication

### Daily Standup (5-10 minutes)

- What did you complete yesterday?
- What will you work on today?
- Any blockers?

### Code Review Checklist

- [ ] Code follows project structure
- [ ] No hardcoded values (use config)
- [ ] Functions have docstrings
- [ ] Changes tested locally
- [ ] No merge conflicts
- [ ] Commit messages are clear

## Module Integration Points

### AI ↔ Backend

**Interface:** Backend imports AI functions

```python
# backend/services/email_processor.py
from ai import classifier, urgency_detector

result = classifier.classify_email(subject, body, sender)
```

**Communication:**

- AI engineer: Keep function signatures stable
- Backend engineer: Use AI functions as documented

### Backend ↔ Frontend

**Interface:** REST API

```javascript
// frontend/src/services/api.js
const tickets = await getTickets();
```

**Communication:**

- Backend engineer: Document API changes in API.md
- Frontend engineer: Test against API docs

### Testing Integration

- AI Engineer: Test AI functions independently
- Backend Engineer: Test API endpoints with Postman
- Frontend Engineer: Test UI with real backend
- All Together: End-to-end testing

## Conflict Resolution

### If You Get Merge Conflicts

```powershell
# 1. Update your branch with latest main
git checkout <your-branch>
git merge main

# 2. VS Code will show conflicts
# Look for markers like:
# <<<<<<< HEAD
# Your changes
# =======
# Their changes
# >>>>>>> main

# 3. Edit files to resolve
# Keep the correct code, remove markers

# 4. Mark as resolved
git add <conflicted-file>
git commit -m "Resolve merge conflicts"
```

### Common Conflict Scenarios

**Scenario 1: Same file edited**

- Solution: Keep both changes if possible
- Or: Discuss with team to decide

**Scenario 2: Function signature changed**

- Solution: Update all callers
- Communication: Notify team before changing signatures

**Scenario 3: Database model changed**

- Solution: Backend engineer coordinates with team
- Run migrations together

## Best Practices

### For Everyone

1. **Commit often** - Small commits are easier to review
2. **Pull daily** - Stay synced with team
3. **Test before committing** - Don't break others' work
4. **Document changes** - Update README if needed
5. **Communicate** - Tell team about major changes

### AI Engineer

```python
# Good: Clear function with docstring
def classify_email(subject: str, body: str) -> Dict:
    """
    Classify email into category

    Args:
        subject: Email subject
        body: Email body

    Returns:
        Classification result with confidence
    """
    pass

# Bad: No documentation
def classify(s, b):
    pass
```

### Backend Engineer

```python
# Good: Proper error handling
try:
    result = process_email(email)
    return result
except Exception as e:
    logger.error(f"Processing failed: {e}")
    raise HTTPException(status_code=500, detail=str(e))

# Bad: No error handling
def process_email(email):
    result = do_something(email)
    return result
```

### Frontend Engineer

```javascript
// Good: Loading states
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);

// Bad: No feedback
const data = await api.getData();
```

## File Organization

```
IntelliDesk/
├── ai/                    # Member 1's files
│   ├── *.py              # Don't touch others' modules
│   └── config.py         # Shared - coordinate changes
│
├── backend/              # Member 2's files
│   ├── *.py
│   ├── routers/
│   ├── services/
│   └── .env             # Personal - never commit
│
└── frontend/            # Member 3's files
    ├── src/
    └── package.json
```

## Quick Reference

### Check Git Status

```powershell
git status              # See what changed
git diff                # See detailed changes
git log --oneline       # See recent commits
```

### Undo Changes

```powershell
git checkout -- file.py  # Discard changes to file
git reset HEAD~1        # Undo last commit (keep changes)
git revert HEAD         # Undo last commit (create new commit)
```

### Branch Management

```powershell
git branch              # List branches
git branch -d old-branch # Delete branch
git checkout -b new-feature # Create and switch to new branch
```

## Emergency Procedures

### "I Broke Everything!"

```powershell
# Option 1: Revert to last commit
git reset --hard HEAD

# Option 2: Revert to specific commit
git log --oneline  # Find good commit
git reset --hard <commit-hash>

# Option 3: Ask team for help!
```

### "My Branch is Way Behind"

```powershell
git checkout main
git pull origin main
git checkout <your-branch>
git rebase main  # Replay your changes on top of main

# If conflicts, resolve them
# Then: git rebase --continue
```

### "I Committed to Wrong Branch"

```powershell
# Move last commit to correct branch
git checkout correct-branch
git cherry-pick <commit-hash>

git checkout wrong-branch
git reset --hard HEAD~1
```

## Team Lead Responsibilities

### Daily

- Review pull requests
- Merge approved changes
- Run integration tests

### Weekly

- Code review session
- Demo new features
- Plan next week's tasks

### Deployment

```powershell
# 1. Ensure all branches merged
git checkout main
git pull origin main

# 2. Run all tests
cd backend
pytest
cd ../frontend
npm test

# 3. Tag release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# 4. Deploy (if using Docker)
docker-compose build
docker-compose up -d
```

## Success Metrics

Track your team's progress:

### Week 1

- [ ] All team members can run the project
- [ ] First commits from each member
- [ ] Basic features working

### Week 2

- [ ] AI classification working
- [ ] API endpoints complete
- [ ] Dashboard displaying tickets

### Week 3

- [ ] Auto-response working
- [ ] Deduplication working
- [ ] UI polished

### Week 4

- [ ] Testing complete
- [ ] Documentation done
- [ ] Demo ready

## Resources

- **API Docs:** http://localhost:8000/docs
- **Design:** frontend/src/components/
- **Database:** backend/models.py
- **AI Logic:** ai/\*.py

## Getting Help

1. Check documentation first (SETUP.md, API.md)
2. Ask teammate who owns that module
3. Search error message online
4. Check GitHub issues
5. Ask team lead

Good luck! 🚀
