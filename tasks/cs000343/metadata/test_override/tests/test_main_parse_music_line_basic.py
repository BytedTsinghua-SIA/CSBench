import re

from .java_runner import compile_and_run, MAIN_JAVA, PITCH_JAVA, SEQUENCE_PLAYER_JAVA


def test_main_parse_music_line_basic(tmp_path):
    code = """
    import abc.player.Main;
    import abc.sound.SequencePlayer;
    import java.lang.reflect.Method;

    public class MainParseLineHarness {
        public static void main(String[] args) throws Exception {
            Method parseDefaultLength = Main.class.getDeclaredMethod("parseDefaultLength", String.class);
            parseDefaultLength.setAccessible(true);
            Object defaultLength = parseDefaultLength.invoke(null, "1/4");

            Method parseMusicLine = Main.class.getDeclaredMethod(
                "parseMusicLine",
                String.class,
                int.class,
                defaultLength.getClass(),
                SequencePlayer.class
            );
            parseMusicLine.setAccessible(true);

            SequencePlayer player = new SequencePlayer(120, 96);
            int tick = (Integer) parseMusicLine.invoke(null, "C2 D/2 z E", 0, defaultLength, player);
            System.out.print(player.toString());
            System.out.println("FINAL_TICK=" + tick);
        }
    }
    """
    output = compile_and_run(
        tmp_path,
        "MainParseLineHarness",
        code,
        [MAIN_JAVA, PITCH_JAVA, SEQUENCE_PLAYER_JAVA],
    )

    lines = output.strip().splitlines()
    assert lines[-1] == "FINAL_TICK=432"

    event_re = re.compile(r"Event: (NOTE_ON|NOTE_OFF)\s+Pitch: (\d+)\s+Tick: (\d+)")
    meta_re = re.compile(r"Meta event: END_OF_TRACK\s+Tick: (\d+)")

    parsed = []
    for line in lines[:-2]:
        match = event_re.match(line.strip())
        assert match is not None
        parsed.append((match.group(1), int(match.group(2)), int(match.group(3))))

    meta_match = meta_re.match(lines[-2].strip())
    assert meta_match is not None
    meta_tick = int(meta_match.group(1))

    assert parsed == [
        ("NOTE_ON", 60, 0),
        ("NOTE_OFF", 60, 192),
        ("NOTE_ON", 62, 192),
        ("NOTE_OFF", 62, 240),
        ("NOTE_ON", 64, 336),
        ("NOTE_OFF", 64, 432),
    ]
    assert meta_tick == 432
