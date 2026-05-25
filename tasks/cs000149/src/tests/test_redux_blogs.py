from tests.utils import run_node

BLOGS = [
    {"id": "1", "title": "A", "likes": 1},
    {"id": "2", "title": "B", "likes": 2},
]


def test_blog_reducer_like_and_remove():
    liked = run_node(
        "bloglist/state/redux/blogs.js",
        "blogReducer",
        [BLOGS, {"type": "LIKE_BLOG", "payload": "1"}],
    )
    assert liked["ok"]
    assert liked["result"][0]["likes"] == 2
    removed = run_node(
        "bloglist/state/redux/blogs.js",
        "blogReducer",
        [liked["result"], {"type": "REMOVE_BLOG", "payload": "2"}],
    )
    assert removed["ok"]
    assert len(removed["result"]) == 1


def test_blog_action_creators():
    set_action = run_node("bloglist/state/redux/blogs.js", "setBlogs", [BLOGS])
    add_action = run_node("bloglist/state/redux/blogs.js", "addBlog", [{"id": "3"}])
    assert set_action["ok"] and add_action["ok"]
    assert set_action["result"]["type"] == "SET_BLOGS"
    assert add_action["result"]["type"] == "ADD_BLOG"
