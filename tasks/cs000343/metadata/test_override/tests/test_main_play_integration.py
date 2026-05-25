from pathlib import Path
import subprocess

from .java_runner import MAIN_JAVA, PITCH_JAVA


def test_main_play_integration(tmp_path):
    abc_content = """\
X:1
T:Unit Test Tune
M:4/4
L:1/4
Q:1/4=120
K:C
C D E
"""
    abc_path = tmp_path / "sample.abc"
    abc_path.write_text(abc_content)

    stub_sequence = """
    package abc.sound;

    import java.util.ArrayList;
    import java.util.List;
    import javax.sound.midi.InvalidMidiDataException;
    import javax.sound.midi.MidiUnavailableException;

    public class SequencePlayer {
        public static SequencePlayer lastInstance;
        public final List<String> events = new ArrayList<>();

        public SequencePlayer(int bpm, int ticksPerBeat)
                throws MidiUnavailableException, InvalidMidiDataException {
            lastInstance = this;
            events.add("BPM=" + bpm);
            events.add("TPB=" + ticksPerBeat);
        }

        public void addNote(int note, int startTick, int numTicks) {
            events.add("NOTE " + note + " " + startTick + " " + numTicks);
        }

        public void play() throws MidiUnavailableException {
            // no-op for test
        }
    }
    """

    harness_code = """
    import abc.player.Main;
    import abc.sound.SequencePlayer;

    public class MainPlayHarness {
        public static void main(String[] args) throws Exception {
            Main.play(args[0]);
            SequencePlayer player = SequencePlayer.lastInstance;
            for (String event : player.events) {
                System.out.println(event);
            }
        }
    }
    """

    stub_path = tmp_path / "SequencePlayer.java"
    stub_path.write_text(stub_sequence)
    harness_path = tmp_path / "MainPlayHarness.java"
    harness_path.write_text(harness_code)

    cmd = [
        "javac",
        "-d",
        str(tmp_path),
        str(harness_path),
        str(stub_path),
        str(MAIN_JAVA),
        str(PITCH_JAVA),
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    result = subprocess.run(
        ["java", "-cp", str(tmp_path), "MainPlayHarness", str(abc_path)],
        check=True,
        capture_output=True,
        text=True,
    )

    lines = result.stdout.strip().splitlines()
    assert "X:1" in lines
    assert "T:Unit Test Tune" in lines
    assert "M:4/4" in lines
    assert "L:1/4" in lines
    assert "Q:1/4=120" in lines
    assert "K:C" in lines

    assert "BPM=120" in lines
    assert "TPB=96" in lines
    assert "NOTE 60 0 96" in lines
    assert "NOTE 62 96 96" in lines
    assert "NOTE 64 192 96" in lines
