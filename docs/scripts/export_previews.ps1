$pptxPath = Join-Path (Get-Location) "TeamName_ProjectName_SchoolName.pptx"
$previewDir = Join-Path (Get-Location) "slide_previews"
if (!(Test-Path $previewDir)) { New-Item -ItemType Directory -Path $previewDir | Out-Null }

$ppt = New-Object -ComObject PowerPoint.Application
$pres = $ppt.Presentations.Open($pptxPath, [Microsoft.Office.Core.MsoTriState]::msoTrue, [Microsoft.Office.Core.MsoTriState]::msoFalse, [Microsoft.Office.Core.MsoTriState]::msoFalse)

for ($i = 1; $i -le $pres.Slides.Count; $i++) {
    $slide = $pres.Slides.Item($i)
    $pngPath = Join-Path $previewDir ("slide_{0:D2}.png" -f $i)
    $slide.Export($pngPath, "PNG", 1920, 1080)
    Write-Host "Exported slide $i to $pngPath"
}

$pres.Close()
$ppt.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
Write-Host "All slides exported to PNG!"
