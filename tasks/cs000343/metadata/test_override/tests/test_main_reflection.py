from .java_runner import compile_and_run, MAIN_JAVA, PITCH_JAVA, SEQUENCE_PLAYER_JAVA


def test_main_parse_tempo_and_length(tmp_path):
    code = """
    import abc.player.Main;
    import java.lang.reflect.Method;

    public class MainReflectionHarness {
        public static void main(String[] args) throws Exception {
            Method parseTempo = Main.class.getDeclaredMethod("parseTempo", String.class);
            parseTempo.setAccessible(true);
            System.out.println(parseTempo.invoke(null, "1/4=140"));
            System.out.println(parseTempo.invoke(null, "150"));
            System.out.println(parseTempo.invoke(null, "bad"));

            Method parseDefaultLength = Main.class.getDeclaredMethod("parseDefaultLength", String.class);
            parseDefaultLength.setAccessible(true);
            Object lenQuarter = parseDefaultLength.invoke(null, "1/4");
            Method toTicks = lenQuarter.getClass().getDeclaredMethod("toTicks", int.class);
            toTicks.setAccessible(true);
            System.out.println(toTicks.invoke(lenQuarter, 96));

            Object lenEighth = parseDefaultLength.invoke(null, "1/8");
            System.out.println(toTicks.invoke(lenEighth, 96));

            Object lenBad = parseDefaultLength.invoke(null, "bad");
            System.out.println(toTicks.invoke(lenBad, 96));
        }
    }
    """
    output = compile_and_run(
        tmp_path,
        "MainReflectionHarness",
        code,
        [MAIN_JAVA, PITCH_JAVA, SEQUENCE_PLAYER_JAVA],
    )
    lines = output.strip().splitlines()
    assert lines == ["140", "150", "120", "96", "48", "48"]
