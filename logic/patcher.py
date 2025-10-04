import os
import shutil
import logging
import time

def patch_by_relative_path(gta_path, patch_path, logger=print):
    if not os.path.isdir(gta_path):
        raise FileNotFoundError(f"GTA-Pfad ungültig: {gta_path}")
    if not os.path.isdir(patch_path):
        raise FileNotFoundError(f"Patch-Pfad ungültig: {patch_path}")

    patched_files = []

    for dirpath, _, filenames in os.walk(patch_path):
        for filename in filenames:
            patch_file = os.path.join(dirpath, filename)

            # relativer Pfad ab Patch-Wurzel
            relative_path = os.path.relpath(patch_file, patch_path)

            # Zielpfad im GTA-Verzeichnis
            gta_file = os.path.join(gta_path, relative_path)

            if not os.path.isfile(gta_file):
                logger(f"[WARN] Datei existiert nicht in GTA: {relative_path}")
                continue

            try:
                # Backup erstellen
                backup_file = gta_file + ".bak"
                shutil.copy2(gta_file, backup_file)
                logger(f"[INFO] Backup erstellt: {backup_file}")

                # Sicherstellen, dass das Backup abgeschlossen ist
                time.sleep(0.3)

                # Datei patchen
                shutil.copy2(patch_file, gta_file)
                logger(f"[INFO] Datei gepatcht: {relative_path}")
                patched_files.append(relative_path)

            except Exception as e:
                logger(f"[ERROR] Fehler beim Patchen von {relative_path}: {e}")

    if not patched_files:
        raise RuntimeError("Keine Dateien wurden gepatcht.")

    return patched_files
