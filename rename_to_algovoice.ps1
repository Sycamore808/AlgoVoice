# AlgoVoice 批量重命名脚本
# 将所有文件中的 FinLoom 替换为 AlgoVoice

Write-Host "开始批量替换 FinLoom -> AlgoVoice..." -ForegroundColor Green

# 定义要处理的文件扩展名
$extensions = @("*.py", "*.txt", "*.md", "*.yaml", "*.json", "*.html", "*.vue", "*.js", "*.css", "*.bat")

# 替换所有文本文件中的内容
foreach ($ext in $extensions) {
    $files = Get-ChildItem -Path . -Filter $ext -Recurse -File -ErrorAction SilentlyContinue
    
    foreach ($file in $files) {
        try {
            $content = Get-Content $file.FullName -Raw -Encoding UTF8 -ErrorAction Stop
            
            if ($content -match "FinLoom|Finloom|finloom") {
                Write-Host "处理: $($file.FullName)" -ForegroundColor Yellow
                
                $newContent = $content -replace "FinLoom", "AlgoVoice"
                $newContent = $newContent -replace "Finloom", "AlgoVoice"
                $newContent = $newContent -replace "finloom", "algovoice"
                
                Set-Content -Path $file.FullName -Value $newContent -Encoding UTF8 -NoNewline
                Write-Host "  ✓ 完成" -ForegroundColor Green
            }
        }
        catch {
            Write-Host "  跳过 (无法读取): $($file.FullName)" -ForegroundColor Gray
        }
    }
}

Write-Host ""
Write-Host "文本替换完成！" -ForegroundColor Green
Write-Host ""
Write-Host "请注意：文件夹重命名需要手动执行以下命令：" -ForegroundColor Cyan
Write-Host ""
Write-Host "git mv FinLoom-server-main AlgoVoice-server-main" -ForegroundColor White
Write-Host "git mv FinLoom-server-develop AlgoVoice-server-develop" -ForegroundColor White
Write-Host ""

