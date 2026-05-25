from tests.utils import run_node

BLOG = {"id": "b1", "title": "First", "author": "Ada", "url": "https://example.com", "likes": 3}


def test_blog_views():
    listing = run_node("bloglist/views/blogs.js", "buildBlogList", [[BLOG]])
    assert listing["ok"]
    assert listing["result"][0]["title"] == "First"
    detail = run_node("bloglist/views/blogs.js", "buildBlogDetail", [BLOG])
    assert detail["ok"]
    assert detail["result"]["likes"] == 3
