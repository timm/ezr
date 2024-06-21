# Introduction to Git

## What is Git?
Git is a distributed version control system used for tracking changes in source code during software development. It allows multiple developers to work on a project simultaneously without overwriting each other's changes.

## Main Concepts

### Repository
A repository (or repo) is a storage space where your project lives. It can be local (on your computer) or remote (on a server like GitHub).

### Commit
A commit is a snapshot of your project at a particular point in time. Each commit has a unique ID and includes a message describing the changes.

### Branch
A branch is a parallel version of your project. By default, Git creates a `main` (or `master`) branch. Branches allow you to develop features independently from the main codebase.

### Merge
Merging is the process of combining changes from different branches. It integrates the work from one branch into another.

### Clone
Cloning is copying a repository from a remote server to your local machine.

### Pull and Push
- **Pull**: Fetches changes from a remote repository and merges them into your local branch.
- **Push**: Sends your committed changes to a remote repository.

## Common Traps and How to Avoid Them

### Merge Conflicts
**Trap**: Conflicts occur when changes in different branches affect the same part of a file and Git can't automatically merge them.

**Avoid**: Frequently pull changes from the remote repository and communicate with your team to avoid overlapping work. Resolve conflicts using a merge tool.

### Forgetting to Commit Frequently
**Trap**: Working for too long without committing can make it hard to track changes and increases the risk of losing work.

**Avoid**: Commit often with meaningful messages. This makes it easier to backtrack and understand the history of changes.

### Working Directly on the Main Branch
**Trap**: Making changes directly on the `main` branch can lead to unstable code and makes it harder to manage different features or fixes.

**Avoid**: Create new branches for features or fixes. Once the work is done and tested, merge it back into `main`.

### Not Pushing Changes Regularly
**Trap**: If you don't push your changes frequently, your local repository can diverge significantly from the remote repository, leading to complex merges.

**Avoid**: Push your changes often to keep the remote repository updated and reduce the risk of conflicts.

## Basic Commands

```sh
# Clone a repository
git clone <repository-url>

# Check the status of your files
git status

# Add files to staging area
git add <file>

# Commit your changes
git commit -m "Commit message"

# Push changes to remote repository
git push

# Pull changes from remote repository
git pull

# Create a new branch
git checkout -b <branch-name>

# Merge a branch into the current branch
git merge <branch-name>
```

By understanding these basic concepts and being aware of common pitfalls, you can effectively use Git for version control in your projects. 
