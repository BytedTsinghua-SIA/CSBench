package abc.sound;

import static org.junit.Assert.*;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.junit.Test;

public class SequencePlayerTest {

    @Test
    public void testSimpleSequence() throws Exception {
        SequencePlayer player = new SequencePlayer(120, 4);

        player.addNote(new Pitch('C').toMidiNote(), 0, 2);
        player.addNote(new Pitch('D').toMidiNote(), 2, 2);

        String[] lines = player.toString().trim().split("\\n");
        assertEquals(5, lines.length);

        Pattern eventPattern = Pattern.compile(
                "Event: (NOTE_ON|NOTE_OFF)\\s+Pitch: (\\d+)\\s+Tick: (\\d+)");
        Pattern metaPattern = Pattern.compile("Meta event: END_OF_TRACK\\s+Tick: (\\d+)");

        assertEvent(eventPattern, lines[0], "NOTE_ON", 60, 0);
        assertEvent(eventPattern, lines[1], "NOTE_OFF", 60, 2);
        assertEvent(eventPattern, lines[2], "NOTE_ON", 62, 2);
        assertEvent(eventPattern, lines[3], "NOTE_OFF", 62, 4);

        Matcher meta = metaPattern.matcher(lines[4].trim());
        assertTrue(meta.matches());
        assertEquals(4, Integer.parseInt(meta.group(1)));
    }

    @Test
    public void testZeroDurationNote() throws Exception {
        SequencePlayer player = new SequencePlayer(120, 4);

        player.addNote(new Pitch('E').toMidiNote(), 3, 0);

        String[] lines = player.toString().trim().split("\\n");
        assertEquals(3, lines.length);

        Pattern eventPattern = Pattern.compile(
                "Event: (NOTE_ON|NOTE_OFF)\\s+Pitch: (\\d+)\\s+Tick: (\\d+)");
        Pattern metaPattern = Pattern.compile("Meta event: END_OF_TRACK\\s+Tick: (\\d+)");

        assertEvent(eventPattern, lines[0], "NOTE_ON", 64, 3);
        assertEvent(eventPattern, lines[1], "NOTE_OFF", 64, 3);

        Matcher meta = metaPattern.matcher(lines[2].trim());
        assertTrue(meta.matches());
        assertEquals(3, Integer.parseInt(meta.group(1)));
    }

    private void assertEvent(Pattern pattern, String line, String type,
                             int pitch, int tick) {
        Matcher match = pattern.matcher(line.trim());
        assertTrue(match.matches());
        assertEquals(type, match.group(1));
        assertEquals(pitch, Integer.parseInt(match.group(2)));
        assertEquals(tick, Integer.parseInt(match.group(3)));
    }

}
