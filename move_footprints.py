from kipy import KiCad
from kipy.geometry import Angle
from kicad_utils import mirror_point
from fp_mapping import FP_MAPPING, MIRROR_AXIS_X_MM

def move_footprints_from_FP_MAPPING(MIRROR_AXIS_X_MM, board, FP_MAPPING):
    fp_dict = {fp.reference_field.text.value: fp for fp in board.get_footprints()}
    for r_ref, l_ref in FP_MAPPING.items():
        if r_ref in fp_dict and l_ref in fp_dict:
            r_fp = fp_dict[r_ref]
            l_fp = fp_dict[l_ref]
        
        # 位置のミラーリング
            l_fp.position = mirror_point(r_fp.position, MIRROR_AXIS_X_MM)
        
        # 角度のミラーリング
        # 右手が10度なら左手は-10度（350度）
            r_angle_deg = r_fp.orientation.degrees
            l_new_angle = -r_angle_deg
            l_fp.orientation = Angle.from_degrees(l_new_angle)
        
        # 表面/裏面フリップがある場合はもう少し複雑になりますが、
        # 基本的に分離キーボードで同一面ならこれでOKです。
            board.update_items(l_fp)
            print(f"Mirrored {r_ref} to {l_ref}")
        else:
            print(f"Warning: RefDes pair not found: {r_ref} - {l_ref}")

def main():
    board = KiCad().get_board()

    move_footprints_from_FP_MAPPING(MIRROR_AXIS_X_MM, board, FP_MAPPING)


if __name__ == "__main__":
    main()
