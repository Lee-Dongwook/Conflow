"""
Supervisor Agent Graph Definition.

This module defines the LangGraph for the Supervisor Agent, which orchestrates
various worker agents to achieve complex tasks. It includes the graph state,
nodes for calling worker agents and making decisions, and the graph's
conditional edges.
"""

from typing import Literal

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict


class AgentState(TypedDict):
    """
    Represents the state of the agent's current task and conversation history.

    Attributes:
        current_task (str): The description of the current task the supervisor is managing.
        agent_output (str): The output received from the last executed worker agent.
        chat_history (List[BaseMessage]): A history of the conversation or interactions.
        next_agent (Literal["meeting_summary", "blocker_triage", "retro_insights", "FINISH", "REVISE"]):
            The name of the next agent to call, or a special action.
    """  # noqa: E501
    current_task: str
    agent_output: str
    chat_history: list[BaseMessage]
    next_agent: Literal["meeting_summary", "blocker_triage", "retro_insights", "FINISH", "REVISE", "DELEGATE"]  # noqa: E501

# --- Nodes Definition ---

def call_worker_agent_node(state: AgentState) -> AgentState:
    """
    A placeholder node that simulates calling a specific worker agent
    based on the 'next_agent' in the state.
    """
    next_agent_to_call = state['next_agent']
    current_task = state['current_task']

    print(f"--- Supervisor: Calling Worker Agent: {next_agent_to_call} for task: {current_task} ---")

    # TODO: Replace with actual calls to worker agents based on next_agent_to_call
    # For now, it's a mock output
    mock_output = f"Mock output from {next_agent_to_call} for '{current_task}'."
    new_history = state.get("chat_history", []) + [HumanMessage(content=mock_output)]

    return {
        "agent_output": mock_output,
        "chat_history": new_history,
        "next_agent": "REVISE" # After a worker, always go to decision node for next step
    }

def decide_next_step_node(state: AgentState) -> Literal["meeting_summary", "blocker_triage", "retro_insights", "FINISH", "REVISE", "DELEGATE"]:
    """
    Decides the next step based on the current task, agent output, and history.
    This node acts as the brain of the supervisor, determining if more work is needed,
    if a different agent should be called, or if the overall task is complete.
    """
    current_task = state['current_task']
    agent_output = state['agent_output']
    chat_history = state['chat_history']

    print(f"--- Supervisor: Deciding next step for task: '{current_task}' with output: '{agent_output}' ---")

    # TODO: Implement complex decision logic here.
    # This might involve:
    # 1. Parsing agent_output for keywords (e.g., "summary complete", "blocker found").
    # 2. Using an LLM call to decide based on current_task and chat_history.
    # 3. Checking predefined rules or a state machine.

    # For the initial draft, let's have a simple decision flow:
    if "Meeting summary" in current_task and "summary complete" not in agent_output:
        print("Decision: Need Meeting Summary Agent.")
        return "meeting_summary"
    elif "blocker" in current_task.lower() and "blocker found" not in agent_output:
        print("Decision: Need Blocker Triage Agent.")
        return "blocker_triage"
    elif "retro" in current_task.lower() and "insights generated" not in agent_output:
        print("Decision: Need Retro Insights Agent.")
        return "retro_insights"
    elif "mock output" in agent_output:
        # If we just got a mock output, let's simulate a revision or finish
        if "summary complete" in agent_output or "blocker found" in agent_output or "insights generated" in agent_output:
            print("Decision: Task seems complete (mock). Finishing.")
            return "FINISH"
        else:
            print("Decision: Output received, but task not complete. Delegating (mock).")
            return "DELEGATE" # Or REVISE, depending on next steps
    else:
        print("Decision: Unknown state or task complete. Finishing.")
        return "FINISH"

# --- Graph Definition ---

# Initialize the StateGraph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("call_worker_agent", call_worker_agent_node)
workflow.add_node("decide_next_step", decide_next_step_node)

# Set entry point
workflow.set_entry_point("decide_next_step")

# Define edges
# The supervisor always decides first.
# If the decision is to call a worker, it transitions to 'call_worker_agent'.
workflow.add_conditional_edges(
    "decide_next_step",
    decide_next_step_node,
    {
        "meeting_summary": "call_worker_agent",
        "blocker_triage": "call_worker_agent",
        "retro_insights": "call_worker_agent",
        "DELEGATE": "call_worker_agent", # Delegate to a generic worker or another round of decision
        "FINISH": END,
        "REVISE": "decide_next_step", # Loop back to decide if revision is needed
    },
)

# After a worker agent is called, it always returns to the decision node.
workflow.add_edge("call_worker_agent", "decide_next_step")


# LangGraph API (`langgraph dev`) manages persistence — do not pass a custom checkpointer.
supervisor_agent_graph = workflow.compile()

if __name__ == "__main__":
    print("--- Running Supervisor Agent Graph Example ---")

    # Example 1: Meeting Summary Task
    print("\n[Example 1: Meeting Summary Task]")
    initial_state_1 = {
        "current_task": "Generate a meeting summary for the last standup.",
        "agent_output": "",
        "chat_history": [HumanMessage(content="Please summarize the standup meeting.")]
    }
    for s in supervisor_agent_graph.stream(initial_state_1):
        print(s)
        print("---")

    # Example 2: Blocker Triage Task (simulating a specific output)
    print("\n[Example 2: Blocker Triage Task]")
    initial_state_2 = {
        "current_task": "Identify any blockers from the team's progress.",
        "agent_output": "",
        "chat_history": [HumanMessage(content="Are there any blockers?")]
    }
    for s in supervisor_agent_graph.stream(initial_state_2):
        print(s)
        print("---")
    
    # Example 3: Task completion
    print("\n[Example 3: Task Completion]")
    initial_state_3 = {
        "current_task": "Review and finalize the quarterly report.",
        "agent_output": "The quarterly report is finalized and ready for submission.",
        "chat_history": [HumanMessage(content="Finalize quarterly report.")]
    }
    for s in supervisor_agent_graph.stream(initial_state_3):
        print(s)
        print("---")
    
    print("\n--- Supervisor Agent Graph Example Finished ---")
