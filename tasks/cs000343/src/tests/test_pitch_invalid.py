from .java_runner import compile_and_run, PITCH_JAVA


def test_pitch_invalid_letter(tmp_path):
    code = """
    import abc.sound.Pitch;

    public class PitchHarnessInvalid {
        public static void main(String[] args) {
            try {
                new Pitch('H');
                System.out.println("NO_ERROR");
            } catch (IllegalArgumentException e) {
                System.out.println("ERROR");
            }
        }
    }
    """
    output = compile_and_run(tmp_path, "PitchHarnessInvalid", code, [PITCH_JAVA])
    assert output.strip() == "ERROR"
