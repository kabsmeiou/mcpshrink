## Setup

1. **Install dependencies using [uv]:**

   ```powershell
   uv sync
   ```

2. **Install `googletrans` manually (required for back translation):**
   ```powershell
   uv pip install googletrans==4.0.2
   ```
   > **Note:** If you skip this step, you may encounter  
   > `ModuleNotFoundError: No module named 'googletrans'`

## How to run tests

Run the following command in your terminal at the project root directory:
```
python3 -m pytest
```

## Making a pull request

In our project, we work with branches. The main branch is `main`.  
When you want to add a new feature or fix a bug, please create a new branch from `main` and make your changes there.
After you've made your changes, you can create a pull request to merge your branch back into `main`.

1. **Create a new branch:**
   ```bash
   git checkout -b your-branch-name
   ```
2. **Make your changes and commit them:**
   ```bash
   git add .
   git commit -m "Your commit message"
   ```
3. **Push your branch to the remote repository:**
   ```bash
   git push origin your-branch-name
   ```
4. **Create a pull request:**
   Go to the repository on GitHub, and you should see a prompt to create a pull request for your branch.

Please make sure to follow the project's coding standards and include tests for your changes if applicable.

*Branch names should be descriptive of the feature or fix you are working on, for example, `feature/add-new-endpoint` or `fix/bug-in-authentication`.*

## Conflicts
If you encounter any merge conflicts while creating your pull request, please resolve them before submitting the pull request. You can resolve conflicts by pulling the latest changes from the `main` branch into your branch and fixing any conflicts locally.

To avoid conflicts, it's a good practice to regularly pull the latest changes from the `main` branch into your branch while you are working on it.

```bash
git checkout your-branch-name
git pull origin main
```

or better yet, use rebase:

```bash
git checkout your-branch-name
git fetch origin
git rebase origin/main
```

This will help keep your branch up to date with the latest changes in `main` and reduce the likelihood of conflicts when you create your pull request.

## Project Issues

If you encounter any issues or have questions about the project, please feel free to open an issue on the project's GitHub repository. When creating an issue, please provide as much detail as possible, including steps to reproduce the issue, error messages, and any relevant code snippets. This will help us understand and address the issue more effectively.

If you are working on an issue, please comment on the issue to let others know that you are working on it. This helps prevent duplicate efforts and allows for better collaboration. 