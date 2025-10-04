# logic.py
import os
import shutil
import ctypes
import sys
import logging
import winreg
import threading
from datetime import datetime
import pyaudio
import subprocess
import tempfile
from config import get_logger

def setup_logging():
    """Wird nicht mehr benötigt - Logging wird in config.py eingerichtet"""
    pass

def is_admin():
    try:
        result = ctypes.windll.shell32.IsUserAnAdmin()
        logger = get_logger()
        logger.log_debug(f"Admin-Rechte Check aufgerufen")
        logger.log_info(f"Admin-Rechte: {'✅ Vorhanden' if result else '❌ Nicht vorhanden'}")
        return result
    except Exception as e:
        logger = get_logger()
        logger.log_error("Fehler beim Admin-Rechte Check", exc_info=e)
        return False

def elevate_to_admin():
    try:
        script = sys.argv[0]
        params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
        
        logger = get_logger()
        logger.log_info("🔄 Versuche Administrator-Rechte anzufordern")
        
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
        sys.exit()
    except Exception as e:
        logger = get_logger()
        logger.log_error("Fehler beim Anfordern von Admin-Rechten", exc_info=e)

def find_gta_path():
    logger = get_logger()
    logger.log_debug("Starte GTA Pfad-Suche")
    logger.log_info("🔍 Suche GTA V Installation...")
    
    possible = [
        r"C:\Program Files\Rockstar Games\Grand Theft Auto V",
        r"C:\Program Files (x86)\Rockstar Games\Grand Theft Auto V",
        r"D:\Program Files\Rockstar Games\Grand Theft Auto V",
        r"D:\Program Files (x86)\Rockstar Games\Grand Theft Auto V",        
        os.path.expandvars(r"%ProgramFiles(x86)%\Steam\steamapps\common\Grand Theft Auto V"),
        os.path.expandvars(r"%ProgramFiles%\Epic Games\GTAV")
    ]
    
    logger.log_debug(f"Prüfe {len(possible)} mögliche Pfade")
    
    for i, p in enumerate(possible):
        logger.log_debug(f"Prüfe Pfad {i+1}: {p}")
        if os.path.isfile(os.path.join(p, "GTA5.exe")):
            logger.log_success(f"GTA Pfad gefunden: {p}")
            return p
    
    logger.log_debug("Kein GTA Pfad in Standard-Pfaden gefunden, prüfe Registry...")
    
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Valve\\Steam") as key:
            steam_path, _ = winreg.QueryValueEx(key, "SteamPath")
            steam_gta = os.path.join(steam_path, r"steamapps\\common\\Grand Theft Auto V")
            logger.log_debug(f"Steam Pfad aus Registry: {steam_gta}")
            if os.path.isfile(os.path.join(steam_gta, "GTA5.exe")):
                logger.log_success(f"GTA Pfad über Steam Registry gefunden: {steam_gta}")
                return steam_gta
    except Exception as e:
        logger.log_warning(f"Steam Registry Zugriff fehlgeschlagen: {e}")
    
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Rockstar Games\\Launcher\\Installs\\GTAV") as key:
            install_path, _ = winreg.QueryValueEx(key, "InstallFolder")
            logger.log_debug(f"Rockstar Launcher Pfad aus Registry: {install_path}")
            if os.path.isfile(os.path.join(install_path, "GTA5.exe")):
                logger.log_success(f"GTA Pfad über Rockstar Launcher gefunden: {install_path}")
                return install_path
    except Exception as e:
        logger.log_warning(f"Rockstar Launcher Registry Zugriff fehlgeschlagen: {e}")
    
    logger.log_warning("❌ GTA Pfad konnte nicht automatisch gefunden werden")
    return None

def list_microphones():
    logger = get_logger()
    mics = []
    try:
        logger.log_info("🔊 Starte Mikrofon-Erkennung")
        logger.log_debug("Initialisiere PyAudio")
        pa = pyaudio.PyAudio()
        device_count = pa.get_device_count()
        logger.log_debug(f"System hat {device_count} Audio-Geräte")
        
        for i in range(device_count):
            info = pa.get_device_info_by_index(i)
            logger.log_debug(f"Prüfe Gerät {i}: {info['name']} - Input Channels: {info.get('maxInputChannels', 0)}")
            if info.get('maxInputChannels', 0) > 0:
                mics.append(info['name'])
                logger.log_debug(f"✅ Mikrofon gefunden: {info['name']}")
        
        pa.terminate()
        logger.log_success(f"{len(mics)} Mikrofone gefunden")
    except Exception as e:
        logger.log_error("Fehler bei der Mikrofon-Erkennung", exc_info=e)
    return mics

