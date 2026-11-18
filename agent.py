"""
Safe Task Agent — beginner-friendly demonstration.

This is a local demo, not a production AI agent. It uses a simple rule-based
planner so the safety and control flow are easy to inspect. Tools are simulated:
the agent does not access the internet, send messages, spend money, or modify
files outside its own demo memory.
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Any
import re


@dataclass
class AgentState:
    goal: str
    notes: List[str] = field(default_factory=list)
    steps_taken: List[str] = field(default_factory=list)
    status: str = "running"


@dataclass
class Tool:
    name: str
    description: str
    function: Callable[[str, AgentState], str]
    requires_approval: bool = False


class SafetyGuard:
    """Central place for input, tool, and action safety checks."""

    BLOCKED_PATTERNS = [
        r"\bsteal\b", r"\bhack into\b", r"\bmake a weapon\b",
        r"\bhurt someone\b", r"\bself[- ]harm\b"
    ]

    HIGH_IMPACT_PATTERNS = [
        r"\bsend\b", r"\bdelete\b", r"\bpurchase\b", r"\bpay\b",
        r"\bpublish\b", r"\bsubmit\b", r"\bshare private\b"
    ]

    def check_goal(self, goal: str) -> tuple[bool, str]:
        if not goal or not goal.strip():
            return False, "Please provide a non-empty goal."
        if len(goal) > 500:
            return False, "Goal is too long (maximum 500 characters)."
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, goal, re.IGNORECASE):
                return False, "This demo cannot help with harmful or abusive requests."
        return True, "Goal passed basic input checks."

    def check_tool(self, tool_name: str, allowed_tools: Dict[str, Tool]) -> tuple[bool, str]:
        if tool_name not in allowed_tools:
            return False, "Tool is not on the allowlist."
        return True, "Tool is allowed."

    def needs_human_approval(self, action_text: str, tool: Tool) -> bool:
        if tool.requires_approval:
            return True
        return any(re.search(p, action_text, re.IGNORECASE)
                   for p in self.HIGH_IMPACT_PATTERNS)


class SafeTaskAgent:
    def __init__(self, max_steps: int = 4):
        self.guard = SafetyGuard()
        self.max_steps = max_steps
        self.state: AgentState | None = None

        # Explicit allowlist: only these tools can run.
        self.tools: Dict[str, Tool] = {
            "make_checklist": Tool(
                "make_checklist",
                "Turn a goal into a short checklist.",
                self.make_checklist
            ),
            "save_note": Tool(
                "save_note",
                "Save a note in this demo's in-memory state.",
                self.save_note
            ),
            "draft_message": Tool(
                "draft_message",
                "Prepare a message draft; does not send it.",
                self.draft_message
            ),
        }

    def plan(self, goal: str) -> List[tuple[str, str]]:
        """A small, inspectable planning loop."""
        lowered = goal.lower()
        if "message" in lowered or "email" in lowered:
            return [
                ("draft_message", "Prepare a draft for: " + goal),
                ("save_note", "Record that a draft was prepared.")
            ]
        return [
            ("make_checklist", goal),
            ("save_note", "Record the goal and checklist.")
        ]

    def make_checklist(self, text: str, state: AgentState) -> str:
        items = [
            "Clarify the desired outcome",
            "Break the work into small steps",
            "Check the result against the goal"
        ]
        return "Checklist:\n- " + "\n- ".join(items)

    def save_note(self, text: str, state: AgentState) -> str:
        state.notes.append(text)
        return "Saved a note in temporary in-memory state."

    def draft_message(self, text: str, state: AgentState) -> str:
        return "Draft only (not sent): " + text

    def evaluate_step(self, goal: str, output: str) -> tuple[bool, str]:
        """Simple trajectory/output evaluation."""
        if not output or not output.strip():
            return False, "Tool returned an empty result."
        if len(output) > 2000:
            return False, "Tool output exceeded the demo length limit."
        return True, "Step produced a non-empty, bounded output."

    def run(self, goal: str, approve_high_impact: bool = False) -> Dict[str, Any]:
        ok, reason = self.guard.check_goal(goal)
        if not ok:
            return {"status": "blocked", "reason": reason, "trace": []}

        self.state = AgentState(goal=goal)
        trace = []
        plan = self.plan(goal)

        for index, (tool_name, action_text) in enumerate(plan, start=1):
            if index > self.max_steps:
                self.state.status = "stopped"
                trace.append({"step": index, "event": "max_steps_reached"})
                break

            allowed, tool_reason = self.guard.check_tool(tool_name, self.tools)
            if not allowed:
                self.state.status = "blocked"
                trace.append({"step": index, "event": "tool_blocked", "reason": tool_reason})
                break

            tool = self.tools[tool_name]
            if self.guard.needs_human_approval(action_text, tool):
                if not approve_high_impact:
                    trace.append({
                        "step": index,
                        "tool": tool_name,
                        "event": "waiting_for_human_approval",
                        "message": "No action was taken. Human approval is required."
                    })
                    self.state.status = "needs_approval"
                    break

            output = tool.function(action_text, self.state)
            valid, evaluation = self.evaluate_step(goal, output)
            trace.append({
                "step": index,
                "tool": tool_name,
                "event": "completed" if valid else "output_rejected",
                "evaluation": evaluation,
                "output": output
            })
            self.state.steps_taken.append(tool_name)

            if not valid:
                self.state.status = "stopped"
                break

        else:
            self.state.status = "completed"

        return {
            "status": self.state.status,
            "goal": self.state.goal,
            "memory_notes": list(self.state.notes),
            "steps_taken": list(self.state.steps_taken),
            "trace": trace
        }


if __name__ == "__main__":
    agent = SafeTaskAgent()
    print("SAFE TASK AGENT — demo")
    print("Try: Create a checklist for my study plan")
    user_goal = input("\nYour goal: ").strip()
    result = agent.run(user_goal)
    print("\nRun result:")
    from pprint import pprint
    pprint(result)
