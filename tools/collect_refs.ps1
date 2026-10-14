# 采集编译参考程序集（refs）
# 用途：把「游戏 0.111.0 的 sts2.dll/0Harmony.dll + RitsuLib 全量」复制到 mod\lightsworn\refs\
#       之后编译永远读 refs，与 Steam 当前分支无关 —— 不用再为编译切 beta 分支
#
# 用法（只需在游戏处于 0.111.0 分支时运行一次）：
#   1. Steam 库 → 杀戮尖塔2 → 右键属性 → 测试版 → 选 0.111.0 → 等更新完成
#   2. 双击或右键运行本脚本（tools\collect_refs.ps1）
#   3. 校验通过后，可随时把 Steam 切回正式版玩（编译不再受影响）
#
# 说明：参考程序集只用于编译期（HintPath，Private=false 不随构建输出），
#       运行期用游戏自带的 sts2.dll —— 所以 0.111 编译的 dll 在正式版 0.107.1 上照常运行
#       （跨版本 API 差异由 mod 内 LsCompat/HonestPowerLegacyPatch 在运行期闭合，已实测）。

$ErrorActionPreference = 'Stop'

$gameDir   = 'D:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2'
$workshop  = 'D:\Program Files (x86)\Steam\steamapps\workshop\content\2868840\3747602295'
$refRoot   = 'D:\1-workdata\lightsworn_mod\mod\lightsworn\refs'

$gameData  = Join-Path $gameDir 'data_sts2_windows_x86_64'
$gameSts2  = Join-Path $gameData 'sts2.dll'
$gameHarm  = Join-Path $gameData '0Harmony.dll'
$refData   = Join-Path $refRoot 'data'
$refRitsu  = Join-Path $refRoot 'RitsuLib'

Write-Host "== 采集编译参考程序集 ==" -ForegroundColor Cyan

# ---- 1. 校验游戏安装与版本 ----
if (-not (Test-Path $gameSts2))  { Write-Host "找不到 $gameSts2" -ForegroundColor Red; exit 1 }
if (-not (Test-Path $gameHarm))  { Write-Host "找不到 $gameHarm" -ForegroundColor Red; exit 1 }

$release = Join-Path $gameDir 'release_info.json'
if (Test-Path $release) {
    $ri = Get-Content $release -Raw | ConvertFrom-Json
    Write-Host "游戏当前版本: $($ri.version) (branch $($ri.branch))"
    if ($ri.version -notmatch '^v?0\.111\.') {
        Write-Host "⚠ 当前不是 0.111.x 分支——refs 必须来自 0.111（源码按 6 参 ModifyDamageMultiplicative 编译）。" -ForegroundColor Yellow
        Write-Host "  请先在 Steam 里切到 0.111.0 分支并等更新完成，再运行本脚本。" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "⚠ 没有 release_info.json，无法校验版本（继续）" -ForegroundColor Yellow
}

$sts2Size = (Get-Item $gameSts2).Length
Write-Host ("sts2.dll: {0:N1} MB" -f ($sts2Size / 1MB))
if ($sts2Size -lt 8MB) { Write-Host "⚠ sts2.dll 大小异常（<8MB），可能不是完整的 0.111 版本" -ForegroundColor Yellow }

# ---- 2. 采集 ----
New-Item -ItemType Directory -Force -Path $refData | Out-Null
Copy-Item $gameSts2 $refData -Force
Copy-Item $gameHarm $refData -Force
Write-Host "已复制: data\sts2.dll, data\0Harmony.dll"

if (Test-Path (Join-Path $workshop 'RitsuLib.References.props')) {
    if (Test-Path $refRitsu) { Remove-Item $refRitsu -Recurse -Force }
    Copy-Item $workshop $refRitsu -Recurse -Force
    Write-Host "已复制: RitsuLib\ (workshop 3747602295 全量)"
} else {
    Write-Host "⚠ 找不到 RitsuLib（$workshop）——请确认创意工坊已订阅 RitsuLib" -ForegroundColor Red
    exit 1
}

# ---- 3. 校验产物 ----
Write-Host ""
Write-Host "== 校验 ==" -ForegroundColor Cyan
$ok = $true
foreach ($f in @('data\sts2.dll', 'data\0Harmony.dll', 'RitsuLib\RitsuLib.References.props',
                'RitsuLib\compat\0.111.0\STS2-RitsuLib.dll', 'RitsuLib\compat\0.111.0\STS2-RitsuLib.Runtime.dll')) {
    $p = Join-Path $refRoot $f
    if (Test-Path $p) {
        Write-Host ("  [OK] {0}  ({1:N0} bytes)" -f $f, (Get-Item $p).Length)
    } else {
        Write-Host ("  [缺失] {0}" -f $f) -ForegroundColor Red
        $ok = $false
    }
}

if ($ok) {
    Write-Host ""
    Write-Host "✔ 完成！现在可以直接 dotnet build 编译（无论 Steam 在哪个分支）。" -ForegroundColor Green
    Write-Host "  之后可随时把游戏切回正式版玩，编译不受影响。"
} else {
    Write-Host "✘ 有缺失项，请检查上面的错误。" -ForegroundColor Red
    exit 1
}
