import pytest
from app.api.hooks import compare_metrics, OpensMetrics, reset_hook_store


def test_compare_metrics_same_values():
    """Compare two identical metric sets should return empty delta."""
    before = [OpensMetrics(session_type="main", total_prompts=3, open_count=2, opens_per_100=66.67, router_count=1, playbook_count=0, principle_count=0)]
    after = [OpensMetrics(session_type="main", total_prompts=3, open_count=2, opens_per_100=66.67, router_count=1, playbook_count=0, principle_count=0)]
    delta = compare_metrics(before, after)
    assert delta == {}


def test_compare_metrics_different_opens():
    """Compare metrics where open_count changed."""
    before = [OpensMetrics(session_type="main", total_prompts=3, open_count=2, opens_per_100=66.67, router_count=1, playbook_count=0, principle_count=0)]
    after = [OpensMetrics(session_type="main", total_prompts=3, open_count=3, opens_per_100=100.0, router_count=1, playbook_count=0, principle_count=0)]
    delta = compare_metrics(before, after)
    assert delta["main"]["open_count"] == 1  # 3 - 2
    assert delta["main"]["opens_per_100"] == 33.33  # 100.0 - 66.67


def test_compare_metrics_new_session_type():
    """Compare metrics where a new session type appears in after."""
    before = []
    after = [OpensMetrics(session_type="subagent", total_prompts=3, open_count=2, opens_per_100=66.67, router_count=0, playbook_count=1, principle_count=0)]
    delta = compare_metrics(before, after)
    assert "subagent" in delta
    assert delta["subagent"]["open_count"] == 2
    assert delta["subagent"]["playbook_count"] == 1


def test_compare_metrics_router_increase():
    """Compare metrics where router_count increased."""
    before = [OpensMetrics(session_type="main", total_prompts=4, open_count=1, opens_per_100=25.0, router_count=1, playbook_count=0, principle_count=0)]
    after = [OpensMetrics(session_type="main", total_prompts=4, open_count=1, opens_per_100=25.0, router_count=3, playbook_count=0, principle_count=0)]
    delta = compare_metrics(before, after)
    assert delta["main"]["router_count"] == 2  # 3 - 1
