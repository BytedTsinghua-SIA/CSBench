import subprocess
from pathlib import Path
import pytest

SRC_DIR = Path(__file__).resolve().parents[1]
JAVA_SOURCES = [
    "main/java/GraphBuildingHandler.java",
    "main/java/GraphDB.java",
    "main/java/GraphDBLauncher.java",
    "main/java/Rasterer.java",
    "main/java/Router.java",
]

@pytest.fixture(scope="session", autouse=True)
def compile_core_sources():
    files = [str(Path(src)) for src in JAVA_SOURCES]
    subprocess.run(["javac", "-d", str(SRC_DIR), *files], cwd=SRC_DIR, check=True)

@pytest.fixture(scope="session")
def tiny_osm(tmp_path_factory: pytest.TempPathFactory) -> Path:
    p = tmp_path_factory.mktemp("osm") / "tiny.osm.xml"
    p.write_text(
        "<?xml version='1.0' encoding='UTF-8'?>\n"
        "<osm version='0.6' generator='pytest'>\n"
        "  <node id='1' lat='0.0' lon='0.0'/>\n"
        "  <node id='2' lat='0.0' lon='1.0'/>\n"
        "  <node id='3' lat='0.0' lon='2.0'/>\n"
        "  <node id='4' lat='1.0' lon='1.0'/>\n"
        "  <way id='100'>\n"
        "    <nd ref='1'/>\n"
        "    <nd ref='2'/>\n"
        "    <nd ref='3'/>\n"
        "    <tag k='highway' v='residential'/>\n"
        "    <tag k='name' v='Main Street'/>\n"
        "  </way>\n"
        "  <way id='200'>\n"
        "    <nd ref='2'/>\n"
        "    <nd ref='4'/>\n"
        "    <tag k='highway' v='residential'/>\n"
        "    <tag k='name' v='Oak Avenue'/>\n"
        "  </way>\n"
        "</osm>\n"
    )
    return p

def _compile_and_run(tmp_path: Path, cls_name: str, src: str) -> str:
    java = tmp_path / f"{cls_name}.java"
    java.write_text(src, encoding="utf-8")
    subprocess.run(["javac", "-cp", str(SRC_DIR), java.name], cwd=tmp_path, check=True)
    cp = f"{tmp_path}:{SRC_DIR}"
    proc = subprocess.run(
        ["java", "-cp", cp, cls_name],
        cwd=SRC_DIR,
        text=True,
        capture_output=True,
        check=True,
    )
    return proc.stdout

def test_rasterer_against_golden(tmp_path):
    out = _compile_and_run(
        tmp_path,
        "Proj3RasterHarness",
        """
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
public class Proj3RasterHarness {
    private static final String RASTER_PARAM_FILE = "raster_params.txt";
    private static final String RASTER_RESULT_FILE = "raster_results.txt";
    public static void main(String[] args) throws Exception {
        Rasterer rasterer = new Rasterer();
        List<Map<String, Double>> params = loadRasterParams();
        List<Map<String, Object>> expected = loadRasterResults();
        if (params.size() != expected.size()) throw new RuntimeException("count mismatch");
        for (int i = 0; i < params.size(); i++) {
            Map<String, Object> actual = rasterer.getMapRaster(params.get(i));
            Map<String, Object> exp = expected.get(i);
            verify("Raster " + i, exp, actual);
        }
        System.out.println("OK_RASTER");
    }
    private static List<Map<String, Double>> loadRasterParams() throws Exception {
        List<String> lines = Files.readAllLines(Paths.get(RASTER_PARAM_FILE), Charset.defaultCharset());
        List<Map<String, Double>> tests = new ArrayList<>();
        List<String> filtered = new ArrayList<>();
        for (String line : lines) if (!line.trim().isEmpty() && !line.startsWith("#")) filtered.add(line.trim());
        int i = 0;
        while (i + 5 < filtered.size()) {
            Map<String, Double> p = new HashMap<>();
            p.put("ullon", Double.parseDouble(filtered.get(i)));
            p.put("ullat", Double.parseDouble(filtered.get(i+1)));
            p.put("lrlon", Double.parseDouble(filtered.get(i+2)));
            p.put("lrlat", Double.parseDouble(filtered.get(i+3)));
            p.put("w", Double.parseDouble(filtered.get(i+4)));
            p.put("h", Double.parseDouble(filtered.get(i+5)));
            tests.add(p);
            i += 6;
        }
        return tests;
    }
    private static List<Map<String, Object>> loadRasterResults() throws Exception {
        List<String> lines = Files.readAllLines(Paths.get(RASTER_RESULT_FILE), Charset.defaultCharset());
        List<String> filtered = new ArrayList<>();
        for (String line : lines) if (!line.trim().isEmpty() && !line.startsWith("#")) filtered.add(line.trim());
        List<Map<String, Object>> expected = new ArrayList<>();
        int i = 0;
        while (i + 6 < filtered.size()) {
            Map<String, Object> r = new HashMap<>();
            r.put("raster_ul_lon", Double.parseDouble(filtered.get(i++)));
            r.put("raster_ul_lat", Double.parseDouble(filtered.get(i++)));
            r.put("raster_lr_lon", Double.parseDouble(filtered.get(i++)));
            r.put("raster_lr_lat", Double.parseDouble(filtered.get(i++)));
            r.put("depth", Integer.parseInt(filtered.get(i++)));
            r.put("query_success", Boolean.parseBoolean(filtered.get(i++)));
            String[] dims = filtered.get(i++).split(" ");
            int rows = Integer.parseInt(dims[0]);
            int cols = Integer.parseInt(dims[1]);
            String[][] grid = new String[rows][cols];
            for (int rRow = 0; rRow < rows; rRow++)
                for (int cCol = 0; cCol < cols; cCol++)
                    grid[rRow][cCol] = filtered.get(i++);
            r.put("render_grid", grid);
            expected.add(r);
        }
        return expected;
    }
    private static void verify(String label, Map<String, Object> exp, Map<String, Object> act) {
        for (String k : exp.keySet()) {
            if (!act.containsKey(k)) throw new RuntimeException(label + " missing " + k);
            Object e = exp.get(k), a = act.get(k);
            if (e instanceof Double) {
                if (Math.abs(((Double)e) - ((Double)a)) > 1e-7) throw new RuntimeException(label + " mismatch " + k);
            } else if (e instanceof String[][]) {
                if (!java.util.Arrays.deepEquals((String[][])e, (String[][])a)) throw new RuntimeException(label + " grid");
            } else if (!e.equals(a)) throw new RuntimeException(label + " mismatch " + k);
        }
    }
}
"""
    )
    assert "OK_RASTER" in out

