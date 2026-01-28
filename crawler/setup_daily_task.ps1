# 设置每日爬取定时任务
# 以管理员权限运行此脚本

$taskName = "MutsumiSaki-DailyCrawl"
$pythonPath = "python"  # 或者使用完整路径如 "C:\Python312\python.exe"
$scriptPath = "D:\mutsumi-saki-archive\crawler\daily_crawl.py"
$workingDir = "D:\mutsumi-saki-archive\crawler"

# 检查任务是否已存在
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "任务 '$taskName' 已存在，正在更新..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# 创建触发器 - 每天凌晨3点运行
$trigger = New-ScheduledTaskTrigger -Daily -At 3:00AM

# 创建操作
$action = New-ScheduledTaskAction `
    -Execute $pythonPath `
    -Argument $scriptPath `
    -WorkingDirectory $workingDir

# 创建设置
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

# 创建主体（使用当前用户）
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

# 注册任务
Register-ScheduledTask `
    -TaskName $taskName `
    -Description "每日爬取睦祥资源（Pixiv 插画和小说）" `
    -Trigger $trigger `
    -Action $action `
    -Settings $settings `
    -Principal $principal

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "✅ 定时任务创建成功！" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""
Write-Host "任务名称: $taskName"
Write-Host "运行时间: 每天凌晨 3:00"
Write-Host "脚本路径: $scriptPath"
Write-Host "日志目录: $workingDir\logs\"
Write-Host ""
Write-Host "你可以使用以下命令管理任务：" -ForegroundColor Yellow
Write-Host "  查看任务: Get-ScheduledTask -TaskName '$taskName'"
Write-Host "  手动运行: Start-ScheduledTask -TaskName '$taskName'"
Write-Host "  禁用任务: Disable-ScheduledTask -TaskName '$taskName'"
Write-Host "  删除任务: Unregister-ScheduledTask -TaskName '$taskName'"
Write-Host ""
