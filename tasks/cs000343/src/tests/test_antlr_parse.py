from pathlib import Path
import os
import subprocess


def test_antlr_parse(tmp_path):
    root = Path(__file__).resolve().parents[1]
    antlr_jar = root / "lib" / "antlr.jar"
    abc_g4 = root / "src" / "abc" / "parser" / "Abc.g4"
    gen_dir = tmp_path / "gen"
    gen_dir.mkdir()

    subprocess.run(
        [
            "java",
            "-jar",
            str(antlr_jar),
            "-o",
            str(gen_dir),
            str(abc_g4),
        ],
        check=True,
        capture_output=True,
    )

    harness_code = """
    package abc.parser;

    import org.antlr.v4.runtime.BaseErrorListener;
    import org.antlr.v4.runtime.ANTLRInputStream;
    import org.antlr.v4.runtime.CommonTokenStream;
    import org.antlr.v4.runtime.RecognitionException;
    import org.antlr.v4.runtime.Recognizer;

    public class ParseHarness {
        public static void main(String[] args) {
            ANTLRInputStream input = new ANTLRInputStream("+");
            AbcLexer lexer = new AbcLexer(input);
            CommonTokenStream tokens = new CommonTokenStream(lexer);
            AbcParser parser = new AbcParser(tokens);
            parser.removeErrorListeners();
            parser.addErrorListener(new BaseErrorListener() {
                @Override
                public void syntaxError(Recognizer<?, ?> recognizer, Object offendingSymbol,
                                        int line, int charPositionInLine,
                                        String msg, RecognitionException e) {
                    throw new RuntimeException("syntax error");
                }
            });
            parser.line();
            System.out.println("OK");
        }
    }
    """

    harness_path = tmp_path / "ParseHarness.java"
    harness_path.write_text(harness_code)

    java_files = [str(path) for path in gen_dir.rglob("*.java")]
    cmd = [
        "javac",
        "-cp",
        str(antlr_jar),
        "-d",
        str(tmp_path),
        str(harness_path),
    ] + java_files
    subprocess.run(cmd, check=True, capture_output=True)

    result = subprocess.run(
        [
            "java",
            "-cp",
            f"{tmp_path}{os.pathsep}{antlr_jar}",
            "abc.parser.ParseHarness",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip() == "OK"
