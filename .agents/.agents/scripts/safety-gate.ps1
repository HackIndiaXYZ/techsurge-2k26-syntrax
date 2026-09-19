$inputString = [Console]::In.ReadToEnd()
$output = @{ decision = "allow" }
$output | ConvertTo-Json -Compress | Write-Host

