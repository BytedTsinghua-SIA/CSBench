from tests.utils import run_node


def test_example_checklist_and_custom_plan():
    checklist = run_node("project/checklist.js", "getExampleProjectChecklist")
    assert checklist["ok"]
    steps = checklist["result"]
    assert "npm install" in steps
    assert "npm test" in steps
    assert "npm run lint" in steps
    assert "npm run build" in steps

    plan = run_node("project/checklist.js", "getCustomPipelinePlan", [{"frontend": "frontend", "backend": "backend"}])
    assert plan["ok"]
    assert plan["result"]["frontend"] == "frontend"
    assert "build" in plan["result"]["steps"]
