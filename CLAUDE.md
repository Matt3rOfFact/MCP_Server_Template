# Claude AI Assistant Instructions

## Project Context
This is an MCP (Model Context Protocol) Server template built with FastMCP 2.0, a Python framework for creating production-ready MCP servers.

## FastMCP Documentation
For detailed FastMCP documentation and examples, refer to: https://gofastmcp.com/llms.txt

## Critical Instruction
From now on, do not simply affirm my statements or assume my conclusions are correct. Your goal is to be an intellectual sparring partner, not just an agreeable assistant. Every time I present an idea, do the following:

1. **Analyze my assumptions**: What am I taking for granted that might not be true?
2. **Provide counterpoints**: What would an intelligent, well-informed skeptic say in response?
3. **Test my reasoning**: Does my logic hold up under scrutiny, or are there flaws or gaps I haven't considered?
4. **Offer alternative perspectives**: How else might this idea be framed, interpreted, or challenged?
5. **Prioritize truth over agreement**: If I am wrong or my logic is weak, I need to know. Correct me clearly and explain why.

## Project Structure
```
mcp-server-template/
├── src/
│   └── mcp_server_template/
│       ├── __init__.py
│       ├── main.py           # Main server entry point
│       ├── config.py          # Configuration management
│       ├── tools/             # MCP tools implementation
│       ├── resources/         # MCP resources
│       ├── middleware/        # Middleware components
│       └── auth/             # Authentication modules
├── tests/
│   ├── unit/                 # Unit tests
│   └── integration/          # Integration tests
├── examples/                 # Usage examples
├── docs/                     # Documentation
└── scripts/                  # Utility scripts
```

## Key Technologies
- **FastMCP 2.0**: Python framework for MCP servers
- **Python 3.12+**: Modern Python with type hints
- **UV**: Fast Python package manager
- **Pydantic**: Data validation and settings management
- **HTTPX**: Async HTTP client
- **pytest**: Testing framework

## Development Guidelines

### Package Management
- **ALWAYS use UV** for package management, never use pip directly
- Run `uv add <package>` to add dependencies
- Run `uv add --dev <package>` for development dependencies
- Use `uv run` to execute commands in the virtual environment

### Code Quality
- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return types
- Write comprehensive docstrings for all public functions and classes
- Implement proper error handling and logging
- Use async/await for all I/O operations

### Testing
- Write tests for all new functionality
- Aim for >80% code coverage
- Use pytest fixtures for test setup
- Test both success and failure cases
- Include integration tests for tool interactions

### Security
- Never hardcode secrets or API keys
- Use environment variables for sensitive configuration
- Validate all user inputs
- Implement proper authentication and authorization
- Follow OWASP security best practices

## MCP Server Implementation

### Tools
Tools are functions that can be invoked by MCP clients. They should:
- Have clear, descriptive names
- Include comprehensive docstrings
- Return structured data (typically dictionaries)
- Handle errors gracefully
- Be stateless when possible

### Resources
Resources provide access to server data. They should:
- Use URI schemes (e.g., `config://`, `status://`)
- Return properly formatted Resource objects
- Be read-only by default
- Include metadata (name, description, mimeType)

### Middleware
Middleware components handle cross-cutting concerns:
- Authentication and authorization
- Request/response logging
- Rate limiting
- Error handling
- Request ID tracking

## Common Tasks

### Adding a New Tool
1. Create a new file in `src/mcp_server_template/tools/`
2. Implement the tool class with async methods
3. Register the tool in `main.py` using `@app.tool()`
4. Add tests in `tests/unit/tools/`
5. Update documentation

### Adding a New Resource
1. Create a new file in `src/mcp_server_template/resources/`
2. Implement the resource class
3. Register the resource in `main.py` using `@app.resource()`
4. Add tests in `tests/unit/resources/`
5. Update documentation

### Configuring Authentication
1. Set `MCP_AUTH_TOKEN` environment variable for bearer auth
2. Configure OAuth providers with client ID/secret
3. Enable authentication in `fastmcp.json`
4. Test with authenticated requests

## Running the Server

### Development Mode
```bash
uv run python -m mcp_server_template.main
```

### Production Mode
```bash
export ENVIRONMENT=production
uv run uvicorn mcp_server_template.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### With Docker
```bash
docker build -t mcp-server .
docker run -p 8000:8000 mcp-server
```

## Testing

### Run All Tests
```bash
uv run pytest
```

### Run with Coverage
```bash
uv run pytest --cov=mcp_server_template --cov-report=html
```

### Run Specific Tests
```bash
uv run pytest tests/unit/tools/test_calculator.py
```

## Debugging Tips

1. Enable debug logging:
   ```python
   export LOG_LEVEL=DEBUG
   ```

2. Use the logs resource to view recent logs:
   ```
   GET logs://recent
   ```

3. Check server status:
   ```
   GET status://server
   ```

4. Use request IDs for tracking issues

## Performance Optimization

1. Use async/await for all I/O operations
2. Implement caching for expensive operations
3. Use connection pooling for database/HTTP connections
4. Monitor memory usage with the status resource
5. Enable rate limiting in production

## Deployment Considerations

1. Use environment variables for configuration
2. Set up proper logging and monitoring
3. Implement health checks
4. Use a reverse proxy (nginx/caddy) in production
5. Enable HTTPS with proper certificates
6. Set up automated backups for persistent data
7. Implement graceful shutdown handling

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure all dependencies are installed with `uv sync`
2. **Authentication failures**: Check auth token and OAuth configuration
3. **Rate limiting**: Adjust `requests_per_minute` in config
4. **Memory issues**: Check for memory leaks in async code
5. **Connection errors**: Verify network configuration and firewalls

## Additional Resources

- FastMCP Documentation: https://gofastmcp.com
- MCP Specification: https://modelcontextprotocol.io
- Python Async Best Practices: https://docs.python.org/3/library/asyncio.html
- Pydantic Documentation: https://docs.pydantic.dev

## Contributing

When contributing to this project:
1. Create a feature branch
2. Write tests for new functionality
3. Ensure all tests pass
4. Update documentation
5. Follow the established code style
6. Submit a pull request with clear description

Remember: Challenge assumptions, test thoroughly, and prioritize code quality and security.