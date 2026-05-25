from tests.utils import run_node


def test_pipeline_workflow_contains_steps():
    result = run_node("workflows/pipeline.js", "buildPipelineWorkflow")
    assert result["ok"]
    text = result["result"]
    assert "npm run lint" in text
    assert "npm run build" in text
    assert "npm test" in text
    assert "test:e2e" in text
    assert "pull_request" in text
    assert "github.event_name" in text