def test_graph_vertices_and_path(tmp_path, tiny_osm: Path):
    out = _compile_and_run(
        tmp_path,
        "Proj3GraphCoreHarness",
        f"""
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
public class Proj3GraphCoreHarness {{
    private static final String OSM = "{tiny_osm.as_posix()}";
    public static void main(String[] args) {{
        GraphDB graph = new GraphDB(OSM);
        List<Long> vs = new ArrayList<>();
        for (Long id : graph.vertices()) vs.add(id);
        if (vs.size() != 4) throw new RuntimeException("vcount " + vs.size());
        List<Long> exp = Arrays.asList(1L, 2L, 4L);
        List<Long> path = Router.shortestPath(graph, 0.0, 0.0, 1.0, 1.0);
        if (!exp.equals(path)) throw new RuntimeException("path " + path);
        System.out.println("OK_GRAPH_CORE");
    }}
}}
"""
    )
    assert "OK_GRAPH_CORE" in out

def test_graph_route_directions(tmp_path, tiny_osm: Path):
    out = _compile_and_run(
        tmp_path,
        "Proj3GraphDirHarness",
        f"""
import java.util.Arrays;
import java.util.List;
public class Proj3GraphDirHarness {{
    private static final String OSM = "{tiny_osm.as_posix()}";
    public static void main(String[] args) {{
        GraphDB g = new GraphDB(OSM);
        List<Long> path = Arrays.asList(1L, 2L, 4L);
        List<Router.NavigationDirection> ds = Router.routeDirections(g, path);
        if (ds.size() != 2) throw new RuntimeException("dcount " + ds.size());
        Router.NavigationDirection first = ds.get(0);
        double d1 = g.distance(1L, 2L);
        if (first.direction != Router.NavigationDirection.START) throw new RuntimeException("first dir");
        if (!"Main Street".equals(first.way)) throw new RuntimeException("first way " + first.way);
        if (Math.abs(first.distance - d1) > 1e-3) throw new RuntimeException("first dist");
        Router.NavigationDirection second = ds.get(1);
        double d2 = g.distance(2L, 4L);
        if (second.direction != Router.NavigationDirection.LEFT) throw new RuntimeException("second dir");
        if (!"Oak Avenue".equals(second.way)) throw new RuntimeException("second way " + second.way);
        if (Math.abs(second.distance - d2) > 1e-3) throw new RuntimeException("second dist");
        System.out.println("OK_GRAPH_DIR");
    }}
}}
"""
    )
    assert "OK_GRAPH_DIR" in out