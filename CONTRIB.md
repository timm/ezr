# 🤝 Contributing to This Project

Thanks for your interest in contributing! This project is a minimalist, modular system for interpretable active learning and optimization. We aim for clarity, conciseness, and low dependency code.

## 🧭 Project Principles

- 🧼 **Readable**: Minimal lines, clear naming, inline documentation.
- ⚡ **Fast**: No heavy libraries; keep it light and efficient.
- 🧪 **Testable**: Each module should be runnable and testable independently.
- 🎯 **Purposeful**: Only add features that support the core goals: explainable reasoning, optimization, and small-data learning.

## 📁 Code Structure

| File         | Purpose                                                  |
|--------------|----------------------------------------------------------|
| `lib.py`     | Core utilities and data types (`Num`, `Sym`, etc.)      |
| `data.py`    | Data loading and preprocessing                           |
| `prep.py`    | Configuration and command-line processing                |
| `dist.py`    | Distance metrics and selection logic                     |
| `tree.py`    | Tree-based explanation and learning                      |
| `stats.py`   | Statistical summarization                                |
| `like.py`    | Likelihood computation for "best-vs-rest" classification|
| `about.py`   | Experiment metadata and description                      |
| `likely.py`  | Main entry point for running `--likely` experiments      |

## 📦 How to Contribute

### 1. Clone and Set Up

```bash
git clone https://github.com/yourname/yourrepo
cd yourrepo
python3 -B -m yourmainmodule -h
```

### 2. Style Guide

- Prefer one-liners when readable.
- Avoid external dependencies (unless essential).
- Use `o()` for objects, avoid classes unless necessary.
- Use meaningful short names (`num`, `sym`, `row`, `col`).
- Write short functions. The current LOC distribution is shown below. 7 to 15 lines seems normal and less is beest. 

```bash
gawk 'BEGIN {RS="\ndef"; FS="\n"} {print NF}' *.py | sort -n | fmt
```

<img width="500"  alt="image" src="https://github.com/user-attachments/assets/6de1c388-03ea-4eb3-b782-72d6c13dc68c" />


### 3. Tests

Each `.py` file should run as a test:

```bash
python3 -B -m lib
```

If adding a module, ensure:

```python
if __name__ == "__main__":
    eg("your_example", your_test_fn)
```

### 4. Add New Examples

Use the `eg()` test runner style already present in modules like `lib.py`.

## ✅ Before You Commit

- Check with `python3 -B -m <module>` that your file runs.
- Run all modules once to catch regressions.
- Keep it clean: no trailing whitespace, unnecessary comments, or debug prints.

## 🧙🏽 Suggestions Welcome

Not sure if your idea fits? Create an issue or open a draft PR for feedback.
