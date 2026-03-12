from app.mcp.models import AgentInstruction


def test_agent_instruction_defaults() -> None:
    inst = AgentInstruction(
        agent="dev",
        system_prompt="sys",
        user_message="msg",
        action_required="act",
        session_id="s1",
        step="implement",
    )
    assert inst.context == {}


def test_agent_instruction_with_context() -> None:
    inst = AgentInstruction(
        agent="reviewer",
        system_prompt="s",
        user_message="m",
        action_required="a",
        session_id="s2",
        step="review",
        context={"diff": "---\n+++"},
    )
    assert inst.context["diff"] == "---\n+++"