def get_default_microphone():
    logger = get_logger()
    logger.log_debug("Starte Suche nach Standard-Mikrofon")
    mics = list_microphones()
    
    for mic in mics:
        if "micro" in mic.lower():
            logger.log_success(f"Standard-Mikrofon ausgewählt: {mic}")
            return mic
    
    default_mic = mics[0] if mics else None
    if default_mic:
        logger.log_info(f"Erstes verfügbares Mikrofon ausgewählt: {default_mic}")
    else:
        logger.log_warning("❌ Keine Mikrofone verfügbar")
    
    return default_mic

def set_registry(key_name, value):
    logger = get_logger()
    try:
        logger.log_debug(f"Versuche Registry-Eintrag zu setzen: {key_name} = {value}")
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\RAGE-MP") as key:
            winreg.SetValueEx(key, key_name, 0, winreg.REG_SZ, value)
        logger.log_success(f"Registry Eintrag gesetzt: {key_name} = {value}")
        return True
    except Exception as e:
        logger.log_error(f"Fehler beim Setzen des Registry Eintrags {key_name}", exc_info=e)
        return False

def fix_connection_issue(logger_callback=print):
    logger = get_logger()
    logger.log_debug("Connection Fix Funktion aufgerufen")
    logger.log_info("🔧 Starte Connection Fix...")
    
    try:
        config_path = r"C:\GrandRP Launcher\RAGEMP\config.xml"
        logger.log_debug(f"Ziel-Pfad: {config_path}")
        
        if not os.path.isfile(config_path):
            logger.log_warning(f"Primärer Config-Pfad nicht gefunden: {config_path}")
            logger_callback(f"❌ RAGEMP config.xml nicht gefunden: {config_path}")
            
            # Alternative Pfade prüfen
            alternative_paths = [
                os.path.expanduser(r"~\Documents\Rockstar Games\GTA V\RAGEMP\config.xml"),
                os.path.expanduser(r"~\Documents\RAGEMP\config.xml"),
                os.path.join(os.getcwd(), "RAGEMP", "config.xml")
            ]
            
            logger.log_debug(f"Prüfe {len(alternative_paths)} alternative Pfade")
            
            for i, alt_path in enumerate(alternative_paths):
                logger.log_debug(f"Prüfe alternativen Pfad {i+1}: {alt_path}")
                if os.path.isfile(alt_path):
                    config_path = alt_path
                    logger.log_success(f"Config.xml in alternativem Pfad gefunden: {alt_path}")
                    logger_callback(f"✅ Config.xml gefunden in: {alt_path}")
                    break
            else:
                logger.log_error("❌ Config.xml in keinem bekannten Pfad gefunden")
                logger_callback("❌ Config.xml in keinem bekannten Pfad gefunden")
                return False

        logger.log_info(f"📁 Config-Pfad: {config_path}")
        logger_callback(f"📁 Config-Pfad: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.log_debug("Config.xml erfolgreich gelesen")

        # Prüfe verschiedene Channel-Konfigurationen
        if '<channel>prerelease</channel>' in content:
            logger.log_info("🔄 Ändere Channel von 'prerelease' zu '11_test_1907'")
            content = content.replace('<channel>prerelease</channel>', '<channel>11_test_1907</channel>')
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.log_success("✅ Connection Fix erfolgreich - Channel geändert")
            logger_callback("✅ Connection Issue behoben - Channel geändert")
            return True
            
        elif '<channel>11_test_1907</channel>' in content:
            logger.log_success("✅ Channel ist bereits korrekt konfiguriert")
            logger_callback("✅ Channel ist bereits korrekt auf '11_test_1907' gesetzt")
            return True
            
        elif '<channel>' in content:
            start = content.find('<channel>') + 9
            end = content.find('</channel>')
            current_channel = content[start:end]
            logger.log_info(f"🔍 Aktueller Channel: '{current_channel}'")
            logger_callback(f"ℹ️ Aktueller Channel: '{current_channel}'")
            
            if current_channel != '11_test_1907':
                logger.log_info(f"🔄 Ändere Channel von '{current_channel}' zu '11_test_1907'")
                content = content.replace(f'<channel>{current_channel}</channel>', '<channel>11_test_1907</channel>')
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.log_success("✅ Channel erfolgreich geändert")
                logger_callback(f"✅ Channel von '{current_channel}' zu '11_test_1907' geändert")
                return True
            else:
                logger.log_success("✅ Channel ist bereits korrekt")
                logger_callback("✅ Channel ist bereits korrekt")
                return True
        else:
            logger.log_warning("⚠️ Channel-Tag nicht in erwarteter Form gefunden")
            logger_callback("❌ Channel-Tag nicht in config.xml gefunden")
            return False

    except PermissionError as e:
        logger.log_error("❌ Keine Schreibberechtigung für Config-Datei")
        logger_callback("❌ Keine Schreibberechtigung")
        logger_callback("💡 Führen Sie das Programm als Administrator aus")
        return False
    except Exception as e:
        logger.log_error("❌ Fehler beim Connection Fix", exc_info=e)
        logger_callback(f"❌ Fehler beim Connection Fix: {e}")
        return False

def delete_localprefs(logger_callback=print):
    logger = get_logger()
    logger.log_debug("LocalPrefs Lösch-Funktion aufgerufen")
    logger.log_info("🗑️ Starte LocalPrefs Bereinigung...")
    
    try:
        documents_path = os.path.expanduser("~/Documents")
        localprefs_path = os.path.join(
            documents_path, 
            "Rockstar Games", 
            "Social Club", 
            "Launcher", 
            "Renderer", 
            "LocalPrefs.json"
        )
        
        logger.log_info(f"🔍 Suche LocalPrefs.json in: {localprefs_path}")
        logger_callback(f"🔍 Suche LocalPrefs.json in: {localprefs_path}")
        
        if os.path.isfile(localprefs_path):
            # Sicherung erstellen bevor gelöscht wird
            backup_path = localprefs_path + ".backup"
            logger.log_debug(f"Erstelle Sicherung: {backup_path}")
            shutil.copy2(localprefs_path, backup_path)
            os.remove(localprefs_path)
            logger.log_success("✅ LocalPrefs.json erfolgreich gelöscht und gesichert")
            logger_callback("✅ LocalPrefs.json erfolgreich gelöscht")
            logger_callback(f"📁 Sicherung erstellt: {backup_path}")
            return True
        else:
            logger.log_info("ℹ️ LocalPrefs.json nicht gefunden - bereits gelöscht oder nicht vorhanden")
            logger_callback("ℹ️ LocalPrefs.json nicht gefunden - bereits gelöscht oder nicht vorhanden")
            
            # Prüfe alternative Pfade
            alternative_paths = [
                os.path.join(documents_path, "Rockstar Games", "GTA V", "LocalPrefs.json"),
                os.path.join(documents_path, "LocalPrefs.json"),
            ]
            
            logger.log_debug(f"Prüfe {len(alternative_paths)} alternative Pfade")
            
            for alt_path in alternative_paths:
                if os.path.isfile(alt_path):
                    logger.log_info(f"📁 Alternative LocalPrefs.json gefunden: {alt_path}")
                    logger_callback(f"📁 Alternative LocalPrefs.json gefunden: {alt_path}")
                    backup_path = alt_path + ".backup"
                    shutil.copy2(alt_path, backup_path)
                    os.remove(alt_path)
                    logger.log_success(f"✅ Alternative LocalPrefs.json gelöscht: {alt_path}")
                    logger_callback(f"✅ Alternative LocalPrefs.json gelöscht: {alt_path}")
                    logger_callback(f"📁 Sicherung erstellt: {backup_path}")
                    return True
            
            logger.log_success("✅ Status: Keine LocalPrefs.json Dateien gefunden - System ist bereinigt")
            logger_callback("✅ Status: Keine LocalPrefs.json Dateien gefunden - System ist bereinigt")
            return True  # Keine Datei gefunden ist auch ein Erfolg
            
    except Exception as e:
        logger.log_error("❌ Fehler beim Löschen von LocalPrefs", exc_info=e)
        logger_callback(f"❌ Fehler beim Löschen: {e}")
        return False

def fix_windows_compatibility(logger_callback=print):
    logger = get_logger()
    logger.log_debug("Windows Kompatibilitäts-Fix Funktion aufgerufen")
    
    try:
        if not is_admin():
            error_msg = "❌ Admin-Rechte benötigt für Windows Kompatibilitäts-Fix"
            logger.log_error(error_msg)
            logger_callback(error_msg)
            return False

        logger.log_info("⚙️ Starte Windows Kompatibilitäts-Fix")
        logger_callback("⚙️ Starte Windows Kompatibilitäts-Fix...")

        ps_script = '''
# Admin check
If (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "Admin rights required"
    exit 1
}

$timestamp = (Get-Date).ToString("yyyyMMdd_HHmmss")
$backupDir = "C:\\Temp\\AppCompat_Backup_$timestamp"
New-Item -Path $backupDir -ItemType Directory -Force | Out-Null
Write-Host "Backup-Verzeichnis erstellt: $backupDir"

function Export-RegistryKeyIfExists {
    param($hivePath, $outfile)
    try {
        reg export $hivePath $outfile /y > $null 2>&1
        if ($LASTEXITCODE -eq 0) { Write-Host "Backup: $outfile" }
    } catch {
        Write-Warning "Backup failed: $hivePath"
    }
}

$regPathsToBackup = @(
    "HKCU\\Software\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Layers",
    "HKCU\\Software\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Compatibility Assistant\\Store",
    "HKCU\\Software\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Compatibility Assistant\\Persisted",
    "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Layers",
    "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Compatibility Assistant",
    "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\AppCompat",
    "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\AppCompat"
)

Write-Host "Erstelle Registry Backups..."
foreach ($r in $regPathsToBackup) {
    $out = Join-Path $backupDir ( ($r -replace '[\\\\:]','_') + ".reg" )
    Export-RegistryKeyIfExists -hivePath $r -outfile $out
}

function Remove-RegistryPathSafe {
    param($path)
    try {
        if (Test-Path $path) {
            Remove-Item -Path $path -Recurse -Force -ErrorAction Stop
            Write-Host "Entfernt: $path"
        } else {
            Write-Host "Nicht vorhanden: $path"
        }
    } catch {
        Write-Warning "Fehler beim Entfernen: $path - $_"
    }
}

Write-Host "Bereinige Registry-Einträge..."
$pathsToRemove = @(
    "HKCU:\\Software\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Layers",
    "HKCU:\\Software\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Compatibility Assistant\\Store",
    "HKCU:\\Software\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Compatibility Assistant\\Persisted",
    "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Layers",
    "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Compatibility Assistant"
)

foreach ($p in $pathsToRemove) { Remove-RegistryPathSafe -path $p }

Write-Host "Setze PCA Deaktivierung..."
try {
    $policyPath = "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\AppCompat"
    if (-not (Test-Path $policyPath)) { 
        New-Item -Path $policyPath -Force | Out-Null
        Write-Host "Policy-Pfad erstellt: $policyPath"
    }
    New-ItemProperty -Path $policyPath -Name "DisablePCA" -PropertyType DWord -Value 1 -Force | Out-Null
    Write-Host "Policy DisablePCA gesetzt: $policyPath\\DisablePCA = 1"

    $winPath = "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\AppCompat"
    if (-not (Test-Path $winPath)) { 
        New-Item -Path $winPath -Force | Out-Null
        Write-Host "Registry-Pfad erstellt: $winPath"
    }
    New-ItemProperty -Path $winPath -Name "DisablePCA" -PropertyType DWord -Value 1 -Force | Out-Null
    Write-Host "Registry DisablePCA gesetzt: $winPath\\DisablePCA = 1"
} catch {
    Write-Warning "Fehler beim Setzen von DisablePCA: $_"
}

Write-Host "Stoppe PCA Service..."
try {
    $svcName = "PcaSvc"
    if (Get-Service -Name $svcName -ErrorAction SilentlyContinue) {
        Stop-Service -Name $svcName -Force -ErrorAction SilentlyContinue
        Set-Service -Name $svcName -StartupType Disabled
        Write-Host "Service gestoppt und deaktiviert: $svcName"
    } else {
        Write-Host "Service $svcName nicht gefunden."
    }
} catch {
    Write-Warning "Fehler beim Service-Handling: $_"
}

Write-Host "✅ Kompatibilitäts-Fix abgeschlossen!"
Write-Host "Backups befinden sich in: $backupDir"
Write-Host "🔄 Ein Neustart wird empfohlen"
'''

        logger.log_debug("Erstelle temporäres PowerShell Script")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False) as f:
            f.write(ps_script)
            temp_script = f.name

        logger.log_info("🔧 Führe PowerShell Script aus...")
        logger_callback("🔧 Führe PowerShell Script aus...")
        
        result = subprocess.run([
            'powershell', '-ExecutionPolicy', 'Bypass', '-File', temp_script
        ], capture_output=True, text=True, timeout=120)

        os.unlink(temp_script)
        logger.log_debug("Temporäres Script gelöscht")

        if result.returncode == 0:
            logger.log_success("✅ Windows Kompatibilitäts-Fix erfolgreich durchgeführt")
            # PowerShell Ausgabe an UI weiterleiten
            for line in result.stdout.split('\n'):
                if line.strip():
                    logger.log_debug(f"PS Output: {line}")
                    logger_callback(f"PS: {line}")
            logger_callback("✅ Windows Kompatibilitäts-Fix erfolgreich durchgeführt")
            logger_callback("🔄 Neustart des Systems wird empfohlen")
            return True
        else:
            error_msg = f"❌ Fehler bei Kompatibilitäts-Fix: {result.stderr}"
            logger.log_error(error_msg)
            logger_callback(error_msg)
            return False

    except subprocess.TimeoutExpired:
        error_msg = "❌ Kompatibilitäts-Fix timeout"
        logger.log_error(error_msg)
        logger_callback(error_msg)
        return False
    except Exception as e:
        error_msg = f"❌ Fehler bei Kompatibilitäts-Fix: {e}"
        logger.log_error(error_msg, exc_info=e)
        logger_callback(error_msg)
        return False

