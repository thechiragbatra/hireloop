from app.graph import build_graph


def test_build_graph_returns_compiled_graph():
    graph = build_graph()
    assert graph is not None
