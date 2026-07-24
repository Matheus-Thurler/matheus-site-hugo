---
title: "GitHub Actions Matrix Strategy: Testing Multiple Versions Simultaneously"
date: 2025-08-24
slug: github-actions-matrix-strategy
description: "Learn to use Matrix Strategy in GitHub Actions to test your code across multiple language versions, operating systems, and dependencies at once, saving time and ensuring compatibility."
cover: /images/covers/github-actions-matrix.png
readingTime: "12"
katex: false
mermaid: false
tags: ['github-actions', 'ci-cd', 'testing', 'devops', 'automation']
categories: ['devops', 'ci-cd']
---

Testing your code on just one version of Node.js, Python, or Ruby is risky. What if your code breaks on Python 3.9 but works on 3.12? What if there are Windows-specific bugs you don't catch on Linux? **GitHub Actions Matrix Strategy** solves this elegantly.

## The Problem: Multi-Version Compatibility

Imagine this common scenario:

```yaml
# Simple workflow
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm test
```

**Problems:**
- ❌ Only tests on Node.js 20
- ❌ Only tests on Ubuntu
- ❌ Users with Node 16 or 18 may have issues
- ❌ Windows or macOS-specific bugs go undetected

To test 3 Node versions × 3 OSes = 9 combinations, you'd need 9 separate jobs. Too much duplicated code!

## The Solution: Matrix Strategy

Matrix Strategy lets you define multiple test dimensions in a single job:

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        node-version: [16, 18, 20]
    
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm test
```

**Result:** 9 jobs running in parallel automatically! 🚀

## How Matrix Works

### Basic Syntax

```yaml
strategy:
  matrix:
    # Each key defines a dimension
    language: [node, python, go]
    version: [latest, stable]
```

GitHub Actions creates a **cartesian product** of all combinations:
- language: node, version: latest
- language: node, version: stable
- language: python, version: latest
- language: python, version: stable
- language: go, version: latest
- language: go, version: stable

**Total:** 3 × 2 = **6 jobs**

### Accessing Matrix Values

Use `${{ matrix.variable }}` to access the current value:

```yaml
steps:
  - name: Print current combination
    run: |
      echo "Testing ${{ matrix.language }} version ${{ matrix.version }}"
```

## Practical Examples

### 1. Multi-Version Node.js Testing

```yaml
name: Node.js CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [16.x, 18.x, 20.x, 21.x]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test
      
      - name: Run lint
        run: npm run lint
```

**Result:** Tests on Node 16, 18, 20, and 21 simultaneously.

### 2. Cross-Platform Testing

```yaml
name: Cross-Platform Tests

on: [push, pull_request]

jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.9', '3.10', '3.11', '3.12']
    
    runs-on: ${{ matrix.os }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run tests
        run: pytest
```

**Result:** 3 OSes × 4 Python versions = **12 parallel jobs**

### 3. Matrix with Multiple Dimensions

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest]
    node-version: [18, 20]
    database: [postgres, mysql, sqlite]
    include:
      # Add specific combination
      - os: macos-latest
        node-version: 20
        database: postgres

steps:
  - name: Start database
    run: |
      echo "Starting ${{ matrix.database }} on ${{ matrix.os }}"
```

**Result:** (2 × 2 × 3) + 1 = **13 jobs**

## Advanced Features

### 1. Include - Add Specific Combinations

```yaml
strategy:
  matrix:
    os: [ubuntu-latest]
    node-version: [18, 20]
    include:
      # Test Node 16 only on Ubuntu
      - os: ubuntu-latest
        node-version: 16
      
      # Test Node 20 on macOS too
      - os: macos-latest
        node-version: 20
        
      # Add extra variables for specific combination
      - os: ubuntu-latest
        node-version: 20
        experimental: true
```

### 2. Exclude - Remove Unwanted Combinations

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    node-version: [16, 18, 20]
    exclude:
      # Node 16 not supported on Windows
      - os: windows-latest
        node-version: 16
      
      # Save runners - skip macOS for Node 18
      - os: macos-latest
        node-version: 18
```

**Result:** (3 × 3) - 2 = **7 jobs** instead of 9

### 3. Fail-Fast (Default: true)

```yaml
strategy:
  fail-fast: false  # Continue other jobs even if one fails
  matrix:
    version: [1, 2, 3, 4, 5]
```

**fail-fast: true** (default): Cancels all jobs if one fails  
**fail-fast: false**: Runs all independently

### 4. Max-Parallel - Limit Concurrent Executions

```yaml
strategy:
  max-parallel: 3  # Only 3 jobs at a time
  matrix:
    version: [1, 2, 3, 4, 5, 6, 7, 8]
```

Useful for:
- Saving CI minutes
- Avoiding external API rate limiting
- Limiting resource usage

## Real-World Use Cases

### 1. Multi-Version NPM Library

```yaml
name: NPM Package CI

on: [push, pull_request]

jobs:
  test:
    strategy:
      matrix:
        node-version: [16, 18, 20, 22]
        os: [ubuntu-latest, windows-latest, macos-latest]
        exclude:
          # Node 22 still experimental
          - os: windows-latest
            node-version: 22
    
    runs-on: ${{ matrix.os }}
    
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      
      - run: npm ci
      - run: npm test
      - run: npm run build
      
      - name: Test installation
        run: |
          npm pack
          npm install -g *.tgz
```

### 2. Application with Multiple Databases

```yaml
strategy:
  matrix:
    database:
      - type: postgres
        version: '14'
        port: 5432
      - type: postgres
        version: '15'
        port: 5432
      - type: mysql
        version: '8.0'
        port: 3306
      - type: mariadb
        version: '10.11'
        port: 3306

steps:
  - name: Start ${{ matrix.database.type }}
    run: |
      docker run -d \
        -p ${{ matrix.database.port }}:${{ matrix.database.port }} \
        ${{ matrix.database.type }}:${{ matrix.database.version }}
  
  - name: Run migrations
    env:
      DATABASE_URL: ${{ matrix.database.type }}://localhost:${{ matrix.database.port }}/test
    run: npm run migrate
  
  - name: Run tests
    run: npm test
```

### 3. Multi-Architecture Build

```yaml
strategy:
  matrix:
    include:
      - arch: amd64
        os: ubuntu-latest
      - arch: arm64
        os: ubuntu-latest
      - arch: armv7
        os: ubuntu-latest

steps:
  - uses: actions/checkout@v4
  
  - name: Set up QEMU
    uses: docker/setup-qemu-action@v3
  
  - name: Build for ${{ matrix.arch }}
    run: |
      docker buildx build \
        --platform linux/${{ matrix.arch }} \
        -t myapp:${{ matrix.arch }} \
        .
```

## Naming and Identification

### Dynamic Job Name

```yaml
jobs:
  test:
    name: Test on ${{ matrix.os }} with Node ${{ matrix.node-version }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        node-version: [18, 20]
    runs-on: ${{ matrix.os }}
```

**Result in UI:**
- Test on ubuntu-latest with Node 18
- Test on ubuntu-latest with Node 20
- Test on windows-latest with Node 18
- Test on windows-latest with Node 20

## Performance and Costs

### Runtime Consumption

Example: Matrix with 12 combinations, each running 5 minutes.

**fail-fast: true** (if none fail): 5 minutes × 12 = **60 runner minutes**  
**fail-fast: true** (if one fails at 2min): ~2-5 minutes (cancels others)  
**fail-fast: false**: Always 60 minutes

### Optimizations

1. **Use aggressive caching:**

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ matrix.node-version }}-${{ hashFiles('**/package-lock.json') }}
```

2. **Prioritize important combinations:**

```yaml
include:
  - os: ubuntu-latest
    node-version: 20
    priority: high  # Run this first
```

3. **Use max-parallel to control cost:**

```yaml
strategy:
  max-parallel: 2  # Max 2 jobs at a time on free accounts
```

## Debugging Matrix

### See All Combinations

```yaml
jobs:
  debug:
    strategy:
      matrix:
        os: [ubuntu, windows, macos]
        version: [1, 2, 3]
    steps:
      - name: Print matrix
        run: |
          echo "OS: ${{ matrix.os }}"
          echo "Version: ${{ matrix.version }}"
          echo "Runner: ${{ runner.os }}"
```

### Test One Combination

Use `workflow_dispatch` with inputs:

```yaml
on:
  workflow_dispatch:
    inputs:
      os:
        type: choice
        options: [ubuntu-latest, windows-latest, macos-latest]
      node-version:
        type: choice
        options: [16, 18, 20]

jobs:
  test:
    runs-on: ${{ inputs.os }}
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
```

## Best Practices

1. ✅ **Always test LTS + latest versions**
2. ✅ **Use fail-fast: false in PRs to see all issues**
3. ✅ **Document which combinations are mandatory**
4. ✅ **Use exclude to save on non-critical combinations**
5. ✅ **Name jobs descriptively**
6. ❌ **Avoid very large matrices (>20 combinations)**
7. ❌ **Don't duplicate logic - use matrix**

## Conclusion

Matrix Strategy transforms:

```yaml
# From 100+ lines of duplicated code
test-node-16-ubuntu: ...
test-node-18-ubuntu: ...
test-node-20-ubuntu: ...
test-node-16-windows: ...
# ... etc
```

Into:

```yaml
# 20 elegant lines
strategy:
  matrix:
    os: [ubuntu, windows, macos]
    node: [16, 18, 20]
```

Benefits:
- ⏱️ **Time savings** - parallel testing
- 🎯 **More coverage** - multiple combinations easily
- 🔧 **Simple maintenance** - one place to update
- 💰 **Cost control** - max-parallel and exclude

---

**Already using Matrix Strategy? Share in the comments how many combinations you test!**

#GitHubActions #CI #Testing #DevOps
