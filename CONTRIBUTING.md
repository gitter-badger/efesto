# Contribution guide

Welcome to Efesto's contribution guide!

## Contributing
Please open an issue describing your changes.

Branch the master and submit a pull request to with your changes. Ensure that
all tests are passing.

Pull requests concerning additional features need to provide the tests for those
features.

## Tests
To run tests you will need pytest and pytest-falcon. Efesto needs to be
installed.

You can run all tests with:
```
py.test
```

## Commits messages
Efesto uses an Angular-like style for commits messages.

```
<type>(<scope>): <subject>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

### Subject
The subject should contains succinct description of the change:

* use the imperative, present tense: "change" not "changed" nor "changes"
* don't capitalize first letter
* no dot (.) at the end

### Types
Must be one of the following:

* feat: changes that add a new feature
* fix: changes that fix a bug
* docs: changes to documentation or docstrings
* style: changes regarding formatting, white spaces, etc.
* refactor: changes that neither fixes a bug or a feature
* performance: changes that improve performance
* tests: changes regarding tests
* config: changes regarding the build process or auxiliary tools

### Scopes
The scope can be anything that helps identifying where a change has been made;
usually this would be a file or in case of large files, a class.

When using a file name as scope, use only lowercase and omit the extension.
