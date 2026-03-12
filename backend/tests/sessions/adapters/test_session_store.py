from app.mcp.models import AgentInstruction
from app.sessions.adapters.session_store import SessionStore
from app.sessions.models import SessionStatus

_mk = lambda step: AgentInstruction(  # noqa: E731
    agent="a", system_prompt="s", user_message="m",
    action_required="act", session_id="s1", step=step,
)


def test_create_and_get() -> None:
    store = SessionStore()
    record = store.create("s1", "req")
    assert record.session_id == "s1"
    assert store.get("s1") is record


def test_get_missing() -> None:
    assert SessionStore().get("nope") is None


def test_list_all() -> None:
    store = SessionStore()
    store.create("s1", "r1")
    store.create("s2", "r2")
    assert {r.session_id for r in store.list_all()} == {"s1", "s2"}


def test_append_plan_step() -> None:
    store = SessionStore()
    store.create("s1", "req")
    record = store.append_instruction("s1", _mk("plan"))
    assert record.status == SessionStatus.active


def test_append_test_step() -> None:
    store = SessionStore()
    store.create("s1", "req")
    assert store.append_instruction("s1", _mk("test")).status == SessionStatus.testing


def test_append_implement_step() -> None:
    store = SessionStore()
    store.create("s1", "req")
    assert store.append_instruction("s1", _mk("implement")).status == SessionStatus.implementing


def test_append_review_step() -> None:
    store = SessionStore()
    store.create("s1", "req")
    assert store.append_instruction("s1", _mk("review")).status == SessionStatus.reviewing


def test_append_unknown_step_keeps_status() -> None:
    store = SessionStore()
    store.create("s1", "req")
    assert store.append_instruction("s1", _mk("unknown")).status == SessionStatus.active


def test_set_status() -> None:
    store = SessionStore()
    store.create("s1", "req")
    assert store.set_status("s1", SessionStatus.approved).status == SessionStatus.approved


def test_delete_existing() -> None:
    store = SessionStore()
    store.create("s1", "req")
    assert store.delete("s1") is True
    assert store.get("s1") is None


def test_delete_missing() -> None:
    assert SessionStore().delete("nope") is False
