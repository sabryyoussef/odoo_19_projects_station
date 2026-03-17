# ================================================
# MedTech ERP Documentation to CSV Converter
# ================================================
# Purpose: Convert all markdown documentation to CSV format for AI agent upload
# Created: 2024
# Usage: .\scripts\generate_documentation_csv.ps1
# Output: MedTech_ERP_Documentation.csv (master file)
#         *_docs.csv (individual module files)
#         MedTech_ERP_Documentation.json (JSON export)
# ================================================

# Set working directory
Set-Location -Path $PSScriptRoot\..

Write-Host "`n=== MedTech ERP Documentation CSV Generator ===" -ForegroundColor Cyan
Write-Host "Starting documentation conversion...`n" -ForegroundColor Yellow

# Initialize CSV data array
$csvData = @()

# Define all MedTech modules
$modules = @(
    'medtech_core',
    'medtech_quality_capa',
    'medtech_traceability',
    'medtech_recall',
    'medtech_vendor_compliance',
    'medtech_field_service_history',
    'error_reporter_enterprise'
)

# Process each module
$totalFiles = 0
$totalSections = 0

foreach ($module in $modules) {
    $docsPath = Join-Path $module "docs"
    
    # Check if docs folder exists
    if (-not (Test-Path $docsPath)) {
        Write-Host "⚠ Skipping $module - no docs folder found" -ForegroundColor Yellow
        continue
    }
    
    # Get all markdown files
    $mdFiles = Get-ChildItem -Path $docsPath -Filter "*.md"
    
    if ($mdFiles.Count -eq 0) {
        Write-Host "⚠ Skipping $module - no markdown files found" -ForegroundColor Yellow
        continue
    }
    
    Write-Host "Processing $module ($($mdFiles.Count) files)..." -ForegroundColor Green
    
    foreach ($file in $mdFiles) {
        $totalFiles++
        $docType = $file.BaseName
        
        # Read entire file content
        $content = Get-Content $file.FullName -Raw -Encoding UTF8
        
        if (-not $content) {
            Write-Host "  ⚠ Empty file: $($file.Name)" -ForegroundColor Yellow
            continue
        }
        
        # Split content by markdown headers (##, ###, ####, etc.)
        # Regex pattern: (?m)^##+ matches start of line with 2+ # characters
        $sections = $content -split '(?m)^##+ '
        
        # Process each section
        $sectionCount = 0
        foreach ($section in $sections) {
            # Skip empty sections
            if (-not $section.Trim()) {
                continue
            }
            
            # Split section into lines
            $lines = $section -split "`n"
            
            # First line is the section title
            $sectionTitle = ($lines[0] -replace '^#+\s*', '').Trim()
            
            # Remaining lines are the content
            if ($lines.Length -gt 1) {
                $sectionContent = ($lines[1..($lines.Length - 1)] -join "`n").Trim()
            } else {
                $sectionContent = ""
            }
            
            # Only add if we have content or a title
            if ($sectionTitle -or $sectionContent) {
                $csvData += [PSCustomObject]@{
                    Module = $module
                    DocType = $docType
                    Section = $sectionTitle
                    Content = $sectionContent -replace '"', '""'  # Escape quotes for CSV
                }
                $sectionCount++
                $totalSections++
            }
        }
        
        Write-Host "  ✓ $($file.Name): $sectionCount sections" -ForegroundColor Gray
    }
}

# Export master CSV
Write-Host "`nGenerating CSV files..." -ForegroundColor Yellow

if ($csvData.Count -gt 0) {
    # Master CSV with all modules
    $masterCsv = "MedTech_ERP_Documentation.csv"
    $csvData | Export-Csv -Path $masterCsv -NoTypeInformation -Encoding UTF8
    Write-Host "  ✓ $masterCsv ($($csvData.Count) entries)" -ForegroundColor Green
    
    # Individual module CSVs
    $csvData | Group-Object Module | ForEach-Object {
        $moduleName = $_.Name
        $fileName = "${moduleName}_docs.csv"
        $_.Group | Export-Csv -Path $fileName -NoTypeInformation -Encoding UTF8
        Write-Host "  ✓ $fileName ($($_.Count) entries)" -ForegroundColor Green
    }
    
    # JSON export with metadata
    Write-Host "`nGenerating JSON export..." -ForegroundColor Yellow
    $jsonData = @()
    foreach ($row in $csvData) {
        # Categorize document type
        $category = switch ($row.DocType) {
            'README' { 'Overview' }
            'INSTALLATION' { 'Setup' }
            'USER_GUIDE' { 'Usage' }
            'IMPROVEMENTS' { 'Enhancements' }
            default { 'Other' }
        }
        
        # Calculate word count
        $wordCount = if ($row.Content) {
            ($row.Content -split '\s+' | Where-Object { $_ }).Count
        } else {
            0
        }
        
        $jsonData += @{
            module = $row.Module
            docType = $row.DocType
            section = $row.Section
            content = $row.Content
            metadata = @{
                category = $category
                wordCount = $wordCount
            }
        }
    }
    
    $jsonFile = "MedTech_ERP_Documentation.json"
    $jsonData | ConvertTo-Json -Depth 5 | Out-File $jsonFile -Encoding UTF8
    $jsonSize = [math]::Round((Get-Item $jsonFile).Length / 1MB, 2)
    Write-Host "  ✓ $jsonFile ($jsonSize MB)" -ForegroundColor Green
    
} else {
    Write-Host "⚠ No documentation found to export!" -ForegroundColor Red
    exit 1
}

# Summary
Write-Host "`n=== Conversion Complete ===" -ForegroundColor Cyan
Write-Host "Modules Processed: $($modules.Count)" -ForegroundColor Green
Write-Host "Files Processed: $totalFiles" -ForegroundColor Green
Write-Host "Sections Extracted: $totalSections" -ForegroundColor Green
Write-Host "`nFiles Generated:" -ForegroundColor Yellow
Write-Host "  - MedTech_ERP_Documentation.csv (master)" -ForegroundColor Gray
Write-Host "  - MedTech_ERP_Documentation.json (JSON)" -ForegroundColor Gray
Write-Host "  - 7 individual module CSV files" -ForegroundColor Gray

# Statistics breakdown
Write-Host "`nBy Module:" -ForegroundColor Yellow
$csvData | Group-Object Module | Sort-Object Count -Descending | ForEach-Object {
    Write-Host "  $($_.Name): $($_.Count) sections" -ForegroundColor Gray
}

Write-Host "`nBy Document Type:" -ForegroundColor Yellow
$csvData | Group-Object DocType | Sort-Object Count -Descending | ForEach-Object {
    Write-Host "  $($_.Name): $($_.Count) sections" -ForegroundColor Gray
}

Write-Host "`n✓ Ready for AI agent upload!" -ForegroundColor Green
Write-Host "See AI_KNOWLEDGE_BASE_README.md for integration guide.`n" -ForegroundColor Cyan
