# Agent Guidelines

This document contains guidelines for AI agents working on this repository.

## Commit Message Convention

This project uses **Conventional Commits** for all commit messages. This specification provides a simple set of rules for creating an explicit commit history.

### Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **build**: Changes that affect the build system or external dependencies
- **ci**: Changes to CI configuration files and scripts
- **chore**: Other changes that don't modify src or test files
- **revert**: Reverts a previous commit

### Examples

```bash
feat: add user authentication
fix: resolve memory leak in data processor
docs: update installation instructions
style: format code with ruff
refactor: simplify database connection logic
test: add unit tests for utils module
build: upgrade python version to 3.13
ci: add github actions workflow
chore: update dependencies
```

### Development Tools

This project uses **Ruff** as the linter and formatter for Python code.

#### Ruff Commands

```bash
# Check code for issues
uv run ruff check .

# Format code
uv run ruff format .

# Fix auto-fixable issues
uv run ruff check --fix .
```

#### Configuration

Ruff is configured in `pyproject.toml` under the `[tool.ruff]` section.