def patch_by_relative_path(gta_path, patch_path, logger_callback=print):
    logger = get_logger()
    patched_files = []

    logger.log_info(f"🚀 Starte Patch-Prozess: {patch_path} -> {gta_path}")
    logger_callback(f"🚀 Starte Patch-Prozess: {os.path.basename(patch_path)} -> {os.path.basename(gta_path)}")

    if not os.path.isdir(gta_path):
        error_msg = f"❌ GTA-Pfad ungültig: {gta_path}"
        logger.log_error(error_msg)
        raise FileNotFoundError(error_msg)
        
    if not os.path.isdir(patch_path):
        error_msg = f"❌ Patch-Pfad ungültig: {patch_path}"
        logger.log_error(error_msg)
        raise FileNotFoundError(error_msg)

    logger.log_debug(f"GTA-Pfad validiert: {gta_path}")
    logger.log_debug(f"Patch-Pfad validiert: {patch_path}")

    try:
        file_count = 0
        for dirpath, _, filenames in os.walk(patch_path):
            file_count += len(filenames)
        
        logger.log_info(f"🔍 Gefunden {file_count} Dateien zum Patchen")
        logger_callback(f"🔍 Gefunden {file_count} Dateien zum Patchen")

        processed_files = 0
        for dirpath, _, filenames in os.walk(patch_path):
            for filename in filenames:
                processed_files += 1
                patch_file = os.path.join(dirpath, filename)
                relative_path = os.path.relpath(patch_file, patch_path)
                gta_target = os.path.join(gta_path, relative_path)

                logger.log_debug(f"Verarbeite Datei {processed_files}/{file_count}: {filename}")

                if os.path.isfile(gta_target):
                    target_path = gta_target
                    logger.log_debug(f"Standardpfad gefunden: {target_path}")
                else:
                    found = None
                    logger.log_debug(f"Suche alternative Pfade für: {filename}")
                    for g_dir, _, g_files in os.walk(gta_path):
                        for g_file in g_files:
                            if g_file.lower() == filename.lower():
                                found = os.path.join(g_dir, g_file)
                                break
                        if found:
                            break

                    if found:
                        logger.log_warning(f"⚠️ Standardpfad nicht gefunden für {filename}, ersetze: {found}")
                        logger_callback(f"⚠️ Standardpfad nicht gefunden für {filename}, ersetze: {os.path.basename(found)}")
                        target_path = found
                    else:
                        logger.log_warning(f"⚠️ Datei nicht vorhanden im GTA-Verzeichnis: {relative_path}")
                        logger_callback(f"⚠️ Datei nicht vorhanden: {relative_path}")
                        continue

                try:
                    # Backup erstellen
                    backup_file = target_path + ".bak"
                    os.makedirs(os.path.dirname(backup_file), exist_ok=True)
                    shutil.copy2(target_path, backup_file)
                    logger.log_info(f"📁 Backup erstellt: {os.path.basename(backup_file)}")
                    logger_callback(f"📁 Backup erstellt: {os.path.basename(backup_file)}")

                    # Datei patchen
                    shutil.copy2(patch_file, target_path)
                    patched_rel_path = os.path.relpath(target_path, gta_path)
                    logger.log_success(f"✅ Datei gepatcht: {patched_rel_path}")
                    logger_callback(f"✅ Datei gepatcht: {patched_rel_path}")
                    patched_files.append(patched_rel_path)

                except Exception as e:
                    error_msg = f"❌ Fehler beim Patchen von {relative_path}: {e}"
                    logger.log_error(error_msg, exc_info=e)
                    logger_callback(f"❌ {error_msg}")

        if not patched_files:
            error_msg = "❌ Keine gültigen Dateien zum Patchen gefunden."
            logger.log_error(error_msg)
            raise RuntimeError(error_msg)

        logger.log_success(f"🎉 Patch abgeschlossen: {len(patched_files)} Dateien gepatcht")
        logger_callback(f"🎉 Patch abgeschlossen: {len(patched_files)} Dateien gepatcht")
        return patched_files

    except Exception as e:
        logger.log_error("❌ Fehler während des Patch-Prozesses", exc_info=e)
        raise

