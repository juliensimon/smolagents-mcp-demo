# MCP Server Test Suite

This directory contains a comprehensive test suite for the MCP (Model Context Protocol) servers. The test suite is designed to validate server functionality, integration, performance, and security.

## Overview

The test suite consists of multiple test categories and scenarios:

- **Integration Tests**: Real MCP server integration using actual MCP clients
- **Functionality Tests**: Detailed tests for each server's specific capabilities
- **Health Tests**: Server connectivity and responsiveness checks
- **Configuration Tests**: Configuration validation and loading
- **Environment Tests**: Environment setup and dependency checks
- **Scenario Tests**: Complex integration workflows and use cases

## Test Categories

### Core Test Categories

1. **integration** - Real MCP server integration tests
2. **configuration** - Configuration validation tests
3. **environment** - Environment setup tests
4. **health** - Server health and connectivity tests
5. **scenarios** - Complex integration scenarios and workflows

### Functionality Test Categories

6. **basic_functionality** - Detailed basic server functionality tests
7. **code_metrics_functionality** - Detailed code metrics server functionality tests
8. **code_security_functionality** - Detailed code security server functionality tests
9. **code_retrieval_functionality** - Detailed code retrieval server functionality tests
10. **git_functionality** - Detailed git server functionality tests

## Test Scenarios

The test suite includes predefined scenarios for different testing purposes:

- **smoke** - Basic functionality tests to ensure servers are working
- **integration** - Full integration tests with all servers
- **functionality** - Detailed functionality tests for each server
- **performance** - Performance and stress tests
- **security** - Security-focused tests
- **full** - Complete test suite with all categories

## Prerequisites

Before running the tests, ensure:

1. **Environment Variables**:
   ```bash
   export TOGETHER_API_KEY="your_together_api_key_here"
   ```

2. **Python Dependencies**:
   ```bash
   pip install smolagents requests gradio textblob psutil
   ```

3. **Server Status**: All MCP servers should be running and accessible

## Running Tests

### Basic Usage

```bash
# Run all tests
python tests/run_tests.py

# Run with verbose output
python tests/run_tests.py --verbose

# Generate detailed report
python tests/run_tests.py --report
```

### Test Categories

```bash
# Run specific test category
python tests/run_tests.py integration
python tests/run_tests.py health
python tests/run_tests.py functionality

# Run quick tests (environment and configuration only)
python tests/run_tests.py quick

# Run core tests (integration and scenarios)
python tests/run_tests.py core
```

### Test Scenarios

```bash
# Run specific scenario
python tests/run_tests.py smoke
python tests/run_tests.py integration
python tests/run_tests.py functionality
python tests/run_tests.py performance
python tests/run_tests.py security
python tests/run_tests.py full
```

### Utility Commands

```bash
# List all available test categories
python tests/run_tests.py list

# List all available test scenarios
python tests/run_tests.py list-scenarios

# Validate environment setup
python tests/run_tests.py validate
```

## Test Files

### Main Test Files

- **`test_mcp_integration.py`** - Main integration tests and core functionality
- **`test_server_functionality.py`** - Detailed server-specific functionality tests
- **`test_config.py`** - Test configuration and scenario definitions
- **`run_tests.py`** - Test runner and orchestration

### Test Structure

```
tests/
├── __init__.py
├── README.md
├── run_tests.py                 # Main test runner
├── test_mcp_integration.py      # Integration tests
├── test_server_functionality.py # Server-specific tests
└── test_config.py              # Test configuration
```

## Test Coverage

### Basic Server Tests
- Sentiment analysis with various text types
- Edge cases and error handling
- Performance benchmarks

### Code Metrics Server Tests
- Code complexity analysis
- Style analysis
- Naming conventions
- Error handling patterns
- Documentation quality

### Code Security Server Tests
- Command injection detection
- SQL injection detection
- Code injection detection
- Safe code analysis

### Code Retrieval Server Tests
- URL validation (valid and invalid)
- Content retrieval from various sources
- Error handling for network issues

### Git Server Tests
- Repository status analysis
- Git log analysis
- Branch operations
- Commit history analysis

### Integration Tests
- End-to-end workflows
- Multi-server interactions
- Performance testing
- Concurrent request handling
- Memory usage monitoring

## Test Data

The test suite includes comprehensive test data for various scenarios:

### Sentiment Analysis Data
- Positive, negative, neutral, and mixed sentiment texts
- Edge cases (empty strings, special characters, unicode)

### Code Analysis Data
- Simple and complex code examples
- Vulnerable and safe code patterns
- Various programming language constructs

### URL Test Data
- Valid and invalid URLs
- Different protocols and formats

## Performance Testing

The test suite includes performance benchmarks:

- Response time measurements
- Memory usage monitoring
- Concurrent request handling
- Load testing capabilities

## Error Handling

Tests include comprehensive error handling:

- Invalid inputs
- Network failures
- Server unavailability
- Timeout scenarios
- Resource exhaustion

## Configuration

Test configuration is managed through `test_config.py`:

- Test scenarios and categories
- Performance thresholds
- Environment requirements
- Test data definitions

## Reporting

The test suite provides detailed reporting:

- Test execution summaries
- Performance metrics
- Error details
- Environment validation results

## Continuous Integration

The test suite is designed for CI/CD integration:

- Exit codes for automation
- Structured output
- Configurable timeouts
- Environment validation

## Troubleshooting

### Common Issues

1. **Server Connection Failures**:
   - Ensure all servers are running
   - Check server ports and URLs
   - Verify network connectivity

2. **Environment Issues**:
   - Run `python tests/run_tests.py validate` to check setup
   - Verify API keys are set
   - Check Python version (3.8+ required)

3. **Test Failures**:
   - Check server logs for errors
   - Verify test data is accessible
   - Review timeout settings

### Debug Mode

Run tests with verbose output for detailed debugging:

```bash
python tests/run_tests.py --verbose
```

### Individual Test Execution

Run specific test classes directly:

```bash
# Run integration tests only
python -m unittest tests.test_mcp_integration.TestMCPIntegration

# Run specific test method
python -m unittest tests.test_mcp_integration.TestMCPIntegration.test_server_connectivity
```

## Contributing

When adding new tests:

1. Follow the existing test structure
2. Add appropriate test data to `test_config.py`
3. Update test categories if needed
4. Include both positive and negative test cases
5. Add performance considerations for new functionality

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Resource Cleanup**: Clean up temporary files and connections
3. **Error Handling**: Test both success and failure scenarios
4. **Performance**: Monitor response times and resource usage
5. **Documentation**: Document complex test scenarios

## Support

For issues with the test suite:

1. Check the troubleshooting section
2. Review server logs
3. Validate environment setup
4. Check test configuration
5. Review recent changes to server implementations
