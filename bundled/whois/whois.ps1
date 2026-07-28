param(
    [Parameter(Mandatory=$true)]
    [string]$Domain
)

$whoisServer = "whois.internic.net"
try {
    $tcp = New-Object System.Net.Sockets.TcpClient($whoisServer, 43)
    $stream = $tcp.GetStream()
    $writer = New-Object System.IO.StreamWriter($stream)
    $writer.WriteLine($Domain)
    $writer.Flush()
    
    $reader = New-Object System.IO.StreamReader($stream)
    while ($line = $reader.ReadLine()) {
        if ($line -match "^>") { continue }
        Write-Host $line
    }
    
    $reader.Close()
    $writer.Close()
    $tcp.Close()
} catch {
    Write-Error "Error querying WHOIS: $_"
}
