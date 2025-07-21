# MCP Server Test Suite

This directory contains the comprehensive test suite for the MCP (Model Context Protocol) servers. The tests are organized into two categories: **offline tests** and **online tests**.

## Test Organization

### 📁 Offline Tests (`test_offline.py`)
Tests that can run without live MCP servers or endpoints. These are safe to run in CI/CD environments.

**Categories:**
- **Configuration Tests** - Configuration structure and validation
- **Environment Tests** - Environment setup and dependencies
- **Config Validation Tests** - Configuration file validation
- **File Structure Tests** - File structure and import validation

### 🌐 Online Tests (`test_online.py`)
Tests that require live MCP servers and external endpoints. These should NOT be run in CI environments.

**Categories:**
- **Integration Tests** - Real MCP server integration
- **Health Tests** - Server health and connectivity
- **Basic Server Functionality** - Sentiment analysis and text processing
- **Code Metrics Functionality** - Complexity and style analysis
- **Code Security Functionality** - Vulnerability detection
- **Code Retrieval Functionality** - URL validation and content retrieval
- **Git Server Functionality** - Git operations and repository analysis
- **Integration Scenarios** - Complex workflows and scenarios

## Test Runners

### Main Test Runner (`run_tests.py`)
Unified test runner that can execute both offline and online tests.

```bash
# Run all tests (offline + online)
python tests/run_tests.py all

# Run only offline tests
python tests/run_tests.py offline

# Run only online tests
python tests/run_tests.py online

# Run quick tests (configuration + environment)
python tests/run_tests.py quick

# Run health tests
python tests/run_tests.py health

# Run functionality tests
python tests/run_tests.py functionality

# Run integration tests
python tests/run_tests.py integration

# List available test suites
python tests/run_tests.py list

# List all test categories
python tests/run_tests.py list-categories

# List test scenarios
python tests/run_tests.py list-scenarios

# Validate environment
python tests/run_tests.py validate

# Run with verbose output
python tests/run_tests.py all --verbose

# Generate detailed report
python tests/run_tests.py all --report

# Force offline-only mode (safe for CI)
python tests/run_tests.py all --offline-only

# Force online-only mode (requires servers)
python tests/run_tests.py all --online-only
```

### Offline Test Runner (`run_offline_tests.py`)
Dedicated runner for offline tests only.

```bash
# Run all offline tests
python tests/run_offline_tests.py all

# Run specific category
python tests/run_offline_tests.py configuration
python tests/run_offline_tests.py environment
python tests/run_offline_tests.py config_validation
python tests/run_offline_tests.py file_structure

# List categories
python tests/run_offline_tests.py list

# Verbose output
python tests/run_offline_tests.py all --verbose

# Generate report
python tests/run_offline_tests.py all --report
```

### Online Test Runner (`run_online_tests.py`)
Dedicated runner for online tests only.

```bash
# Set API key first
export TOGETHER_API_KEY="your-api-key"

# Start all servers
python start_all_servers.py

# Run all online tests
python tests/run_online_tests.py all

# Run specific category
python tests/run_online_tests.py health
python tests/run_online_tests.py functionality
python tests/run_online_tests.py integration

# List categories
python tests/run_online_tests.py list

# Verbose output
python tests/run_online_tests.py all --verbose

# Generate report
python tests/run_online_tests.py all --report
```

## Test Scenarios

The test suite includes predefined scenarios that test complex workflows:

```bash
# List available scenarios
python tests/run_tests.py list-scenarios

# Run a specific scenario
python tests/run_tests.py code_review_workflow
python tests/run_tests.py ci_cd_workflow
python tests/run_tests.py multi_language_support
```

## CI/CD Integration

### GitHub Actions
The CI pipeline runs only offline tests to ensure reliability:

```yaml
- name: Run offline tests
  run: |
    python tests/run_tests.py offline --verbose
```

### Local Development
For local development, you can run the full test suite:

```bash
# Quick validation (offline only)
python tests/run_tests.py quick

# Full offline validation
python tests/run_tests.py offline

# Full online validation (requires servers)
python tests/run_tests.py online

# Complete test suite
python tests/run_tests.py all
```

## Prerequisites

### For Offline Tests
- Python 3.8+
- Required Python packages (see `requirements.txt`)
- Valid configuration file (`config.json`)

### For Online Tests
- All prerequisites for offline tests
- `TOGETHER_API_KEY` environment variable set
- All MCP servers running
- Network connectivity to external endpoints

## Test Categories Details

### Offline Test Categories

#### Configuration Tests
- Config structure validation
- Server URL format validation
- Port uniqueness validation
- Model configuration validation

#### Environment Tests
- Environment variable access
- Dependency availability
- Configuration validation
- Python version compatibility

#### Config Validation Tests
- Config file existence
- JSON validity
- Server config completeness
- Model parameters structure

#### File Structure Tests
- Server module imports
- Client module imports
- Required file existence
- Directory structure validation

### Online Test Categories

#### Integration Tests
- Server connectivity
- Tools availability
- MCP client integration

#### Health Tests
- Server health checks
- MCP endpoint accessibility
- Response time validation

#### Basic Server Functionality
- Sentiment analysis (positive/negative/neutral)
- Text processing capabilities

#### Code Metrics Functionality
- Complexity analysis
- Style analysis
- Naming conventions
- Error handling analysis

#### Code Security Functionality
- SQL injection detection
- Command injection detection
- Code injection detection
- Hardcoded secrets detection

#### Code Retrieval Functionality
- URL validation
- Content retrieval
- File content analysis
- Batch file retrieval

#### Git Server Functionality
- Git status operations
- Git log retrieval
- Git branch operations
- Git add/commit operations

#### Integration Scenarios
- Code review workflows
- CI/CD workflows
- Multi-language support
- Large codebase analysis

## Troubleshooting

### Offline Tests Failing
- Check configuration file structure
- Verify all required files exist
- Ensure Python version compatibility
- Check import dependencies

### Online Tests Failing
- Verify all servers are running
- Check `TOGETHER_API_KEY` is set
- Ensure network connectivity
- Verify server URLs are correct

### Common Issues
- **Import errors**: Make sure you're running from the project root
- **Configuration errors**: Validate your `config.json` file
- **Server connection errors**: Ensure all MCP servers are running
- **API key errors**: Set the `TOGETHER_API_KEY` environment variable

## Test Reports

All test runners support detailed reporting:

```bash
# Generate detailed report
python tests/run_tests.py all --report

# Save report to file
python tests/run_tests.py all --report > test_report.txt
```

Reports include:
- Test execution summary
- Pass/fail statistics
- Detailed results by category
- Performance metrics
- Error details

## Best Practices

1. **Always run offline tests** in CI/CD pipelines
2. **Run online tests locally** before deploying
3. **Use quick tests** for fast validation during development
4. **Run full test suite** before major releases
5. **Check test reports** for detailed analysis
6. **Validate environment** before running online tests

## Migration Notes

The test suite has been reorganized from the original structure:

**Original Files → New Organization:**
- `test_config.py` → `test_offline.py` (configuration tests)
- `test_mcp_integration.py` → Split between `test_offline.py` and `test_online.py`
- `test_server_functionality.py` → `test_online.py` (functionality tests)

**Benefits of Reorganization:**
- Clear separation between offline and online tests
- CI/CD compatibility with offline tests
- Better organization and maintainability
- Unified test runner interface
- Comprehensive reporting capabilities
