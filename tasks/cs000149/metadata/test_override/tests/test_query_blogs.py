from tests.utils import run_node

BLOGS = [
    {"id": "1", "likes": 1},
    {"id": "2", "likes": 2},
]


def test_query_cache_updates():
    added = run_node(
        "bloglist/state/query/blogs.js",
        "addBlogToCache",
        [BLOGS, {"id": "3", "likes": 0}],
    )
    assert added["ok"]
    assert len(added["result"]) == 3
    liked = run_node(
        "bloglist/state/query/blogs.js",
        "updateBlogLikes",
        [BLOGS, "1"],
    )
    assert liked["ok"]
    assert liked["result"][0]["likes"] == 2
    removed = run_node(
        "bloglist/state/query/blogs.js",
        "removeBlogFromCache",
        [BLOGS, "2"],
    )
    assert removed["ok"]
    assert len(removed["result"]) == 1
