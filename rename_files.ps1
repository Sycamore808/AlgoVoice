# Replace FinLoom with AlgoVoice in all text files

Write-Host "Replacing FinLoom with AlgoVoice..." -ForegroundColor Green

$extensions = @("*.py", "*.txt", "*.md", "*.yaml", "*.json", "*.html", "*.vue", "*.js", "*.css", "*.bat", "*.sh")

foreach ($ext in $extensions) {
    Get-ChildItem -Path . -Filter $ext -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
        try {
            $content = Get-Content $_.FullName -Raw -Encoding UTF8
            if ($content -match "FinLoom|Finloom|finloom") {
                Write-Host "Processing: $($_.Name)"
                $content = $content -replace "FinLoom", "AlgoVoice"
                $content = $content -replace "Finloom", "AlgoVoice"  
                $content = $content -replace "finloom", "algovoice"
                [System.IO.File]::WriteAllText($_.FullName, $content, [System.Text.Encoding]::UTF8)
            }
        } catch {
            Write-Host "Skipped: $($_.Name)" -ForegroundColor Gray
        }
    }
}

Write-Host "Done!" -ForegroundColor Green

