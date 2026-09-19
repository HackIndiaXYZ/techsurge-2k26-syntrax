$ErrorActionPreference = "Stop"

$inputString = [Console]::In.ReadToEnd()
if ([string]::IsNullOrWhiteSpace($inputString)) {
    @{ decision = "allow" } | ConvertTo-Json -Compress | Write-Host
    exit 0
}

$inputJson = $inputString | ConvertFrom-Json

if ($inputJson.toolCall.name -ne "run_command") {
    @{ decision = "allow" } | ConvertTo-Json -Compress | Write-Host
    exit 0
}

$cmd = $inputJson.toolCall.args.CommandLine
$decision = "allow"
$reason = ""

if (-not [string]::IsNullOrWhiteSpace($cmd)) {
    # 1. Deny rules (Extremely dangerous root deletion)
    if ($cmd -match "(?i)\brm\s+-rf\s+/\s*(?:\n|$|;)" -or $cmd -match "(?i)\bRemove-Item\s+-Recurse\s+-Force\s+[A-Z]:\\\s*(?:\n|$|;)") {
        $decision = "deny"
        $reason = "Extremely dangerous root deletion operation blocked."
    }
    # 2. Ask rules (Destructive / Delete)
    elseif ($cmd -match "(?i)\b(Remove-Item|rm|rmdir|del|erase)\b" -or 
            $cmd -match "(?i)\b(git clean)\b" -or
            $cmd -match "(?i)\b(DROP\s+(TABLE|DATABASE|SCHEMA|INDEX|VIEW|ROLE|USER)|DELETE\s+FROM|TRUNCATE\s+(TABLE)?)\b" -or
            $cmd -match "(?i)\bdocker\s+(rm|rmi|system\s+prune|volume\s+rm|network\s+rm)\b") {
        
        $decision = "force_ask"
        $reason = "Destructive/Delete operation detected. Human approval explicitly required."
    }
}

$output = @{
    decision = $decision
    reason = $reason
}

$output | ConvertTo-Json -Compress | Write-Host

