def print_detail(fp):
    """
    KiCadオブジェクトの詳細なプロパティを出力するデバッグ用関数。
    よく使われるプロパティを先頭に表示し、その後、他の公開属性をリストアップします。
    """
    print("type:", type(fp).__name__)
    
    # よくあるプロパティを優先して出力
    common_attrs = (
        "get_reference", "get_value", "reference", "value", "ref",
        "get_position", "get_rotation", "get_angle"
    )
    for name in common_attrs:
        if hasattr(fp, name):
            try:
                attr = getattr(fp, name)
                if callable(attr):
                    val = attr()
                else:
                    val = attr
                print(f"{name}: {val}")
            except Exception as e:
                print(f"{name}: <error: {e}>")

    # それ以外の公開属性（呼び出し可能でなければ値を表示）
    for name in dir(fp):
        if name.startswith("_") or name in common_attrs:
            continue
        try:
            attr = getattr(fp, name)
            if callable(attr):
                print(f"{name}(): <callable>")
            else:
                val = repr(attr)
                print(f"{name}: {val}")
        except Exception:
            # 属性へのアクセスでエラーが発生する可能性があるものは無視
            pass