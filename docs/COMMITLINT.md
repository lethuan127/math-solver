# Commitlint Configuration

This repository uses [commitlint](https://commitlint.js.org/) to enforce consistent commit message conventions based on the [Conventional Commits](https://conventionalcommits.org/) specification.

## What is Commitlint?

Commitlint helps your team adhere to a commit convention. It supports npm-installed configurations that make sharing of commit conventions easy.

## Commit Message Format

Each commit message consists of a **header**, a **body** and a **footer**. The header has a special format that includes a **type**, an optional **scope** and a **subject**:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Type

Must be one of the following:

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools and libraries such as documentation generation

### Scope

The scope should be the name of the npm package affected (as perceived by the person reading the changelog generated from commit messages).

### Subject

The subject contains a succinct description of the change:

- Use the imperative, present tense: "change" not "changed" nor "changes"
- Don't capitalize the first letter
- No dot (.) at the end

## Examples

### Valid Commit Messages

```
feat: add image processing capability
fix: resolve authentication timeout issue
docs: update API documentation
style: format code according to prettier rules
refactor: simplify math solver algorithm
perf: optimize image compression
test: add unit tests for firebase client
chore: update dependencies
```

### Invalid Commit Messages

```
❌ Add new feature
❌ Fixed bug
❌ updated docs
❌ feat: Add new feature.
❌ random commit message
```

## Configuration

The commitlint configuration is defined in `commitlint.config.js` with the following rules:

- **Header max length**: 72 characters
- **Body max line length**: 100 characters
- **Footer max line length**: 100 characters
- **Type case**: lowercase
- **Subject**: cannot be empty, cannot end with period

## Git Hooks

This setup uses [Husky](https://typicode.github.io/husky/) to automatically run commitlint on every commit via the `commit-msg` git hook.

When you try to commit, commitlint will:
1. Check if your commit message follows the conventional format
2. Block the commit if the message doesn't comply
3. Show helpful error messages to guide you

## Manual Testing

You can manually test commit messages using the following npm scripts:

```bash
# Test a specific commit message
echo "feat: add new feature" | npx commitlint

# Check the last commit
npm run commitlint:last

# Test current commit message (during commit process)
npm run commitlint
```

## Troubleshooting

### Commit is blocked
If your commit is blocked, check the error message and adjust your commit message format accordingly.

### Bypass commitlint (not recommended)
If you absolutely need to bypass commitlint, you can use:
```bash
git commit --no-verify -m "your message"
```

**Note**: This should only be used in exceptional circumstances and is generally not recommended.

## Benefits

- **Consistency**: All team members follow the same commit message format
- **Automation**: Automatic changelog generation
- **Better History**: Clear and searchable git history
- **CI/CD Integration**: Easier to trigger automated workflows based on commit types
