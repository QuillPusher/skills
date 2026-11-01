# OCR one or more images with the Windows built-in engine (Windows.Media.Ocr).
# No installation needed on Windows 10/11; uses the languages installed in Settings.
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File ocr_windows.ps1 page1.png [page2.png ...] [-Language en-US]
#
# Prints the recognised text for each file, separated by a line "===== <file>".
# Lines that are clearly further apart than normal line spacing get a blank
# line between them, so paragraphs survive. Called by extract_pdf.py --ocr windows.
[CmdletBinding(PositionalBinding = $false)]
param(
  [Parameter(Mandatory = $true, Position = 0, ValueFromRemainingArguments = $true)] [string[]] $Files,
  [Parameter()] [string] $Language = ''
)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType = WindowsRuntime]
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics, ContentType = WindowsRuntime]

$asTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
  })[0]
function Await($op, $type) {
  $task = $asTask.MakeGenericMethod($type).Invoke($null, @($op))
  $task.Wait() | Out-Null
  $task.Result
}

if ($Language) {
  $null = [Windows.Globalization.Language, Windows.Globalization, ContentType = WindowsRuntime]
  $lang = New-Object Windows.Globalization.Language -ArgumentList $Language
  $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($lang)
} else {
  $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
}
if (-not $engine) { Write-Error 'No OCR language available. Install a language pack in Windows Settings > Time & language.'; exit 2 }

foreach ($f in $Files) {
  $path = (Resolve-Path $f).Path
  Write-Output "===== $f"
  $file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($path)) ([Windows.Storage.StorageFile])
  $stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
  $decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
  $bitmap = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
  $result = Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])

  # Sort lines top to bottom and insert a blank line where the vertical gap is large.
  $lines = @($result.Lines | ForEach-Object {
      $rects = $_.Words | ForEach-Object { $_.BoundingRect }
      $top = ($rects | Measure-Object -Property Y -Minimum).Minimum
      $bottom = ($rects | ForEach-Object { $_.Y + $_.Height } | Measure-Object -Maximum).Maximum
      $left = ($rects | Measure-Object -Property X -Minimum).Minimum
      [pscustomobject]@{ Text = $_.Text; Top = $top; Bottom = $bottom; Left = $left; Height = ($bottom - $top) }
    } | Sort-Object Top, Left)
  $prevBottom = $null
  $heights = $lines | ForEach-Object { $_.Height }
  $typical = if ($heights) { ($heights | Sort-Object)[[int]($heights.Count / 2)] } else { 0 }
  foreach ($l in $lines) {
    if ($null -ne $prevBottom -and ($l.Top - $prevBottom) -gt (0.9 * $typical)) { Write-Output '' }
    Write-Output $l.Text
    $prevBottom = $l.Bottom
  }
  $stream.Dispose()
}
