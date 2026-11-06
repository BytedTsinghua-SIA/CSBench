import re

from .java_runner import compile_and_run, PITCH_JAVA, SEQUENCE_PLAYER_JAVA


def test_sequence_player_zero_duration(tmp_path):
    code = """
    import abc.sound.SequencePlayer;
    import abc.sound.Pitch;

    public class SequencePlayerHarnessZero {
        public static void main(String[] args) throws Exception {
            SequencePlayer player = new SequencePlayer(120, 4);
            player.addNote(new Pitch('E').toMidiNote(), 3, 0);
            System.out.print(player.toString());
        }
    }
    """
    output = compile_and_run(
        tmp_path,
        "SequencePlayerHarnessZero",
        code,
        [PITCH_JAVA, SEQUENCE_PLAYER_JAVA],
    )

    lines = [line.strip() for line in output.strip().splitlines()]
    assert len(lines) == 3

    event_re = re.compile(r"Event: (NOTE_ON|NOTE_OFF)\s+Pitch: (\d+)\s+Tick: (\d+)")
    meta_re = re.compile(r"Meta event: END_OF_TRACK\s+Tick: (\d+)")

    first = event_re.match(lines[0])
    second = event_re.match(lines[1])
    meta = meta_re.match(lines[2])

    assert first is not None
    assert second is not None
    assert meta is not None

    assert (first.group(1), int(first.group(2)), int(first.group(3))) == ("NOTE_ON", 64, 3)
    assert (second.group(1), int(second.group(2)), int(second.group(3))) == ("NOTE_OFF", 64, 3)
    assert int(meta.group(1)) == 3
