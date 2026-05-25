from pathlib import Path
import subprocess
import textwrap

ROOT = Path(__file__).resolve().parents[1]
PITCH_JAVA = ROOT / "src" / "abc" / "sound" / "Pitch.java"
SEQUENCE_PLAYER_JAVA = ROOT / "src" / "abc" / "sound" / "SequencePlayer.java"
MAIN_JAVA = ROOT / "src" / "abc" / "player" / "Main.java"


def compile_and_run(tmp_path, class_name, code, sources):
    harness_path = tmp_path / f"{class_name}.java"
    harness_path.write_text(textwrap.dedent(code))

    cmd = ["javac", "-d", str(tmp_path), str(harness_path)] + [str(src) for src in sources]
    subprocess.run(cmd, check=True, capture_output=True)

    result = subprocess.run(
        ["java", "-cp", str(tmp_path), class_name],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout
