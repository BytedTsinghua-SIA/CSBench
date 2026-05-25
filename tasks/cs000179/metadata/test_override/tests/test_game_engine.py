import subprocess
from pathlib import Path
import pytest

SRC_DIR = Path(__file__).resolve().parents[1]
LIB_DIR = SRC_DIR / "library-sp18" / "javalib"
LIB_COMPONENTS = [
    str(LIB_DIR / "stdlib.jar"),
    str(LIB_DIR / "algs4.jar"),
    str(LIB_DIR / "stdlib-package.jar"),
    str(LIB_DIR / "junit-4.12.jar"),
    str(LIB_DIR / "hamcrest-core-1.3.jar"),
]
BASE_CLASSPATH = ":".join([str(SRC_DIR), *LIB_COMPONENTS])

def _collect_java_sources():
    s = []
    for p in SRC_DIR.rglob("*.java"):
        if "library-sp18" in p.parts:
            continue
        s.append(str(p.relative_to(SRC_DIR)))
    return sorted(s)

@pytest.fixture(scope="session", autouse=True)
def compile_project():
    files = _collect_java_sources()
    subprocess.run(["javac", "-cp", BASE_CLASSPATH, *files], cwd=SRC_DIR, check=True)

def _compile_and_run(tmp_path: Path, pkg_path: str, class_name: str, source: str):
    pkg_dir = tmp_path.joinpath(*pkg_path.split("/"))
    pkg_dir.mkdir(parents=True, exist_ok=True)
    java_file = pkg_dir / f"{class_name}.java"
    java_file.write_text(source, encoding="utf-8")
    subprocess.run(
        ["javac", "-cp", BASE_CLASSPATH, "-d", str(tmp_path), str(java_file.relative_to(tmp_path))],
        cwd=tmp_path,
        check=True,
    )
    run_cp = ":".join([str(tmp_path), BASE_CLASSPATH])
    return subprocess.run(
        ["java", "-cp", run_cp, f"{pkg_path}.{class_name}"],
        cwd=SRC_DIR,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    ).stdout

def test_game_deterministic_replay(tmp_path):
    out = _compile_and_run(
        tmp_path,
        "byog.Core",
        "DeterminismHarness",
        """
package byog.Core;
import byog.TileEngine.TETile;
import java.lang.reflect.Field;
public class DeterminismHarness {
    private static World getWorld(Game g) throws Exception {
        Field f = Game.class.getDeclaredField("world");
        f.setAccessible(true);
        return (World) f.get(g);
    }
    private static String flat(TETile[][] t) {
        StringBuilder sb = new StringBuilder();
        for (int y = t[0].length - 1; y >= 0; y--) {
            for (int x = 0; x < t.length; x++) sb.append(t[x][y].character());
            sb.append("\\n");
        }
        return sb.toString();
    }
    private static String snap(Game g, String in) {
        TETile[][] tiles = g.playWithInputString(in);
        try { getWorld(g).getPlayer().drawOnWorld(tiles); } catch (Exception e) { throw new RuntimeException(e); }
        return flat(tiles);
    }
    public static void main(String[] args) {
        Game a = new Game();
        Game b = new Game();
        String cmds = "n123456ssswwaadd";
        String m1 = snap(a, cmds);
        String m2 = snap(b, cmds);
        if (!m1.equals(m2)) throw new RuntimeException("mismatch");
        System.out.println("OK_DETERMINISM");
    }
}
"""
    )
    assert "OK_DETERMINISM" in out

def test_game_save_and_load(tmp_path):
    out = _compile_and_run(
        tmp_path,
        "byog.Core",
        "PersistenceHarness",
        """
package byog.Core;
import byog.TileEngine.TETile;
import java.lang.reflect.Field;
public class PersistenceHarness {
    private static World getWorld(Game g) throws Exception {
        Field f = Game.class.getDeclaredField("world");
        f.setAccessible(true);
        return (World) f.get(g);
    }
    private static String flat(TETile[][] t) {
        StringBuilder sb = new StringBuilder();
        for (int y = t[0].length - 1; y >= 0; y--) {
            for (int x = 0; x < t.length; x++) sb.append(t[x][y].character());
            sb.append("\\n");
        }
        return sb.toString();
    }
    private static String snap(Game g, String in) {
        TETile[][] tiles = g.playWithInputString(in);
        try { getWorld(g).getPlayer().drawOnWorld(tiles); } catch (Exception e) { throw new RuntimeException(e); }
        return flat(tiles);
    }
    public static void main(String[] args) {
        Game saver = new Game();
        String saved = snap(saver, "n987654321ssdd:Q");
        Game loader = new Game();
        String loaded = snap(loader, "l");
        if (!saved.equals(loaded)) throw new RuntimeException("persistence mismatch");
        System.out.println("OK_PERSIST");
    }
}
"""
    )
    assert "OK_PERSIST" in out

def test_game_savefile_cleanup(tmp_path):
    out = _compile_and_run(
        tmp_path,
        "byog.Core",
        "CleanupHarness",
        """
package byog.Core;
public class CleanupHarness {
    public static void main(String[] args) {
        java.io.File f = new java.io.File("savefile.txt");
        try {
            if (!f.exists()) {
                Game g = new Game();
                g.playWithInputString("n1s:Q");
            }
            java.io.File f2 = new java.io.File("savefile.txt");
            if (f2.exists() && !f2.delete()) throw new RuntimeException("delete failed");
            System.out.println("OK_CLEAN");
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
"""
    )
    assert "OK_CLEAN" in out