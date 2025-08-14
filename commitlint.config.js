module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    // Type case should be lower-case
    'type-case': [2, 'always', 'lower-case'],
    // Type should not be empty
    'type-empty': [2, 'never'],
    // Subject should not be empty
    'subject-empty': [2, 'never'],
    // Subject should not end with period
    'subject-full-stop': [2, 'never', '.'],
    // Subject should be lower case (disabled for flexibility)
    'subject-case': [0],
    // Header max length
    'header-max-length': [2, 'always', 72],
    // Body max line length
    'body-max-line-length': [2, 'always', 100],
    // Footer max line length
    'footer-max-line-length': [2, 'always', 100],
  },
};
