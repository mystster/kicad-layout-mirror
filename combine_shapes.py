import math
from kipy import KiCad
from kipy.board_types import BoardPolygon
from kipy.geometry import PolygonWithHoles, PolyLine, PolyLineNode, arc_center, arc_radius, arc_start_angle, arc_end_angle
from shapely.geometry import Polygon, LineString
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

def kipy_to_shapely(geom):
    if isinstance(geom, PolygonWithHoles):
        outline_pts = polyline_to_points(geom.outline)
        if len(outline_pts) < 3:
            return None
        holes = []
        for hole in geom.holes:
            hole_pts = polyline_to_points(hole)
            if len(hole_pts) >= 3:
                holes.append(hole_pts)
        # Ensure outline_pts is closed
        if outline_pts[0] != outline_pts[-1]:
            outline_pts.append(outline_pts[0])
        return Polygon(outline_pts, holes)
    elif isinstance(geom, PolyLine):
        pts = polyline_to_points(geom)
        if len(pts) >= 2:
            return LineString(pts)
    return None

def shapely_to_kipy(shapely_poly):
    if not isinstance(shapely_poly, Polygon):
        return None
    kipy_poly = PolygonWithHoles()
    kipy_poly.outline = points_to_polyline(shapely_poly.exterior.coords)
    for interior in shapely_poly.interiors:
        kipy_poly.add_hole(points_to_polyline(interior.coords))
    return kipy_poly

def merge_shapes_with_ipc(source_layer_name, target_layer_name):
    # 1. KiCad本体に接続
    board = KiCad().get_board()

    # 対象レイヤーの取得
    source_layer = board.get_layer(source_layer_name)
    target_layer = board.get_layer(target_layer_name)

    polygons = []
    lines = []

    # 2. 全ての描画アイテムを走査してshapelyオブジェクトに変換
    for item in board.drawings:
        if item.layer == source_layer:
            try:
                item_geom = item.geometry
                shapely_geom = kipy_to_shapely(item_geom)
                if isinstance(shapely_geom, Polygon):
                    polygons.append(shapely_geom)
                elif isinstance(shapely_geom, LineString):
                    lines.append(shapely_geom)
            except AttributeError:
                continue

    # 3. 幾何学的な「和（Union）」および「面化（Polygonize）」を計算
    merged_polygons = []
    
    # 既存のポリゴン同士を結合
    if polygons:
        merged_polygons.append(unary_union(polygons))
        
    # 線からポリゴンを生成して結合
    if lines:
        polygonized = list(polygonize(lines))
        if polygonized:
            merged_polygons.extend(polygonized)

    if not merged_polygons:
        print("No shapes found to merge.")
        return

    # 全てを結合
    final_shape = unary_union(merged_polygons)

    # Multipolygonの場合はそれぞれをBoardPolygonとして追加
    shapes_to_add = []
    if final_shape.geom_type == 'Polygon':
        shapes_to_add.append(final_shape)
    elif final_shape.geom_type == 'MultiPolygon':
        shapes_to_add.extend(list(final_shape.geoms))

    # 4. 合成結果を新しいポリゴンとして作成して追加
    added_count = 0
    for shape in shapes_to_add:
        kipy_poly = shapely_to_kipy(shape)
        if kipy_poly:
            new_polygon = BoardPolygon(
                board=board,
                layer=target_layer,
                geometry=kipy_poly,
                filled=True
            )
            board.add(new_polygon)
            added_count += 1

    if added_count > 0:
        # 5. 変更をKiCad本体に反映
        board.commit()
        print(f"Successfully merged shapes from {source_layer_name} to {target_layer_name}.")
    else:
        print("Failed to generate a valid polygon from shapes.")

if __name__ == "__main__":
    # レイヤー名はKiCad上の表示名（例: "User.1", "F.Cu"）
    merge_shapes_with_ipc("User.1", "F.Mask")
