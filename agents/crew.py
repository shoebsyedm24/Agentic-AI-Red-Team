"""
CrewAI crew definition for the Agentic AI Red Team Lab.

The crew runs in sequential order: each agent's output becomes available
as context for all subsequent agents via the shared memory store.
The Report Agent always runs last and sees everything.

To add a new attack type:
  1. Create a new agent+task in agents/roles/
  2. Import it here and add to the agents/tasks lists
  3. Add target config in campaign.py
"""
import time
from crewai import Crew, Process

from agents.roles.recon_agent import recon_agent, recon_task
from agents.roles.prompt_injection_agent import injection_agent, injection_task
from agents.roles.jailbreak_agent import jailbreak_agent, jailbreak_task
from agents.roles.data_extraction_agent import extraction_agent, extraction_task
from agents.roles.privilege_escalation_agent import privesc_agent, privesc_task
from agents.roles.webattack_agent import webattack_agent, webattack_task
from agents.roles.report_agent import report_agent, report_task

ALL_AGENTS = [
    recon_agent,
    injection_agent,
    jailbreak_agent,
    extraction_agent,
    privesc_agent,
    webattack_agent,
    report_agent,
]

ALL_TASKS = [
    recon_task,
    injection_task,
    jailbreak_task,
    extraction_task,
    privesc_task,
    webattack_task,
    report_task,
]

# Agents relevant per target type — subsets run when attacking a specific target
TARGET_AGENT_MAP = {
    "chatbot": [recon_agent, injection_agent, jailbreak_agent, extraction_agent, report_agent],
    "rag": [recon_agent, injection_agent, extraction_agent, report_agent],
    "agent": [recon_agent, privesc_agent, extraction_agent, report_agent],
    "multiagent": [recon_agent, injection_agent, privesc_agent, report_agent],
    "webagent": [recon_agent, webattack_agent, injection_agent, report_agent],
    "all": ALL_AGENTS,
}
TARGET_TASK_MAP = {
    "chatbot": [recon_task, injection_task, jailbreak_task, extraction_task, report_task],
    "rag": [recon_task, injection_task, extraction_task, report_task],
    "agent": [recon_task, privesc_task, extraction_task, report_task],
    "multiagent": [recon_task, injection_task, privesc_task, report_task],
    "webagent": [recon_task, webattack_task, injection_task, report_task],
    "all": ALL_TASKS,
}


def build_crew(target: str) -> Crew:
    """Build a CrewAI crew for the given target type."""
    agents = TARGET_AGENT_MAP.get(target, ALL_AGENTS)
    tasks = TARGET_TASK_MAP.get(target, ALL_TASKS)

    def _task_pause(output):
        """30s gap between tasks so each agent gets a fresh Groq TPM window."""
        print("[crew] waiting 30s for Groq TPM window to reset...")
        time.sleep(30)

    return Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
        memory=False,
        task_callback=_task_pause,
    )
