---
title: How to Use pipenv
date: 2024-01-16T23:30:00+08:00
description: "Learn how to use Pipenv to manage Python project dependencies and virtual environments effortlessly. A step-by-step tutorial from installation to advanced usage.."
cover: https://media-site-matheus-nuxt.s3.amazonaws.com/posts/pipenv/thumb/pipenv.jpeg
readingTime: "3"
katex: true
mermaid: true
tags: ['Math', 'Mermaid', 'python']
---

Python's default package manager, `pip`, is excellent for installing packages. However, when it comes to managing project-specific dependencies and virtual environments, `pip` alone can feel a bit basic. Developers often find themselves juggling `pip` with `virtualenv` (or Python's built-in `venv` module), manually creating environments, activating them via specific scripts, and managing `requirements.txt` files.

This is where **Pipenv** comes to the rescue! Pipenv is the "officially recommended Python packaging tool from Python.org", designed to bring the best of all packaging worlds to the Python developer. It automatically creates and manages a virtual environment for your projects, and it manages your project dependencies in a `Pipfile` and `Pipfile.lock`, offering a more robust and deterministic build process.

Let's dive into how you can use Pipenv to streamline your Python workflow.

## Why Choose Pipenv?

- **Integrated Virtual Environments:** No more separate `virtualenv` or `venv` commands. Pipenv handles virtual environment creation and management automatically.
- **Deterministic Builds:** `Pipfile.lock` ensures that you get the same versions of dependencies every time, across different environments.
- **Dependency Resolution:** Pipenv helps resolve complex dependency graphs.
- **Clear Separation of Dependencies:** `Pipfile` distinguishes between default and development dependencies.
- **Security:** It can check for security vulnerabilities in your dependencies.

## Getting Started: Installing Pipenv

First, you need to install Pipenv. You can do this using `pip`:

```shell
pip install pipenv
```

It's generally recommended to install Pipenv on a per-user basis using `pip install --user pipenv` to avoid potential conflicts with system packages, ensuring the user's binary directory is in your PATH.

## Initializing Your Project with Pipenv

1.  **Navigate to Your Project Directory:**
    Open your terminal and go to your existing project folder or create a new one:

    ```shell
    mkdir my-python-project
    cd my-python-project
    ```

2.  **Start Using Pipenv:**
    You can initialize Pipenv in a project in a couple of ways:

    - **Install a package:** If you know what package you want to start with (e.g., `requests`), just install it. Pipenv will automatically create a `Pipfile` and a virtual environment.
      ```shell
      pipenv install requests
      ```
    - **Activate the shell:** If you don't want to install a package yet but want to create the environment and `Pipfile`:
      ```shell
      pipenv shell
      ```
      This command will create a virtual environment for your project (usually in a centralized location or a `.venv` folder within your project if `PIPENV_VENV_IN_PROJECT` is set) and activate it.

    _(Image Alt: Terminal showing pipenv shell command creating a virtual environment and activating it, with Pipfile and Pipfile.lock appearing)_

    Upon initialization, you'll notice two new files in your project directory:

    - `Pipfile`: This file replaces the traditional `requirements.txt` and contains information about your project's direct dependencies, Python version, and sources.
    - `Pipfile.lock`: This file records the exact versions of all your project's dependencies (and sub-dependencies). This ensures deterministic builds. **You should commit both `Pipfile` and `Pipfile.lock` to version control.**

    For those familiar with Node.js, `Pipfile` is analogous to `package.json`, and `Pipfile.lock` is similar to `package-lock.json`.

## Managing Dependencies

### Installing Packages

To install a package and add it to your `Pipfile`, use `pipenv install`:

```shell
pipenv install flask
```

This will install Flask and add it to the `[packages]` section of your `Pipfile` and update `Pipfile.lock`.

_(Image Alt: Pipfile content showing Flask added under the [packages] section)_

### Installing Development Dependencies

For packages only needed for development (e.g., linters, testing frameworks), use the `--dev` flag:

```shell
pipenv install pytest --dev
```

These will be added to the `[dev-packages]` section in your `Pipfile`.

### Uninstalling Packages

To remove a package:

```shell
pipenv uninstall flask
```

### Updating Packages

To update all packages:

```shell
pipenv update
```

To update a specific package:

```shell
pipenv update <package_name>
```

### Viewing the Dependency Graph

To see a tree of your project's dependencies:

```shell
pipenv graph
```

## Working with the Pipenv Environment

### Activating the Virtual Environment Shell

As shown earlier, `pipenv shell` activates your project's virtual environment. Your terminal prompt will usually change to indicate that you're inside the virtual environment.

### Running Commands Without Activating the Shell

If you just want to run a single command using the project's virtual environment without explicitly activating the shell, use `pipenv run`:

```shell
pipenv run python my_script.py
pipenv run pytest
```

### Exiting the Shell

If you've activated the shell with `pipenv shell`, you can deactivate it by simply typing:

```shell
exit
```

## Collaboration and Deployment

### Generating `requirements.txt` (for legacy systems)

While Pipenv uses `Pipfile` and `Pipfile.lock`, you might need a `requirements.txt` file for platforms or colleagues who don't use Pipenv. You can generate one from your `Pipfile.lock`:

```shell
pipenv lock -r > requirements.txt
```

For development dependencies:

```shell
pipenv lock -r -d > dev-requirements.txt
```

### Installing Dependencies from `Pipfile.lock`

When someone else clones your project, or when you're deploying, they can install all the exact dependencies specified in `Pipfile.lock` using:

```shell
pipenv sync
```

This is the recommended command for production deployments as it ensures only the locked versions are installed. If you also need dev dependencies (e.g., in a CI environment for testing):

```shell
pipenv sync --dev
```

Alternatively, `pipenv install --ignore-pipfile` also installs from the lock file.

## Key Advantages of Pipenv Summarized

- **Unified Tool:** Combines package management and virtual environment management.
- **Reproducible Builds:** `Pipfile.lock` ensures consistency across environments.
- **Improved Security:** Helps manage vulnerabilities and ensures dependency integrity.
- **Ease of Use:** More intuitive commands compared to juggling `pip` and `virtualenv`.

## Conclusion: Streamline Your Python Workflow

Pipenv offers a significant improvement over traditional Python packaging workflows by providing a single, powerful tool for managing dependencies and virtual environments. By adopting Pipenv, you can make your development process smoother, more reliable, and easier to manage, especially when working in teams or deploying applications.

Give it a try on your next Python project\!

---