from .java_runner import compile_and_run, PITCH_JAVA


def test_pitch_basic(tmp_path):
    code = """
    import abc.sound.Pitch;

    public class PitchHarnessBasic {
        public static void main(String[] args) {
            Pitch c = new Pitch('C');
            Pitch cs = c.transpose(1);
            Pitch low = c.transpose(-Pitch.OCTAVE);
            System.out.println(c.toString());
            System.out.println(cs.toString());
            System.out.println(low.toString());
            System.out.println(c.difference(cs));
            System.out.println(c.lessThan(cs));
            System.out.println(c.toMidiNote());
        }
    }
    """
    output = compile_and_run(tmp_path, "PitchHarnessBasic", code, [PITCH_JAVA])
    lines = output.strip().splitlines()
    assert lines == ["C", "^C", "C,", "-1", "true", "60"]
