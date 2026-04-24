from kipy.geometry import Vector2

def mirror_point(point: Vector2, axis_x_mm: float) -> Vector2:
    """
    ポイントをX軸に対して線対称に移動します。
    KiCadの内部単位(nm)で計算します。
    
    :param point: 対象の点 (Vector2)
    :param axis_x_mm: 対称軸のX座標 (mm)
    :return: 移動後の点 (Vector2)
    """
    axis_x_nm = int(axis_x_mm * 1000000)
    new_x = 2 * axis_x_nm - point.x
    return Vector2.from_xy(new_x, point.y)