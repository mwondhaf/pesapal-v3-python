<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Copilot Instructions for Pesapal Python Client

This is a Python package for integrating with the Pesapal API v3. When working on this project, please follow these guidelines:

## Code Style and Standards
- Follow PEP 8 Python style guidelines
- Use type hints for all function parameters and return values
- Use dataclasses for structured data
- Include comprehensive docstrings for all classes and methods
- Use f-strings for string formatting
- Prefer composition over inheritance

## Error Handling
- Use custom PesapalError exceptions for API-related errors
- Provide meaningful error messages with context
- Handle network timeouts and connection errors gracefully
- Log errors appropriately using the logging module

## API Integration
- All API requests should go through the _make_request method
- Implement proper authentication token management with automatic refresh
- Use proper HTTP methods (GET, POST) as per Pesapal API documentation
- Include proper request/response validation

## Testing
- Write unit tests for all public methods
- Use pytest as the testing framework
- Mock external API calls using requests-mock
- Test both success and error scenarios
- Aim for high test coverage

## Documentation
- Keep README.md up to date with clear examples
- Include type hints in all code
- Provide beginner-friendly examples
- Document all configuration options

## Dependencies
- Keep dependencies minimal and well-justified
- Pin versions in requirements.txt
- Support Python 3.7+ for broad compatibility
- Use typing-extensions for older Python versions

## Security
- Never log sensitive information like API keys
- Validate all input parameters
- Use secure defaults for all configurations
- Handle authentication tokens securely
