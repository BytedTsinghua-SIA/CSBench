from .utils import load_parser, load_sentence


def test_parse_sentence_6():
    parser = load_parser()
    words = parser.preprocess(load_sentence("6.txt"))
    trees = list(parser.parser.parse(words))
    assert trees