def restore_backups(gta_path, logger_callback=print):
    logger = get_logger()
    logger.log_info(f"🔄 Starte Backup-Wiederherstellung für: {gta_path}")
    logger_callback(f"🔄 Starte Backup-Wiederherstellung für: {os.path.basename(gta_path)}")

    if not os.path.isdir(gta_path):
        error_msg = f"❌ GTA-Pfad ungültig: {gta_path}"
        logger.log_error(error_msg)
        raise FileNotFoundError(error_msg)

    logger.log_debug(f"GTA-Pfad validiert: {gta_path}")

    restored_files = []
    backup_count = 0

    try:
        # Zuerst Backup-Dateien zählen
        for dirpath, _, filenames in os.walk(gta_path):
            for file in filenames:
                if file.endswith(".bak"):
                    backup_count += 1

        logger.log_info(f"🔍 Gefunden {backup_count} Backup-Dateien")
        logger_callback(f"🔍 Gefunden {backup_count} Backup-Dateien")

        processed_backups = 0
        for dirpath, _, filenames in os.walk(gta_path):
            for file in filenames:
                if file.endswith(".bak"):
                    processed_backups += 1
                    bak_file = os.path.join(dirpath, file)
                    original_file = os.path.join(dirpath, file[:-4])  # ohne ".bak"

                    logger.log_debug(f"Verarbeite Backup {processed_backups}/{backup_count}: {file}")

                    try:
                        shutil.copy2(bak_file, original_file)
                        os.remove(bak_file)
                        restored_rel_path = os.path.relpath(original_file, gta_path)
                        logger.log_success(f"✅ Backup zurückgespielt: {restored_rel_path}")
                        logger_callback(f"✅ Backup zurückgespielt: {restored_rel_path}")
                        restored_files.append(restored_rel_path)
                    except Exception as e:
                        error_msg = f"❌ Fehler beim Zurückspielen von {bak_file}: {e}"
                        logger.log_error(error_msg, exc_info=e)
                        logger_callback(f"❌ {error_msg}")

        if not restored_files:
            logger.log_info("ℹ️ Keine Backup-Dateien zum Zurückspielen gefunden")
            logger_callback("ℹ️ Keine Backup-Dateien zum Zurückspielen gefunden")
        else:
            logger.log_success(f"🎉 Backup-Wiederherstellung abgeschlossen: {len(restored_files)} Dateien wiederhergestellt")
            logger_callback(f"🎉 Backup-Wiederherstellung abgeschlossen: {len(restored_files)} Dateien wiederhergestellt")
            
        return restored_files

    except Exception as e:
        logger.log_error("❌ Fehler während der Backup-Wiederherstellung", exc_info=e)
        raise