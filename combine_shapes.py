import math
from kipy import KiCad
import kipy.board_types as bt
from kipy.geometry import PolygonWithHoles, PolyLine, PolyLineNode, arc_center, arc_radius, arc_start_angle, arc_end_angle
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import polygonize, unary_union

def arc_to_points(arc, num_segments=16):
    start = arc.start
    mid = arc.mid
    end = arc.end
    center = arc_center(start, mid, end)
    if center is None:
        return [(start.x, start.y), (end.x, end.y)]
    r = arc_radius(start, mid, end)
    sa = arc_start_angle(start, mid, end)
    ea = arc_end_angle(start, mid, end)
    if sa is None or ea is None:
        return [(start.x, start.y), (end.x, end.y)]
    if ea < sa:
        ea += 2 * math.pi
    pts = []
    for i in range(num_segments + 1):
        angle = sa + (ea - sa) * i / num_segments
        x = center.x + r * math.cos(angle)
        y = center.y + r * math.sin(angle)
        pts.append((x, y))
    return pts

def polyline_to_points(polyline):
    pts = []
    for node in polyline:
        if node.has_point:
            pts.append((node.point.x, node.point.y))
        elif node.has_arc:
            pts.extend(arc_to_points(node.arc))
    return pts

def points_to_polyline(pts):
    pl = PolyLine()
    for x, y in pts:
        pl.append(PolyLineNode.from_xy(int(x), int(y)))
    return pl

def kipy_polygon_to_shapely(geom):
    if isinstance(geom, PolygonWithHoles):
        outline_pts = polyline_to_points(geom.outline)
        if len(outline_pts) < 3:
            return None
        holes = []
        for hole in geom.holes:
            hole_pts = polyline_to_points(hole)
            if len(hole_pts) >= 3:
                holes.append(hole_pts)
        if outline_pts[0] != outline_pts[-1]:
            outline_pts.append(outline_pts[0])
        return Polygon(outline_pts, holes)
    return None

def item_to_shapely(item):
    if isinstance(item, bt.BoardSegment) or isinstance(item, bt.Track):
        return LineString([(item.start.x, item.start.y), (item.end.x, item.end.y)])
    elif isinstance(item, bt.BoardArc) or isinstance(item, bt.ArcTrack):
        arc_pts = arc_to_points(item)
        if len(arc_pts) >= 2:
            return LineString(arc_pts)
    elif isinstance(item, bt.BoardPolygon):
        shapely_polys = []
        for p in item.polygons:
            poly = kipy_polygon_to_shapely(p)
            if poly: shapely_polys.append(poly)
        if len(shapely_polys) == 1:
            return shapely_polys[0]
        elif len(shapely_polys) > 1:
            return unary_union(shapely_polys)
    elif isinstance(item, bt.BoardRectangle):
        return box(item.top_left.x, item.top_left.y, item.bottom_right.x, item.bottom_right.y)
    elif isinstance(item, bt.BoardCircle):
        cx, cy = item.center.x, item.center.y
        rx, ry = item.radius_point.x, item.radius_point.y
        r = math.hypot(rx - cx, ry - cy)
        # Use shapely buffer to create circle polygon
        return Point(cx, cy).buffer(r, resolution=16)
    return None

def shapely_to_kipy_polygon_with_holes(shapely_poly):
    if not isinstance(shapely_poly, Polygon):
        return None
    kipy_poly = PolygonWithHoles()
    kipy_poly.outline = points_to_polyline(shapely_poly.exterior.coords)
    for interior in shapely_poly.interiors:
        kipy_poly.add_hole(points_to_polyline(interior.coords))
    return kipy_poly

def merge_shapes_with_ipc(source_layer_name, target_layer_name):
    board = KiCad().get_board()

    def get_layer_enum(name):
        enum_name = "BL_" + name.replace(".", "_")
        if hasattr(bt.BoardLayer, enum_name):
            return getattr(bt.BoardLayer, enum_name)
        raise ValueError(f"Unknown layer: {name}")

    source_layer = get_layer_enum(source_layer_name)
    target_layer = get_layer_enum(target_layer_name)

    polygons = []
    lines = []

    # Get shapes and tracks instead of the hallucinated "drawings" property
    drawings = board.get_shapes() + board.get_tracks()
    for item in drawings:
        if item.layer == source_layer:
            shapely_geom = item_to_shapely(item)
            if isinstance(shapely_geom, Polygon):
                polygons.append(shapely_geom)
            elif isinstance(shapely_geom, LineString):
                lines.append(shapely_geom)

    merged_polygons = []
    
    if polygons:
        merged_polygons.append(unary_union(polygons))
        
    if lines:
        polygonized = list(polygonize(lines))
        if polygonized:
            merged_polygons.extend(polygonized)

    if not merged_polygons:
        print("No shapes found to merge.")
        return

    final_shape = unary_union(merged_polygons)

    shapes_to_add = []
    if final_shape.geom_type == 'Polygon':
        shapes_to_add.append(final_shape)
    elif final_shape.geom_type == 'MultiPolygon':
        shapes_to_add.extend(list(final_shape.geoms))

    added_count = 0
    for shape in shapes_to_add:
        kipy_poly = shapely_to_kipy_polygon_with_holes(shape)
        if kipy_poly:
            new_polygon = bt.BoardPolygon()
            new_polygon.polygons.append(kipy_poly)
            new_polygon.layer = target_layer
            new_polygon.attributes.fill.filled = True
            
            # Using create_items instead of hallucinated board.add()
            board.create_items(new_polygon)
            added_count += 1

    if added_count > 0:
        print(f"Successfully merged shapes from {source_layer_name} to {target_layer_name}.")
    else:
        print("Failed to generate a valid polygon from shapes.")

if __name__ == "__main__":
    merge_shapes_with_ipc("User.1", "F.Mask")
