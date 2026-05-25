from .utils import load_parser, load_sentence


def test_parse_sentence_2():
    parser = load_parser()
    words = parser.preprocess(load_sentence("2.txt"))
    trees = list(parser.parser.parse(words))
    assert trees
