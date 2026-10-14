extends SceneTree
func _init():
	var tex: Texture2D = load("res://probe/round_tea_party.png-3a62997529796a13ef76505a07ec1667.bptc.ctex")
	if tex == null:
		print("LOAD FAILED")
	else:
		print("SIZE=", tex.get_size())
	quit()
