# Homeco Fernwartung – eigener RustDesk-Client

Ergebnis: `Homeco-Fernwartung.exe` zum Download für Kunden. Das Programm
startet ohne Installation, zeigt im dunklen Homeco-Design das Logo, die ID
(groß in Homeco-Orange) und das Einmalpasswort, und verbindet sich nur mit dem
eigenen Homeco-Server. Kunden können damit selbst keine Verbindung aufbauen.

Kosten: 0 € für die Software. Nötig sind ein Server (vorhandener VPS reicht)
und ein kostenloses GitHub-Konto. Gebaut wird auf GitHub, nicht auf dem eigenen PC.

---

## 1. Server einrichten (einmalig, ca. 15 Min.)

1. DNS: A-Record `remote.homeco-computersysteme.de` → IP des VPS.
2. Auf dem VPS (Docker muss installiert sein):
   ```bash
   mkdir -p /opt/rustdesk && cd /opt/rustdesk
   # docker-compose.yml aus dem Ordner server/ hierher kopieren
   docker compose up -d
   cat data/id_ed25519.pub      # → das ist der Schlüssel (HOMECO_KEY)
   ```
3. Firewall (auch in CloudPanel / beim Hoster): **TCP 21115–21117** und **UDP 21116** öffnen.

## 2. RustDesk auf GitHub forken (einmalig)

1. Auf github.com einloggen → https://github.com/rustdesk/rustdesk → **Fork**.
2. Im Fork: **Settings → Secrets and variables → Actions → New repository secret**
   - `HOMECO_SERVER` = `remote.homeco-computersysteme.de`
   - `HOMECO_KEY` = Inhalt von `id_ed25519.pub`
3. Im Fork auf den Tag **1.5.0** wechseln und daraus einen Branch `homeco` erstellen
   (Branch-Auswahl → Tags → 1.5.0 → „Create branch“). Auf diese Version ist das Branding abgestimmt.

## 3. Branding-Dateien hochladen

Im Fork, Branch `homeco` → **Add file → Upload files**, diese Ordner hineinziehen:

| Aus diesem Ordner           | Ziel im Fork                               |
|-----------------------------|--------------------------------------------|
| `homeco/` (komplett)        | `homeco/`                                  |
| `.github/workflows/homeco-build.yml` | `.github/workflows/homeco-build.yml` |

Falls der Browser den Ordner `.github` beim Hochladen nicht mitnimmt:
**Add file → Create new file**, als Namen `.github/workflows/homeco-build.yml`
eingeben und den Inhalt der Datei hineinkopieren.

## 4. Bauen

Fork → **Actions** (beim ersten Mal „Enable workflows“ bestätigen) →
**Homeco Fernwartung bauen** → **Run workflow** → Branch `homeco`.

Dauer beim ersten Mal ca. 60–90 Minuten, danach schneller (Cache).
Danach liegt die Exe unter **Releases**. Dauerhafter Download-Link für die Website:

```
https://github.com/<DEIN-KONTO>/rustdesk/releases/latest/download/Homeco-Fernwartung.exe
```

Bricht der Schritt „Homeco-Branding anwenden“ ab, hat sich der RustDesk-Code
geändert (nur bei anderen Versionen als 1.5.0). Die Meldung nennt die Datei.

## 5. Verbinden als Techniker

Normales RustDesk (oder ein zweiter Build ohne `conn-type`) installieren →
Einstellungen → Netzwerk → ID-Server `remote.homeco-computersysteme.de`,
Key = `HOMECO_KEY` eintragen. Dann ID + Passwort vom Kunden eingeben.

---

## Was das Branding ändert (`homeco/branding.py`)

- Name `Homeco-Fernwartung` (Fenster, Exe, Datei-Eigenschaften, Ordner in %APPDATA%)
- Server + Schlüssel fest eingebaut (aus den GitHub-Secrets)
- Nur eingehende Verbindungen, kein „Installieren“-Hinweis
- Dunkles Design in Homeco-Farben: Hintergrund `#070B14`, Flächen `#0E1524`, Orange `#FF8000`
- Homeco-Logo oben, HE-Icon für Taskleiste, Tray und Exe
- Zeile „Homeco Fernwartung · basiert auf RustDesk“ mit Link zur Homeco-Website

Anpassen (Name, Farben, Texte): oben in `homeco/branding.py` unter „Einstellungen“.

## Pflichten und Hinweise

- **Lizenz AGPL-3.0:** Der Quellcode der geänderten Version muss für Nutzer
  erreichbar sein. Der öffentliche GitHub-Fork erfüllt das. Auf der Download-Seite
  einen Link „Quellcode“ zum Fork setzen.
- **Markenname:** „RustDesk“ nicht als eigenen Produktnamen verwenden (ist erfüllt).
- **Windows SmartScreen:** Unsignierte Exe → Warnung „Der Computer wurde durch
  Windows geschützt“. Kunden müssen auf „Weitere Informationen → Trotzdem ausführen“
  klicken. Abhilfe später mit einem Code-Signing-Zertifikat.
- **Datenschutz:** Fernwartung in der Datenschutzerklärung erwähnen. Der Server
  steht bei Homeco, es laufen keine Daten über fremde Server.
