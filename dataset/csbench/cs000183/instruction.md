# Project 3 – Bear Maps Backend

## Overview
Implement the Java backend used by the Bear Maps project. All source files live in `main/java` and must remain in the default (unnamed) package so the grading harness can compile and link them directly, and libraries other than the Java standard library and the libraries already included in the project (including the Princeton library) are forbidden. The key deliverables are:

* `GraphBuildingHandler.java` – SAX parser callbacks that translate OpenStreetMap XML into calls on `GraphDB`.
* `GraphDB.java` – data model for the road graph that stores vertices, edges, metadata tags, and exposes helpers such as `vertices()`, `lon(long)`, `lat(long)`, `distance(...)`, `bearing(...)`, and `closest(double,double)`.
* `Rasterer.java` – logic for picking the correct tile depth and grid to satisfy a map viewport request.
* `Router.java` – shortest-path search between two geographic coordinates plus human-readable directions (`routeDirections`).

Helper files like `MapServer.java` and the static assets under `static/` are provided; do not rename or relocate them.

## Functional Expectations
### Rasterer
`Rasterer.getMapRaster(Map<String, Double> params)` receives a query box (`ullon`, `ullat`, `lrlon`, `lrlat`) and the viewport width/height. Your implementation must:

* Compute the minimum depth whose longitudinal distance per pixel is ≤ the query box’s LonDPP (clamped to `[0, 7]`).
* Select every tile at that depth that intersects the query box and build a 2D `String[][] render_grid` containing their filenames (e.g. `d2_x1_y3.png`).
* Populate `raster_ul_lon`, `raster_ul_lat`, `raster_lr_lon`, `raster_lr_lat`, `depth`, `query_success`, `raster_width`, and `raster_height` exactly as in the reference implementation.

### Graph construction and queries
`GraphDB` owns the parsed road network. After `GraphBuildingHandler` walks the XML file, the graph should contain:

* A `Map<Long, Node>` of vertices storing latitude, longitude, incident edge IDs, and tag metadata.
* Bidirectional adjacency information for every allowed road (`highway` tag listed in the handler).
* A post-processing pass that removes isolated nodes (the provided `clean()` helper is fine).
* Accessors used by routing and direction generation: `Iterable<Long> vertices()`, `Iterable<Long> adjacent(long)`, `double distance(long,long)`, `double bearing(long,long)`, and `long closest(double,double)`.

### Routing
`Router.shortestPath` should run Dijkstra or A* to produce the list of vertex IDs from the start point to the goal. Use `GraphDB.closest` to snap arbitrary coordinates to the graph and store parent pointers so you can reconstruct the path. `Router.routeDirections` converts that list into `NavigationDirection` objects grouped by road name and turn type; distances must add up to the same values returned by `GraphDB.distance`.

## Files Required by the Autograder
All production code must remain in:

* `main/java/GraphBuildingHandler.java`
* `main/java/GraphDB.java`
* `main/java/Rasterer.java`
* `main/java/Router.java`

Do not introduce package declarations or rename these files. Any auxiliary classes you add should live in the same directory and default package so they compile with `javac`.
