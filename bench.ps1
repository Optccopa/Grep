function Measure-Best {
    param([string]$Exe, [string]$Path, [string]$Pattern, [int]$Runs = 3)

    $best = [double]::MaxValue
    for ($i = 0; $i -lt $Runs; $i++) {
        $t = (Measure-Command { & $Exe $Path $Pattern > $null }).TotalMilliseconds
        if ($t -lt $best) { $best = $t }
    }
    [math]::Round($best)
}

Measure-Best ./build/Release/grep.exe . "\bkmalloc\w*\("