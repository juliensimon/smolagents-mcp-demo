#!/usr/bin/env python3
"""
Generate 50 Multi-Agent Prompts and Report
Creates prompts designed to trigger multiple agents simultaneously
"""

import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List

try:
    from gradio_client import Client
except ImportError:
    print("Installing gradio-client...")
    import subprocess

    subprocess.check_call(["pip", "install", "gradio-client"])
    from gradio_client import Client


@dataclass
class PromptResult:
    prompt_id: int
    prompt: str
    final_answer: str
    agents_used: List[str]
    functions_used: List[str]
    response_time: float
    success: bool


class MultiAgentPromptGenerator:
    def __init__(self, base_url: str = "http://127.0.0.1:7861"):
        self.base_url = base_url
        self.client = Client(base_url)

    def send_message(self, message: str) -> Dict[str, Any]:
        """Send a message to the multi-agent client and get response."""
        try:
            result = self.client.predict(
                message, [], api_name="/respond"  # message  # chat_history
            )

            return {"success": True, "response": result}

        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}

    def analyze_response_for_tools(
        self, response: str
    ) -> Dict[str, List[str]]:
        """Analyze response to identify which tools were likely used."""
        tools_used = {
            "Code Analysis Agent": [],
            "Research Agent": [],
            "Web Search Agent": [],
        }

        response_lower = response.lower()

        # Code Analysis Agent tools
        if "sentiment" in response_lower or "polarity" in response_lower:
            tools_used["Code Analysis Agent"].append("sentiment_analysis")
        if "complexity" in response_lower or "cyclomatic" in response_lower:
            tools_used["Code Analysis Agent"].append(
                "calculate_code_complexity"
            )
        if "style" in response_lower or "pep" in response_lower:
            tools_used["Code Analysis Agent"].append("analyze_code_style")
        if "coverage" in response_lower:
            tools_used["Code Analysis Agent"].append(
                "measure_code_coverage_metrics"
            )
        if "naming" in response_lower or "convention" in response_lower:
            tools_used["Code Analysis Agent"].append(
                "analyze_naming_conventions"
            )
        if "maintainability" in response_lower:
            tools_used["Code Analysis Agent"].append(
                "calculate_maintainability_index"
            )
        if "security" in response_lower and (
            "pattern" in response_lower or "vulnerability" in response_lower
        ):
            tools_used["Code Analysis Agent"].append(
                "analyze_security_patterns"
            )
        if "performance" in response_lower:
            tools_used["Code Analysis Agent"].append(
                "calculate_performance_metrics"
            )
        if "documentation" in response_lower:
            tools_used["Code Analysis Agent"].append(
                "analyze_documentation_quality"
            )
        if "duplication" in response_lower:
            tools_used["Code Analysis Agent"].append(
                "calculate_code_duplication"
            )
        if "error handling" in response_lower:
            tools_used["Code Analysis Agent"].append("analyze_error_handling")
        if "sql injection" in response_lower:
            tools_used["Code Analysis Agent"].append("analyze_sql_injection")
        if "command injection" in response_lower:
            tools_used["Code Analysis Agent"].append(
                "analyze_command_injection"
            )
        if (
            "secret" in response_lower
            or "password" in response_lower
            or "api_key" in response_lower
        ):
            tools_used["Code Analysis Agent"].append(
                "analyze_hardcoded_secrets"
            )
        if "path traversal" in response_lower:
            tools_used["Code Analysis Agent"].append("analyze_path_traversal")
        if "deserialization" in response_lower:
            tools_used["Code Analysis Agent"].append(
                "analyze_unsafe_deserialization"
            )
        if "xss" in response_lower or "cross-site" in response_lower:
            tools_used["Code Analysis Agent"].append(
                "analyze_xss_vulnerabilities"
            )
        if "input validation" in response_lower:
            tools_used["Code Analysis Agent"].append(
                "analyze_input_validation"
            )

        # Research Agent tools
        if (
            "git status" in response_lower
            or "commit" in response_lower
            or "branch" in response_lower
        ):
            tools_used["Research Agent"].extend(["git_status", "git_log"])
        if (
            "retrieved" in response_lower
            or "downloaded" in response_lower
            or "content" in response_lower
        ):
            tools_used["Research Agent"].append("retrieve_file_content")
        if "analyzed" in response_lower and "file" in response_lower:
            tools_used["Research Agent"].append("analyze_file_content")

        # Web Search Agent tools
        if "search" in response_lower and (
            "found" in response_lower or "according to" in response_lower
        ):
            tools_used["Web Search Agent"].append("web_search")

        return tools_used

    def test_prompt(self, prompt_id: int, prompt: str) -> PromptResult:
        """Test a specific prompt and return detailed results."""
        print(f"Testing Prompt {prompt_id}/50: {prompt[:100]}...")

        start_time = time.time()
        result = self.send_message(prompt)
        end_time = time.time()

        response_time = end_time - start_time

        if "error" in result:
            return PromptResult(
                prompt_id=prompt_id,
                prompt=prompt,
                final_answer=f"Error: {result['error']}",
                agents_used=[],
                functions_used=[],
                response_time=response_time,
                success=False,
            )

        response = result["response"]

        # Handle tuple response format from Gradio
        if isinstance(response, tuple) and len(response) > 1:
            response_content = (
                response[1][-1]["content"]
                if response[1] and len(response[1]) > 0
                else str(response)
            )
        else:
            response_content = str(response)

        # Analyze which tools were actually used
        tools_used = self.analyze_response_for_tools(response_content)
        actual_agents_used = [
            agent for agent, tools in tools_used.items() if tools
        ]
        actual_functions_used = [
            tool for tools in tools_used.values() for tool in tools
        ]

        success = len(actual_agents_used) > 0

        return PromptResult(
            prompt_id=prompt_id,
            prompt=prompt,
            final_answer=response_content,
            agents_used=actual_agents_used,
            functions_used=actual_functions_used,
            response_time=response_time,
            success=success,
        )

    def generate_50_prompts(self):
        """Generate 50 prompts designed to trigger multiple agents."""
        prompts = [
            # 1-10: Code Analysis + Research Agent combinations
            "Analyze the code complexity and maintainability of config_loader.py, then get its git history to see recent changes.",
            "Retrieve the content of start_all_servers.py, analyze its security patterns, and check for any hardcoded secrets.",
            "Get the git status of the project, then analyze the code style and documentation quality of the main configuration files.",
            "Analyze the performance metrics of the client code, retrieve the file content, and check for code duplication issues.",
            "Search for Python security best practices, then analyze our server code for SQL injection and command injection vulnerabilities.",
            "Get the git log for recent commits, then analyze the error handling patterns and naming conventions in the codebase.",
            "Retrieve and analyze the content of logging_utils.py for security vulnerabilities, then check its maintainability index.",
            "Analyze the sentiment of code comments in our files, get the git status, and check for any path traversal vulnerabilities.",
            "Search for API security guidelines, then analyze our endpoint code for XSS vulnerabilities and input validation issues.",
            "Get the git history of config.json, analyze its structure for security patterns, and check for any unsafe deserialization.",
            # 11-20: Web Search + Code Analysis combinations
            "Search for latest developments in MCP protocol, then analyze our implementation for compliance with best practices.",
            "Find information about Python performance optimization, then analyze our server startup code for efficiency improvements.",
            "Search for security vulnerabilities in Gradio applications, then audit our interface code for similar issues.",
            "Look up best practices for error handling in Python, then analyze our error handling patterns and suggest improvements.",
            "Search for code quality metrics and standards, then evaluate our codebase against these standards.",
            "Find information about secure configuration management, then analyze our config_loader.py for security compliance.",
            "Search for Git workflow best practices, then analyze our repository structure and commit patterns.",
            "Look up documentation standards for Python projects, then evaluate our documentation quality and coverage.",
            "Search for testing best practices, then analyze our test files for coverage and quality metrics.",
            "Find information about logging security, then audit our logging implementation for potential information disclosure.",
            # 21-30: Research + Web Search + Code Analysis combinations
            "Get the git status, search for recent security advisories about our dependencies, then analyze our code for affected vulnerabilities.",
            "Retrieve the content of requirements.txt, search for known vulnerabilities in those packages, then analyze our code for usage patterns.",
            "Get the git log, search for best practices in multi-agent systems, then analyze our agent coordination code.",
            "Retrieve server configuration files, search for deployment security guidelines, then audit our deployment code.",
            "Get the project structure, search for code organization best practices, then analyze our file organization and naming.",
            "Retrieve test files, search for testing security best practices, then analyze our test coverage and security testing.",
            "Get the git history, search for version control security practices, then analyze our repository security.",
            "Retrieve documentation files, search for technical writing standards, then evaluate our documentation quality.",
            "Get the build configuration, search for CI/CD security practices, then analyze our build process security.",
            "Retrieve dependency files, search for dependency management best practices, then analyze our dependency security.",
            # 31-40: Complex multi-agent scenarios
            "Perform a comprehensive security audit: retrieve all Python files, search for current security threats, analyze each file for vulnerabilities, and get git history to track security-related changes.",
            "Code quality assessment: get git status, retrieve main source files, search for code quality standards, analyze complexity and maintainability, check for documentation coverage.",
            "Performance optimization review: search for performance best practices, retrieve performance-critical code, analyze performance metrics, get git history for performance-related changes.",
            "Security compliance check: search for compliance standards, retrieve configuration files, analyze security patterns, get git log for security updates, check for policy violations.",
            "Documentation audit: retrieve all documentation files, search for documentation standards, analyze documentation quality, get git history for documentation changes.",
            "Testing strategy evaluation: retrieve test files, search for testing methodologies, analyze test coverage, get git history for test changes, evaluate test quality.",
            "Deployment security review: search for deployment security guidelines, retrieve deployment scripts, analyze security configurations, get git history for deployment changes.",
            "API security assessment: search for API security standards, retrieve API code, analyze endpoint security, get git history for API changes, check for vulnerabilities.",
            "Error handling audit: search for error handling best practices, retrieve error handling code, analyze error patterns, get git history for error fixes.",
            "Code review workflow: get git status, retrieve changed files, search for review standards, analyze code quality, check for security issues.",
            # 41-50: Advanced multi-agent scenarios
            "Full project health check: get git status and history, retrieve all source files, search for industry best practices, analyze code quality metrics, security vulnerabilities, performance issues, and documentation coverage.",
            "Security incident response: search for incident response procedures, retrieve affected files, analyze security impact, get git history for recent changes, check for similar vulnerabilities.",
            "Code migration planning: search for migration best practices, retrieve legacy code, analyze complexity and dependencies, get git history for evolution, plan migration strategy.",
            "Performance bottleneck analysis: search for performance profiling techniques, retrieve performance-critical code, analyze performance metrics, get git history for performance changes, identify bottlenecks.",
            "Security architecture review: search for security architecture principles, retrieve architectural files, analyze security design, get git history for architectural changes, evaluate security posture.",
            "Compliance audit preparation: search for compliance requirements, retrieve compliance-related files, analyze compliance gaps, get git history for compliance changes, prepare audit documentation.",
            "Technical debt assessment: search for technical debt metrics, retrieve codebase files, analyze debt indicators, get git history for debt accumulation, prioritize debt reduction.",
            "Security training needs: search for security training resources, retrieve security-related code, analyze security knowledge gaps, get git history for security incidents, identify training priorities.",
            "Code optimization strategy: search for optimization techniques, retrieve optimization targets, analyze optimization opportunities, get git history for performance changes, develop optimization plan.",
            "Security monitoring setup: search for monitoring best practices, retrieve monitoring code, analyze monitoring coverage, get git history for security events, design monitoring strategy.",
        ]

        return prompts

    def run_all_prompts(self):
        """Run all 50 prompts and generate comprehensive report."""
        print("🚀 Starting 50 Multi-Agent Prompts Test")
        print(
            "Testing prompts designed to trigger multiple agents simultaneously"
        )

        prompts = self.generate_50_prompts()
        results = []

        for i, prompt in enumerate(prompts, 1):
            result = self.test_prompt(i, prompt)
            results.append(result)

            # Small delay between tests
            time.sleep(2)

            # Progress update every 10 prompts
            if i % 10 == 0:
                print(f"✅ Completed {i}/50 prompts")

        # Generate comprehensive report
        self.generate_report(results)

        return results

    def generate_report(self, results: List[PromptResult]):
        """Generate a comprehensive report of all results."""
        print(f"\n{'='*100}")
        print("📊 COMPREHENSIVE 50-PROMPT REPORT")
        print(f"{'='*100}")

        # Statistics
        successful_tests = sum(1 for r in results if r.success)
        total_agents_used = sum(len(r.agents_used) for r in results)
        total_functions_used = sum(len(r.functions_used) for r in results)
        avg_response_time = sum(r.response_time for r in results) / len(
            results
        )

        print(f"📈 STATISTICS:")
        print(f"✅ Successful prompts: {successful_tests}/50")
        print(f"❌ Failed prompts: {50 - successful_tests}/50")
        print(f"🎭 Total agents triggered: {total_agents_used}")
        print(f"🔧 Total functions called: {total_functions_used}")
        print(f"⏱️ Average response time: {avg_response_time:.2f}s")

        # Agent usage breakdown
        agent_usage = {}
        for result in results:
            for agent in result.agents_used:
                agent_usage[agent] = agent_usage.get(agent, 0) + 1

        print(f"\n📊 AGENT USAGE BREAKDOWN:")
        for agent, count in sorted(
            agent_usage.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"  {agent}: {count} prompts")

        # Function usage breakdown
        function_usage = {}
        for result in results:
            for func in result.functions_used:
                function_usage[func] = function_usage.get(func, 0) + 1

        print(f"\n🔧 FUNCTION USAGE BREAKDOWN:")
        for func, count in sorted(
            function_usage.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"  {func}: {count} calls")

        # Detailed results
        print(f"\n📋 DETAILED RESULTS:")
        for result in results:
            status = "✅" if result.success else "❌"
            agents_str = (
                ", ".join(result.agents_used) if result.agents_used else "None"
            )
            functions_str = (
                ", ".join(result.functions_used)
                if result.functions_used
                else "None"
            )

            print(f"\n{status} Prompt {result.prompt_id}:")
            print(f"  Prompt: {result.prompt}")
            print(f"  Agents: {agents_str}")
            print(f"  Functions: {functions_str}")
            print(f"  Time: {result.response_time:.2f}s")
            print(f"  Answer: {result.final_answer[:200]}...")

        # Save detailed report to file
        self.save_detailed_report(results)

    def save_detailed_report(self, results: List[PromptResult]):
        """Save detailed report to JSON file."""
        report_data = {
            "summary": {
                "total_prompts": len(results),
                "successful_prompts": sum(1 for r in results if r.success),
                "failed_prompts": sum(1 for r in results if not r.success),
                "total_agents_triggered": sum(
                    len(r.agents_used) for r in results
                ),
                "total_functions_called": sum(
                    len(r.functions_used) for r in results
                ),
                "average_response_time": sum(r.response_time for r in results)
                / len(results),
            },
            "results": [
                {
                    "prompt_id": r.prompt_id,
                    "prompt": r.prompt,
                    "final_answer": r.final_answer,
                    "agents_used": r.agents_used,
                    "functions_used": r.functions_used,
                    "response_time": r.response_time,
                    "success": r.success,
                }
                for r in results
            ],
        }

        with open("50_prompts_detailed_report.json", "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"\n💾 Detailed report saved to: 50_prompts_detailed_report.json")


if __name__ == "__main__":
    generator = MultiAgentPromptGenerator()
    results = generator.run_all_prompts()
