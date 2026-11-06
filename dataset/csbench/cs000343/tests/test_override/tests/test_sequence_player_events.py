import re

from .java_runner import compile_and_run, PITCH_JAVA, SEQUENCE_PLAYER_JAVA


def test_sequence_player_events(tmp_path):
    code = """
    import abc.sound.SequencePlayer;
    import abc.sound.Pitch;

    public class SequencePlayerHarnessBasic {
        public static void main(String[] args) throws Exception {
            SequencePlayer player = new SequencePlayer(120, 4);
            player.addNote(new Pitch('C').toMidiNote(), 0, 2);
            player.addNote(new Pitch('D').toMidiNote(), 2, 2);
            System.out.print(player.toString());
        }
    }
    """
    output = compile_and_run(
        tmp_path,
        "SequencePlayerHarnessBasic",
        code,
        [PITCH_JAVA, SEQUENCE_PLAYER_JAVA],
    )

    lines = [line.strip() for line in output.strip().splitlines()]
    assert len(lines) == 5

    event_re = re.compile(r"Event: (NOTE_ON|NOTE_OFF)\s+Pitch: (\d+)\s+Tick: (\d+)")
    meta_re = re.compile(r"Meta event: END_OF_TRACK\s+Tick: (\d+)")

    parsed = []
    for line in lines[:4]:
        match = event_re.match(line)
        assert match is not None
        parsed.append((match.group(1), int(match.group(2)), int(match.group(3))))

    meta_match = meta_re.match(lines[4])
    assert meta_match is not None
    meta_tick = int(meta_match.group(1))

    assert parsed == [
        ("NOTE_ON", 60, 0),
        ("NOTE_OFF", 60, 2),
        ("NOTE_ON", 62, 2),
        ("NOTE_OFF", 62, 4),
    ]
    assert meta_tick == 4
