from kipy import KiCad
from kipy.geometry import PolygonWithHoles, PolyLineNode, PolyLine
from kipy.board_types import BoardPolygon, BoardCircle, BoardText
from kipy.board import Board
from kicad_utils import mirror_point

def mirror_shape(MIRROR_AXIS_X_MM, board: Board):
    for shape in board.get_shapes():
        if type(shape) is BoardPolygon:
            new_shape = BoardPolygon()

            for polygon in shape.polygons:
                new_polygon = PolygonWithHoles()
                new_polyline = PolyLine()
                for node in polygon.outline.nodes:
                    new_line = PolyLineNode()
                    new_line.point = mirror_point(node.point, MIRROR_AXIS_X_MM)
                    new_polyline.append(new_line)
                new_polygon.outline = new_polyline
                new_shape.polygons.append(new_polygon)

            new_shape.layer = shape.layer
            new_shape.attributes.stroke.width = shape.attributes.stroke.width
            new_shape.attributes.stroke.style = shape.attributes.stroke.style
            new_shape.attributes.fill.filled = shape.attributes.fill.filled
            
            board.create_items(new_shape)

        elif type(shape) is BoardCircle:
            new_shape = BoardCircle()
            new_shape.center = mirror_point(shape.center, MIRROR_AXIS_X_MM)
            new_shape.radius_point = mirror_point(shape.radius_point, MIRROR_AXIS_X_MM)
            new_shape.layer = shape.layer
            new_shape.attributes.stroke.width = shape.attributes.stroke.width
            new_shape.attributes.stroke.style = shape.attributes.stroke.style
            new_shape.attributes.fill.filled = shape.attributes.fill.filled
            
            board.create_items(new_shape)

        # 他の形状タイプも必要に応じて追加

        else:
            print(f"Shape type {type(shape)} not supported for mirroring.")    

def mirror_text(MIRROR_AXIS_X_MM, board: Board):
    for text in board.get_text():
        new_text = BoardText()
        new_text.value = text.value
        new_text.layer = text.layer
        new_text.attributes.angle = -text.attributes.angle
        new_text.attributes.stroke_width = text.attributes.stroke_width
        new_text.attributes.bold = text.attributes.bold
        new_text.attributes.italic = text.attributes.italic
        new_text.attributes.font_name = text.attributes.font_name
        new_text.attributes.multiline = text.attributes.multiline
        new_text.attributes.size = text.attributes.size
        new_text.position = mirror_point(text.position, MIRROR_AXIS_X_MM)
        board.create_items(new_text)

def main():
    MIRROR_AXIS_X_MM = 200.0  # ミラーリングの基準となるX座標（mm単位）
    board = KiCad().get_board()

    # mirror_shape(MIRROR_AXIS_X_MM, board)
    mirror_text(MIRROR_AXIS_X_MM, board)

if __name__ == "__main__":
    main()
