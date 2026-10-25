"""
Homeco-Branding für RustDesk (getestet gegen RustDesk 1.5.0).

Wird im GitHub-Workflow nach dem Auschecken ausgeführt und ändert den
RustDesk-Quellcode so, dass ein „Homeco Fernwartung“-Client entsteht:
eigener Name, eigener Server, Homeco-Farben und -Logo, nur eingehende
Verbindungen (Kunde zeigt ID + Passwort, kann selbst nicht verbinden).

Server und Schlüssel kommen aus den GitHub-Secrets HOMECO_SERVER und
HOMECO_KEY, damit sie nicht im öffentlichen Repository stehen müssen.

Jede Änderung prüft, dass die gesuchte Stelle genau so existiert. Hat
RustDesk den Code in einer neuen Version umgebaut, bricht das Skript mit
einer klaren Meldung ab, statt still einen halb gebrandeten Client zu bauen.
"""

import os
import re
import shutil
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Einstellungen
# ---------------------------------------------------------------------------
# Nur Buchstaben, Ziffern und Bindestrich (Vorgabe von RustDesk). Bestimmt
# auch den Exe-Namen, den Ordner in %APPDATA% und den Fenstertitel.
APP_NAME = "Homeco-Fernwartung"
COMPANY = "HomeCo Computersysteme"
WEBSITE = "https://www.homeco-computersysteme.de"

# Homeco-Farben (aus dem Logo)
ORANGE = "FF8000"        # Markenorange aus dem Logo
ORANGE_LIGHT = "FF9A3D"  # helleres Orange für die ID (besser lesbar auf Dunkel)
INK = "070B14"         # Fensterhintergrund (wie Website --ink)
INK_2 = "0E1524"       # Flächen, Eingabefelder (--ink-2)
INK_3 = "18213A"       # Hover (--ink-3)

POWERED_DE = "Homeco Fernwartung · basiert auf RustDesk"
POWERED_EN = "Homeco Remote Support · powered by RustDesk"

ROOT = Path(__file__).resolve().parent.parent
ASSETS = Path(__file__).resolve().parent / "assets"


def fail(msg: str) -> None:
    print(f"::error::Branding fehlgeschlagen: {msg}")
    sys.exit(1)


def patch(rel: str, old: str, new: str, count: int = 1, regex: bool = False) -> None:
    """Ersetzt old durch new; count = erwartete Anzahl Treffer (0 = beliebig viele, mind. 1)."""
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    hits = len(re.findall(old, text)) if regex else text.count(old)
    if hits == 0 or (count and hits != count):
        fail(f"{rel}: erwartet {count or '>=1'} Treffer für {old!r}, gefunden {hits}")
    text = re.sub(old, new, text) if regex else text.replace(old, new)
    path.write_text(text, encoding="utf-8")
    print(f"  ok  {rel}  ({hits}x)")


def patch_between(rel: str, start: str, end: str, old: str, new: str) -> None:
    """Wie patch(), aber nur im Abschnitt zwischen start und end."""
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    a = text.find(start)
    b = text.find(end, a)
    if a < 0 or b < 0:
        fail(f"{rel}: Abschnitt {start!r} … {end!r} nicht gefunden")
    section = text[a:b]
    hits = section.count(old)
    if hits == 0:
        fail(f"{rel}: {old!r} im Abschnitt nicht gefunden")
    text = text[:a] + section.replace(old, new) + text[b:]
    path.write_text(text, encoding="utf-8")
    print(f"  ok  {rel}  ({hits}x im Abschnitt)")


