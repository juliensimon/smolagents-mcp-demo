# Test Suite Split: Offline vs Online Tests

This document explains the split of the test suite into two categories: offline tests and online tests.

## Overview

The test suite has been split into two categories to support CI/CD environments where live MCP servers and endpoints are not available:

- **Offline Tests**: Can run without live servers or endpoints
- **Online Tests**: Require live MCP servers and external endpoints

## Offline Tests

### Location
- **Test File**: `tests/test_offline.py`
- **Runner**: `tests/run_offline_tests.py`

### What They Test
- Configuration structure and validation
- Environment setup and dependencies
- File structure and imports
- Configuration file validation
- Python version compatibility

### Categories
1. **Configuration Tests** (`TestConfigurationOffline`)
   - Config structure validation
   - Server URL format validation
   - Port uniqueness validation
   - Model configuration validation

2. **Environment Tests** (`TestEnvironmentOffline`)
   - Environment variable access
   - Dependency availability
   - Configuration validation
   - Python version compatibility

3. **Config Validation Tests** (`TestConfigValidationOffline`)
   - Config file existence
   - JSON validity
   - Server config completeness
   - Model parameters structure

4. **File Structure Tests** (`TestFileStructureOffline`)
   - Server module imports
   - Client module imports
   - Required file existence
   - Directory structure validation

### Running Offline Tests

```bash
# Run all offline tests
python tests/run_offline_tests.py all

# Run specific category
python tests/run_offline_tests.py configuration
python tests/run_offline_tests.py environment
python tests/run_offline_tests.py config_validation
python tests/run_offline_tests.py file_structure

# List available categories
python tests/run_offline_tests.py list

# Verbose output
python tests/run_offline_tests.py all --verbose

# Generate detailed report
python tests/run_offline_tests.py all --report
```

## Online Tests

### Location
- **Test File**: `tests/test_online.py`
- **Runner**: `tests/run_online_tests.py`

### What They Test
- Real MCP server integration
- Server health and connectivity
- Server functionality with live endpoints
- Complex integration scenarios
- Performance and response times

### Categories
1. **Integration Tests** (`TestMCPIntegrationOnline`)
   - Server connectivity
   - Tools availability
   - MCP client integration

2. **Health Tests** (`TestServerHealthOnline`)
   - Server health checks
   - MCP endpoint accessibility
   - Response time validation

3. **Server Functionality Tests**
   - **Basic Server** (`TestBasicServerFunctionalityOnline`)
     - Sentiment analysis
     - Text processing
   - **Code Metrics Server** (`TestCodeMetricsServerFunctionalityOnline`)
     - Complexity analysis
     - Style analysis
   - **Code Security Server** (`TestCodeSecurityServerFunctionalityOnline`)
     - SQL injection detection
     - Command injection detection
   - **Code Retrieval Server** (`TestCodeRetrievalServerFunctionalityOnline`)
     - URL validation
     - Content retrieval
   - **Git Server** (`TestGitServerFunctionalityOnline`)
     - Git status
     - Git log

4. **Integration Scenarios** (`TestIntegrationScenariosOnline`)
   - Code review workflows
   - CI/CD workflows

### Prerequisites
- All MCP servers must be running
- `TOGETHER_API_KEY` environment variable must be set
- External endpoints must be accessible

### Running Online Tests

```bash
# Set API key
export TOGETHER_API_KEY="your-api-key"

# Start all servers first
python start_all_servers.py

# Run all online tests
python tests/run_online_tests.py all

# Run specific category
python tests/run_online_tests.py health
python tests/run_online_tests.py functionality
python tests/run_online_tests.py integration

# List available categories
python tests/run_online_tests.py list

# Verbose output
python tests/run_online_tests.py all --verbose

# Generate detailed report
python tests/run_online_tests.py all --report
```

## CI/CD Integration

### GitHub Actions
The GitHub Actions workflow (`.github/workflows/ci.yml`) has been updated to:

1. **Only run offline tests** in CI environments
2. **Skip online tests** that require live servers
3. **Use the offline test runner** for all CI test runs

### CI Test Execution
```yaml
- name: Run offline tests
  run: |
    python tests/run_offline_tests.py all --verbose
```

### Local Development
For local development, you can run both test suites:

```bash
# Run offline tests (always safe)
python tests/run_offline_tests.py all

# Run online tests (requires servers)
python tests/run_online_tests.py all
```

## Test Migration

### From Original Tests
The original test files have been split as follows:

**Offline Tests** (extracted from):
- `tests/test_config.py` → `tests/test_offline.py`
- `tests/test_mcp_integration.py` (configuration/environment parts) → `tests/test_offline.py`

**Online Tests** (extracted from):
- `tests/test_mcp_integration.py` (integration parts) → `tests/test_online.py`
- `tests/test_server_functionality.py` → `tests/test_online.py`
- `test_real_world_scenarios.py` → `tests/test_online.py`
- `test_multi_agent_prompts.py` → `tests/test_online.py`
- `test_error_handling_debug.py` → `tests/test_online.py`

### Original Test Runner
The original `tests/run_tests.py` remains unchanged and can still be used for local development when all servers are available.

## Benefits

1. **CI/CD Compatibility**: Offline tests can run in any CI environment
2. **Faster CI**: No need to start servers or wait for endpoints
3. **Reliable CI**: No flaky tests due to network issues
4. **Clear Separation**: Easy to understand which tests need what
5. **Local Development**: Full test suite available locally

## Best Practices

1. **Always run offline tests** in CI/CD pipelines
2. **Run online tests locally** before deploying
3. **Keep offline tests comprehensive** to catch configuration issues
4. **Use online tests for integration validation** in development
5. **Document any new tests** in the appropriate category

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
