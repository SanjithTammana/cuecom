# cuecom setup for Windows (x64). Run from the repo root in PowerShell: .\setup_windows.ps1
# Clone into a short path (e.g. C:\code\cuecom): torch's deep header paths break the install past 260 characters
# unless Windows long paths are enabled.
$ErrorActionPreference = 'Stop'

py -3.11 --version
if (-not $?) { throw 'Python 3.11 is required (mediapipe 0.10.7 / envisionhgdetector). Install it from python.org.' }

py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install --no-deps envisionhgdetector==3.0.8
.venv\Scripts\python.exe -c "import cuecom.perception.vision.video, cuecom.perception.audio.vocalization, cuecom.inference.retrieval, cuecom.output.tts; print('cuecom imports OK')"

Write-Host ''
Write-Host 'Done. Prepare models (docs/SESSION-SETUP.md), then run: .\.venv\Scripts\python.exe -m apps.session --assessment'
