$pptxPath = Join-Path (Get-Location) "TeamName_ProjectName_SchoolName.pptx"
$pdfPath = Join-Path (Get-Location) "TeamName_ProjectName_SchoolName.pdf"

Write-Host "Opening PowerPoint COM object..."
$ppt = New-Object -ComObject PowerPoint.Application
$pres = $ppt.Presentations.Open($pptxPath, [Microsoft.Office.Core.MsoTriState]::msoTrue, [Microsoft.Office.Core.MsoTriState]::msoFalse, [Microsoft.Office.Core.MsoTriState]::msoFalse)

Write-Host "Exporting to PDF: $pdfPath"
$pres.SaveAs($pdfPath, 32)
$pres.Close()
$ppt.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null

Write-Host "Export complete! PDF generated successfully."
