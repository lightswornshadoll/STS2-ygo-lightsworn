# 联机实测用窗口自动化工具（本机双开驱动）
# 用法：
#   powershell -File tools\wininput.ps1 list                     列出游戏窗口
#   powershell -File tools\wininput.ps1 shot <out.png> [hwnd]    截屏（默认整个虚拟屏幕）
#   powershell -File tools\wininput.ps1 click <x> <y>            在屏幕坐标点击（含激活窗口）
#   powershell -File tools\wininput.ps1 keys "<keys>"            发送按键（SendKeys 语法：{ENTER}、{ESC}、abc）
#   powershell -File tools\wininput.ps1 focus <hwnd>             激活指定窗口
#   powershell -File tools\wininput.ps1 launch1 / launch2        启动游戏实例（窗口化、左右分屏）
param(
    [Parameter(Position = 0)][string]$cmd,
    [Parameter(Position = 1)][string]$a1,
    [Parameter(Position = 2)][string]$a2,
    [Parameter(Position = 3)][string]$a3
)

# 关键：先声明 Per-Monitor-V2 DPI 感知——否则 GetWindowRect/CopyFromScreen/SetCursorPos 走"虚拟化坐标"，
# 150% 缩放下（2560x1600 实屏报 1707x1067）点击会偏移、截图会错位。
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class DpiFix {
    [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr ctx);
}
"@
[void][DpiFix]::SetProcessDpiAwarenessContext([IntPtr](-4))

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class W {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
    [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr hWnd, int x, int y, int w, int h, bool repaint);
    [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr hWnd, IntPtr after, int x, int y, int w, int h, uint flags);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint x, uint y, uint d, IntPtr e);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
}
"@

function Get-GameWindows {
    Get-Process SlayTheSpire2 -ErrorAction SilentlyContinue |
        Where-Object { $_.MainWindowHandle -ne 0 } |
        Select-Object Id, MainWindowTitle, MainWindowHandle
}

switch ($cmd) {
    'list' {
        Get-GameWindows | Format-Table -AutoSize
    }
    'rects' {
        foreach ($p in (Get-Process SlayTheSpire2 -ErrorAction SilentlyContinue)) {
            if ($p.MainWindowHandle -eq 0) { continue }
            $r = New-Object W+RECT
            [void][W]::GetWindowRect($p.MainWindowHandle, [ref]$r)
            Write-Host ("pid={0} hwnd={1} rect=({2},{3})-({4},{5}) size={6}x{7}" -f `
                $p.Id, $p.MainWindowHandle, $r.L, $r.T, $r.R, $r.B, ($r.R - $r.L), ($r.B - $r.T))
        }
    }
    'shot' {
        $out = $a1
        $b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
        if ($a2) {
            $h = [IntPtr][int]$a2
            $r = New-Object W+RECT
            [void][W]::GetWindowRect($h, [ref]$r)
            $b = New-Object System.Drawing.Rectangle($r.L, $r.T, ($r.R - $r.L), ($r.B - $r.T))
        }
        $bmp = New-Object System.Drawing.Bitmap($b.Width, $b.Height)
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        $g.CopyFromScreen($b.Location, [System.Drawing.Point]::Empty, $b.Size)
        $bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
        $g.Dispose(); $bmp.Dispose()
        Write-Host "saved $out ($($b.Width)x$($b.Height))"
    }
    'drag' {
        # drag <x1> <y1> <x2> <y2>：按住左键从起点拖到终点（分步移动）
        $x1=[int]$a1; $y1=[int]$a2; $x2=[int]$a3
        # a3/a4 限制：这里用固定参数顺序 x1 y1 x2 y2 -> 需要第4个参数，改从环境变量读 y2
        $y2=[int]$env:DRAG_Y2
        [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($x1, $y1)
        Start-Sleep -Milliseconds 200
        [W]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)
        Start-Sleep -Milliseconds 200
        for ($i=1; $i -le 12; $i++) {
            $mx=[int]($x1+($x2-$x1)*$i/12); $my=[int]($y1+($y2-$y1)*$i/12)
            [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($mx, $my)
            Start-Sleep -Milliseconds 25
        }
        Start-Sleep -Milliseconds 200
        [W]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)
        Write-Host "dragged $x1,$y1 -> $x2,$y2"
    }
    'press' { [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point(([int]$a1),([int]$a2)); Start-Sleep -Milliseconds 200; [W]::mouse_event(0x0002,0,0,0,[IntPtr]::Zero); Write-Host 'press' }
    'release' { [W]::mouse_event(0x0004,0,0,0,[IntPtr]::Zero); Write-Host 'release' }
    'move' {
        [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point(([int]$a1), ([int]$a2))
        Write-Host "moved to $a1,$a2"
    }
    'click' {
        $x = [int]$a1; $y = [int]$a2
        [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($x, $y)
        Start-Sleep -Milliseconds 120
        [W]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)   # LEFTDOWN
        Start-Sleep -Milliseconds 60
        [W]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)   # LEFTUP
        Write-Host "clicked $x,$y"
    }
    'keys' {
        [System.Windows.Forms.SendKeys]::SendWait($a1)
        Write-Host "sent keys: $a1"
    }
    'focus' {
        # 可靠的窗口激活：最小化→还原（强制置前）+ SetForegroundWindow
        $h = [IntPtr][int]$a1
        [void][W]::ShowWindow($h, 6)     # SW_MINIMIZE
        Start-Sleep -Milliseconds 200
        [void][W]::ShowWindow($h, 9)     # SW_RESTORE
        Start-Sleep -Milliseconds 150
        [void][W]::SetForegroundWindow($h)
        Start-Sleep -Milliseconds 300
        $fg = [W]::GetForegroundWindow()
        Write-Host ("focused {0} foreground={1} ok={2}" -f $h, $fg, ($fg -eq $h))
    }
    'fg' {
        Write-Host ("foreground hwnd=" + [W]::GetForegroundWindow())
    }
    'place' {
        # place <hwnd> <x> <y>：强制移动窗口（游戏忽略 --position/--resolution，只能外部摆）
        $h = [IntPtr][int]$a1
        [void][W]::MoveWindow($h, [int]$a2, [int]$a3, 853, 1060, $true)
        Write-Host "placed $a1"
    }
    'placeboth' {
        # 左右分屏：hwnd1 在左、hwnd2 在右（各 853 宽）
        [void][W]::MoveWindow([IntPtr][int]$a1, 0, 0, 853, 1060, $true)
        [void][W]::MoveWindow([IntPtr][int]$a2, 854, 0, 853, 1060, $true)
        Write-Host 'placed both'
    }
    'launch1' {
        Start-Process 'D:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2\SlayTheSpire2.exe' `
            -ArgumentList '--windowed', '--resolution', '850x700', '--position', '0,0'
        Write-Host 'launched instance 1'
    }
    'launch2' {
        Start-Process 'D:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2\SlayTheSpire2.exe' `
            -ArgumentList '--windowed', '--resolution', '850x700', '--position', '855,0'
        Write-Host 'launched instance 2'
    }
    default { Write-Host "unknown cmd: $cmd" }
}
