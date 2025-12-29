# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Currently supported versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Geyser seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Reporting Process

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to the maintainers or through GitHub's security advisory feature:

1. Go to the repository's Security tab
2. Click "Report a vulnerability"
3. Fill out the form with details

### What to Include

Please include the following information:

- Type of vulnerability
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 1 week
- **Fix Development**: Varies based on complexity
- **Disclosure**: After fix is available

## Security Best Practices for Users

### Environment Variables

- Never commit `.env` files to version control
- Use strong, unique values for any API keys
- Rotate credentials regularly

### Data Security

- Be cautious with sensitive financial data
- Use the tool in secure, trusted environments
- Validate all input data
- Keep dependencies updated

### API Usage

- Use the caching feature to minimize API calls
- Monitor for unusual activity
- Implement rate limiting in production

### Dependencies

- Regularly update dependencies: `pip install --upgrade -r requirements.txt`
- Run security scans: `safety check`
- Review dependency vulnerabilities

## Known Security Considerations

### Data Sources

- All data comes from Yahoo Finance (yfinance library)
- Data quality and accuracy depends on the source
- No authentication required for public market data

### Input Validation

- Ticker symbols are validated against expected format
- Path traversal protection in file operations
- No SQL injection risk (no database by default)

### Caching

- Cache may contain sensitive analysis results
- Cache directory permissions should be restricted
- Consider encryption for sensitive deployments

## Security Features

### Implemented

- Input validation and sanitization
- Secure file path handling
- No code execution from untrusted sources
- Dependency security scanning in CI/CD
- Type checking to prevent common errors

### Planned

- Enhanced input validation
- Rate limiting for API calls
- Audit logging for production use
- Encryption options for cache
- Security headers for future API

## Disclosure Policy

- Security fixes will be released as soon as possible
- CVE identifiers will be requested for significant vulnerabilities
- Security advisories will be published on GitHub
- Users will be notified through release notes

## Comments on This Policy

If you have suggestions for improving this policy, please submit an issue or pull request.