def rust_str(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def main() -> None:
    server = os.environ.get("HOMECO_SERVER", "").strip()
    key = os.environ.get("HOMECO_KEY", "").strip()
    if not server or not key:
        fail("GitHub-Secrets HOMECO_SERVER und HOMECO_KEY müssen gesetzt sein")
    if not re.fullmatch(r"[A-Za-z0-9-]+", APP_NAME):
        fail("APP_NAME darf nur Buchstaben, Ziffern und Bindestrich enthalten")

    print("Server und Name")
    cfg = "libs/hbb_common/src/config.rs"
    patch(cfg, r'pub const RENDEZVOUS_SERVERS: &\[&str\] = &\[[^\]]*\];',
          f'pub const RENDEZVOUS_SERVERS: &[&str] = &["{rust_str(server)}"];', regex=True)
    patch(cfg, r'pub const RS_PUB_KEY: &str = "[^"]*";',
          f'pub const RS_PUB_KEY: &str = "{rust_str(key)}";', regex=True)
    patch(cfg, 'pub static ref APP_NAME: RwLock<String> = RwLock::new("RustDesk".to_owned());',
          f'pub static ref APP_NAME: RwLock<String> = RwLock::new("{APP_NAME}".to_owned());')

    print("Feste Einstellungen (ersetzt die signierte custom.txt der Pro-Version)")
    patch("src/common.rs", "pub fn load_custom_client() {\n",
          "pub fn load_custom_client() {\n    homeco_settings();\n")
    patch("src/common.rs", "fn read_custom_client_advanced_settings(",
          '''fn homeco_settings() {
    let mut hard = config::HARD_SETTINGS.write().unwrap();
    // Nur eingehende Verbindungen: Kunde zeigt ID + Passwort an
    hard.insert("conn-type".to_owned(), "incoming".to_owned());
    // Kein „Installieren“-Hinweis: Programm läuft direkt nach dem Download
    hard.insert("disable-installation".to_owned(), "Y".to_owned());
    drop(hard);
    // Dunkles Design wie die Homeco-Website, unabhängig von Windows-Einstellung
    config::OVERWRITE_LOCAL_SETTINGS
        .write()
        .unwrap()
        .insert("theme".to_owned(), "dark".to_owned());
}

fn read_custom_client_advanced_settings(''')

    print("Farben")
    dart = "flutter/lib/common.dart"
    patch(dart, "static const Color accent = Color(0xFF0071FF);",
          f"static const Color accent = Color(0xFF{ORANGE});")
    patch(dart, "static const Color accent50 = Color(0x770071FF);",
          f"static const Color accent50 = Color(0x77{ORANGE});")
    patch(dart, "static const Color accent80 = Color(0xAA0071FF);",
          f"static const Color accent80 = Color(0xAA{ORANGE});")
    patch(dart, "static const Color button = Color(0xFF2C8CFF);",
          f"static const Color button = Color(0xFF{ORANGE});")
    patch(dart, "static const Color idColor = Color(0xFF00B6F0);",
          f"static const Color idColor = Color(0xFF{ORANGE_LIGHT});")
    patch(dart, "Color(0xFF18191E)", f"Color(0xFF{INK})", count=0)
    patch(dart, "Color(0xFF24252B)", f"Color(0xFF{INK_2})", count=0)
    patch(dart, "hoverColor: Color.fromARGB(255, 45, 46, 53),", f"hoverColor: Color(0xFF{INK_3}),")
    patch_between(dart, "class MyTheme {", "static ThemeMode getThemeModePreference",
                  "primary: Colors.blue", "primary: accent")

    print("ID groß in Homeco-Orange (wie im Vorbild)")
    patch("flutter/lib/desktop/pages/desktop_home_page.dart",
          "                        style: TextStyle(\n                          fontSize: 22,\n                        ),",
          "                        style: TextStyle(\n                          fontSize: 24,\n"
          "                          fontWeight: FontWeight.w600,\n"
          "                          color: MyTheme.idColor,\n                        ),")

    print("Hinweis „Unterstützt von …“")
    patch(dart, "launchUrl(Uri.parse('https://rustdesk.com'));", f"launchUrl(Uri.parse('{WEBSITE}'));")
    patch("src/lang/de.rs", r'\("powered_by_me", "[^"]*"\)', f'("powered_by_me", "{POWERED_DE}")', regex=True)
    patch("src/lang/en.rs", r'\("powered_by_me", "[^"]*"\)', f'("powered_by_me", "{POWERED_EN}")', regex=True)

    print("Datei-Eigenschaften der Exe")
    for rel in ("Cargo.toml", "libs/portable/Cargo.toml"):
        patch(rel, r'LegalCopyright = "[^"]*"', f'LegalCopyright = "Copyright © {COMPANY}. Basiert auf RustDesk (AGPL-3.0)."', regex=True)
        patch(rel, 'ProductName = "RustDesk"', f'ProductName = "{APP_NAME}"')
        patch(rel, 'FileDescription = "RustDesk Remote Desktop"', 'FileDescription = "Homeco Fernwartung"')
        patch(rel, 'OriginalFilename = "rustdesk.exe"', f'OriginalFilename = "{APP_NAME}.exe"')
    rc = "flutter/windows/runner/Runner.rc"
    patch(rc, 'VALUE "CompanyName", "Purslane Tech Pte. Ltd."', f'VALUE "CompanyName", "{COMPANY}"')
    patch(rc, 'VALUE "FileDescription", "RustDesk Remote Desktop"', 'VALUE "FileDescription", "Homeco Fernwartung"')
    patch(rc, r'VALUE "LegalCopyright", "[^"]*"', f'VALUE "LegalCopyright", "Copyright © {COMPANY}. Basiert auf RustDesk (AGPL-3.0)."', regex=True)
    patch(rc, 'VALUE "OriginalFilename", "rustdesk.exe"', f'VALUE "OriginalFilename", "{APP_NAME}.exe"')
    patch(rc, 'VALUE "ProductName", "RustDesk"', f'VALUE "ProductName", "{APP_NAME}"')

    print("Logo und Icons")
    # loadLogo() zeigt assets/logo.png (max. 300x60), loadIcon() bevorzugt assets/icon.png
    shutil.copy(ASSETS / "logo.png", ROOT / "flutter/assets/logo.png")
    shutil.copy(ASSETS / "icon.png", ROOT / "flutter/assets/icon.png")
    from PIL import Image  # im Workflow per pip installiert

    icon = Image.open(ASSETS / "icon.png").convert("RGBA")
    ico_sizes = [(s, s) for s in (16, 24, 32, 48, 64, 128, 256)]
    for rel in ("res/icon.ico", "flutter/windows/runner/resources/app_icon.ico"):
        icon.save(ROOT / rel, sizes=ico_sizes)
    icon.save(ROOT / "res/tray-icon.ico", sizes=[(16, 16), (24, 24), (32, 32)])
    icon.save(ROOT / "res/icon.png")
    for name, size in (("32x32.png", 32), ("64x64.png", 64), ("128x128.png", 128), ("128x128@2x.png", 256)):
        icon.resize((size, size), Image.LANCZOS).save(ROOT / "res" / name)
    print("  ok  Icons erzeugt")

    print(f"Fertig: {APP_NAME} -> {server}")


if __name__ == "__main__":
    main()
