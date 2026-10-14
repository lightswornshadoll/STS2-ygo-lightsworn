# 部署 dist 三件套到游戏 mods 目录（联机兼容轮新增；robocopy /MIR /IS /IT 防同分钟时间戳跳过）
# 用法：powershell -ExecutionPolicy Bypass -File tools\deploy_dist.ps1
$src = 'D:\1-workdata\lightsworn_mod\dist\lightsworn'
$dst = 'D:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2\mods\Lightsworn'
robocopy $src $dst /MIR /IS /IT /R:2 /W:2 /NFL /NDL /NJH /NJS
Write-Host ("robocopy exit=" + $LASTEXITCODE)
Get-ChildItem $dst | Format-Table Name, Length, LastWriteTime -AutoSize
