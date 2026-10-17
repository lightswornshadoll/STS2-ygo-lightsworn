# 暗黑界的龙神王 格拉法 — Boss 素材（已处理）

从 `D:\download\chrome_download\光道mod素材\暗黑界的龙神王` 的三张原图处理而来，
按 `design\boss制作需求.md` 与原版 Boss 实测规格输出，可直接用于 mod。

| 用途 | 文件 | 尺寸 | 说明 |
|---|---|---|---|
| 战斗立绘 | `01_战斗立绘/dark_world_grapha.png` | 1600×1200 RGBA | 透明底，已去白底/水印/封闭白洞 |
| 地图节点图标 | `02_地图节点/dark_world_grapha_boss_icon.png` | 350×307 RGBA | **白色线稿遮罩**，游戏内会被 act 颜色染色 |
| 地图节点描边 | `02_地图节点/dark_world_grapha_boss_icon_outline.png` | 350×307 RGBA | 白色圆盘剪影，垫在线稿后面 |
| 地图节点原色版 | `02_地图节点/dark_world_grapha_boss_icon_color.png` | 350×307 RGBA | 黑圆盘+白线稿，仅供自定义地图节点，默认地图节点不要用 |
| 历史记录图标（主） | `03_历史记录/dark_world_grapha_boss.png` | 85×85 RGBA | 彩色头部特写（圆形取景），推荐用这个 |
| 历史记录描边（主） | `03_历史记录/dark_world_grapha_boss_outline.png` | 85×85 RGBA | 白色剪影，外扩约 2px |
| 历史记录（全身备选） | `03_历史记录/dark_world_grapha_boss_full.png` | 85×85 RGBA | 保留原图全身构图，头部较小 |
| 历史记录描边（全身） | `03_历史记录/dark_world_grapha_boss_full_outline.png` | 85×85 RGBA | 全身版白色剪影，外扩约 2px |
| 预览 | `00_预览.png` | 1400×980 | 三张成品的拼图预览 |

统一占位 ID：`dark_world_grapha`。
如果最终 encounter 类名/ID 不是这个，把文件名前缀换掉即可（见下方“落盘路径”）。

---

## 1. 做了什么处理

### 战斗立绘

- 原图 1536×1536，白底且右下角有 AI 水印。
- 按 Boss 实际内容裁切，裁切范围避开了水印；四边泛洪去白底。
- 翅膀与身体之间有几块**被包住的纯白背景**（泛洪到不了），用低分辨率连通域识别后挖掉，共约 4.46 万像素。
- 边界用亮度估 alpha 并反白边，输出 1600×1200 透明画布。
- 内容 bbox：`(71, 78) - (1527, 1122)`；底部（脚/爪）在 y≈1122。
  静态立绘若按“脚底贴地”定位，可用这个底边，而不是画布底边 1200。

### 地图节点图标

原版地图节点 `NBossMapPoint` 会对图标做 `SelfModulate`：

```csharp
_placeholderImage.SelfModulate   = _act.MapTraveledColor;  // 深色
_placeholderOutline.SelfModulate = _act.MapBgColor;        // 浅灰
```

所以这里输出的是**白色线稿遮罩 + 白色圆盘描边**：
游戏里线稿被染成深色、圆盘被染成浅灰，最终是“浅色圆盘 + 深色线稿”的徽章效果。
`dark_world_grapha_boss_icon_color.png` 保留了你原图的黑圆盘白线稿，
但**默认地图节点会把它整体染暗，线稿会几乎看不见**，只适合以后换自定义地图节点/Spine 节点时用。

### 历史记录图标

- 主图标是**头部特写**（圆形取景）：85×85 下头、角、红眼都清晰，和原版历史图标“头部特写”的用法一致。
- 之所以用圆形取景：直接方形裁头时，裁切边会在描边里形成一圈方框，很难看；圆形遮罩把边缘收干净。
- 描边是白色剪影，比彩色图标外扩约 2px；顶栏/历史界面会按原版规则使用。
- 另附**全身版** `*_boss_full.png` + `_full_outline.png`，保留原图完整构图；85×85 下头部较小，只作备选。

---

## 2. 落盘路径

假设 mod 工程根为 `mod\lightsworn\lightsworn\`：

```
images\monsters\dark_world_grapha.png
images\map\lightsworn\dark_world_grapha_boss_icon.png
images\map\lightsworn\dark_world_grapha_boss_icon_outline.png
images\ui\run_history\dark_world_grapha_boss.png
images\ui\run_history\dark_world_grapha_boss_outline.png
```

`EncounterAssetProfile` 建议写法：

```csharp
public override EncounterAssetProfile AssetProfile => new(
    // 注意：BossNodeSpinePath 这里复用作“PNG 路径前缀”，不要带 .png
    // 游戏会自己拼 .png 和 _outline.png
    BossNodeSpinePath: "res://lightsworn/images/map/lightsworn/dark_world_grapha_boss_icon",
    RunHistoryIconPath: "res://lightsworn/images/ui/run_history/dark_world_grapha_boss.png",
    RunHistoryIconOutlinePath: "res://lightsworn/images/ui/run_history/dark_world_grapha_boss_outline.png");
```

历史图标和地图节点都建议显式填：历史图标不填会去游戏本体的
`images/ui/run_history/<encounter_id>.png` 找；地图节点不填会走默认的
`animations/map/<encounter_id>/...` Spine 路径——两者都找不到 mod 目录里的图。

战斗立绘由静态怪物视觉代码加载：

```csharp
Texture = ResourceLoader.Load<Texture2D>("res://lightsworn/images/monsters/dark_world_grapha.png")
```

1600×1200 是横向构图；具体 `Scale` / `Position` 按战斗台高度调，
参考本 mod 圣女战斗立绘的 0.33 缩放、脚底贴地的写法即可。

---

## 3. 重新生成

```bash
cd D:/1-workdata/lightsworn_mod/tools
py make_grapha_boss_assets.py
```

输入路径写死在脚本顶部；换图时改 `SRC` / 三个文件名即可。
脚本会覆盖 `design/boss素材_暗黑界的龙神王/` 下的同名输出。

> 原图是 AI 生成素材，右下角水印已在裁切时排除；正式发布前请确认素材来源与授权。
