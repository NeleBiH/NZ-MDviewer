#!/bin/bash
#
# NZ-MDviewer Installer / Uninstaller
# ====================================
# Jednostavna instalacija i deinstalacija
#
# Korištenje:
#   chmod +x install_uninstall.sh
#   ./install_uninstall.sh
#
# CLI opcije:
#   ./install_uninstall.sh --install    (ili -i)
#   ./install_uninstall.sh --update     (ili -U)
#   ./install_uninstall.sh --force      (ili -f)
#   ./install_uninstall.sh --uninstall  (ili -u)
#   ./install_uninstall.sh --help       (ili -h)
#

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

# Čitaj verziju iz NZ-MDviewer/__init__.py
_get_source_version() {
    local init_file="$SCRIPT_DIR/NZ-MDviewer/__init__.py"
    if [ -f "$init_file" ]; then
        grep -oP 'VERSION\s*=\s*"\K[^"]+' "$init_file" | head -1
    fi
}

VERSION="$(_get_source_version)"
[ -z "$VERSION" ] && VERSION="unknown"

# Lokacije
INSTALL_DIR="$HOME/.local/share/nzmdviewer"
VENV_DIR="$INSTALL_DIR/venv"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
SETTINGS_FILE="$HOME/.local/share/nzmdviewer/settings.json"
BACKUP_DIR="/tmp/nzmdviewer_backup_$$"

# Boje
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ============================================
# HELP FUNKCIJA
# ============================================
show_help() {
    echo ""
    echo -e "${CYAN}NZ-MDviewer Installer v$VERSION${NC}"
    echo "================================"
    echo ""
    echo "OPIS:"
    echo "  Installer/deinstaller za NZ-MDviewer Markdown Viewer"
    echo ""
    echo "KORIŠTENJE:"
    echo "  $0 [OPCIJA]"
    echo ""
    echo "OPCIJE:"
    echo "  -i, --install      Instalira NZ-MDviewer"
    echo "  -U, --update       Ažurira na novu verziju (ako postoji)"
    echo "  -f, --force        Force reinstall (gazi staru verziju)"
    echo "  -u, --uninstall    Deinstalira NZ-MDviewer"
    echo "  -h, --help         Prikaže ovu pomoć"
    echo "  -v, --version      Prikaže verziju"
    echo ""
    echo "BEZ ARGUMENATA:"
    echo "  Pokreće interaktivni meni"
    echo ""
    echo "PRIMJERI:"
    echo "  $0 --install       # Direktna instalacija"
    echo "  $0 --update        # Ažuriranje na novu verziju"
    echo "  $0 --force         # Force reinstall (gazi staro)"
    echo "  $0 --uninstall     # Direktna deinstalacija"
    echo "  $0                 # Interaktivni meni"
    echo ""
}

show_version() {
    echo "NZ-MDviewer v$VERSION"
}

# Čitaj instaliranu verziju iz instaliranog __init__.py
_get_installed_version() {
    local init_file="$INSTALL_DIR/NZ-MDviewer/__init__.py"
    if [ -f "$init_file" ]; then
        grep -oP 'VERSION\s*=\s*"\K[^"]+' "$init_file" | head -1
    fi
}

# ============================================
# BACKUP / RESTORE POSTAVKI
# ============================================
do_backup_settings() {
    if [ -f "$SETTINGS_FILE" ]; then
        mkdir -p "$BACKUP_DIR"
        cp "$SETTINGS_FILE" "$BACKUP_DIR/settings.json"
        echo -e "  ${GREEN}✓${NC} Backup postavki: $BACKUP_DIR/settings.json"
        return 0
    fi
    return 1
}

do_restore_settings() {
    if [ -f "$BACKUP_DIR/settings.json" ]; then
        mkdir -p "$(dirname "$SETTINGS_FILE")"
        cp "$BACKUP_DIR/settings.json" "$SETTINGS_FILE"
        echo -e "  ${GREEN}✓${NC} Postavke vraćene iz backupa"
        rm -rf "$BACKUP_DIR"
        return 0
    fi
    return 1
}

# ============================================
# INSTALACIJA IKONA U HICOLOR THEME
# ============================================
do_install_icons() {
    local src="$INSTALL_DIR/NZ-MDviewer/icons"
    local dst="$HOME/.local/share/icons/hicolor"

    # PNG ikone po standardnim veličinama
    declare -A ICON_SIZES=(
        ["16x16"]="nzmdviewer_16.png"
        ["22x22"]="nzmdviewer_22.png"
        ["24x24"]="nzmdviewer_24.png"
        ["32x32"]="nzmdviewer_32.png"
        ["48x48"]="nzmdviewer_48.png"
        ["64x64"]="nzmdviewer_64.png"
        ["128x128"]="nzmdviewer_128.png"
        ["256x256"]="nzmdviewer_256.png"
        ["512x512"]="nzmdviewer_512.png"
    )

    for size in "${!ICON_SIZES[@]}"; do
        local src_file="$src/${ICON_SIZES[$size]}"
        if [ -f "$src_file" ]; then
            mkdir -p "$dst/$size/apps"
            cp "$src_file" "$dst/$size/apps/nzmdviewer.png"
        fi
    done

    # SVG ikona
    if [ -f "$src/nzmdviewer.svg" ]; then
        mkdir -p "$dst/scalable/apps"
        cp "$src/nzmdviewer.svg" "$dst/scalable/apps/nzmdviewer.svg"
    fi

    # Obnovi icon cache
    gtk-update-icon-cache -f -t "$dst" 2>/dev/null || true
    # KDE podrška
    kbuildsycoca6 --noincremental 2>/dev/null || kbuildsycoca5 --noincremental 2>/dev/null || true
}

do_remove_icons() {
    local dst="$HOME/.local/share/icons/hicolor"

    for size in 16x16 22x22 24x24 32x32 48x48 64x64 128x128 256x256 512x512; do
        rm -f "$dst/$size/apps/nzmdviewer.png"
    done
    rm -f "$dst/scalable/apps/nzmdviewer.svg"

    gtk-update-icon-cache -f -t "$dst" 2>/dev/null || true
    kbuildsycoca6 --noincremental 2>/dev/null || kbuildsycoca5 --noincremental 2>/dev/null || true
}

# ============================================
# FORCE INSTALL FUNKCIJA
# ============================================
do_force_install() {
    echo ""
    echo -e "${YELLOW}╔════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║  🔄 NZ-MDviewer Force Reinstaller          ║${NC}"
    echo -e "${YELLOW}║  Gazi staru verziju i instalira novu       ║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════════╝${NC}"
    echo ""

    # Provjeri da li source NZ-MDviewer/ paket postoji
    if [ ! -d "$SCRIPT_DIR/NZ-MDviewer" ]; then
        echo -e "${RED}❌ GREŠKA: Ne mogu naći NZ-MDviewer/ paket${NC}"
        echo "   Stavi ovu skriptu u isti folder sa NZ-MDviewer/ direktorijumom"
        exit 1
    fi

    # 1. Backup postavki
    echo -e "${YELLOW}[1/5] Backup postavki...${NC}"
    HAS_BACKUP=false
    if do_backup_settings; then
        HAS_BACKUP=true
    else
        echo -e "  ${CYAN}○${NC} Nema postojećih postavki za backup"
    fi

    # 2. Ukloni staru instalaciju
    echo -e "${YELLOW}[2/5] Uklanjam postojeću instalaciju...${NC}"
    if [ -d "$INSTALL_DIR" ]; then
        rm -rf "$INSTALL_DIR"
        echo -e "  ${GREEN}✓${NC} Obrisano: $INSTALL_DIR"
    fi
    if [ -f "$BIN_DIR/nzmdviewer" ]; then
        rm -f "$BIN_DIR/nzmdviewer"
        echo -e "  ${GREEN}✓${NC} Obrisan: $BIN_DIR/nzmdviewer"
    fi
    if [ -f "$DESKTOP_DIR/nzmdviewer.desktop" ]; then
        rm -f "$DESKTOP_DIR/nzmdviewer.desktop"
        echo -e "  ${GREEN}✓${NC} Obrisan: $DESKTOP_DIR/nzmdviewer.desktop"
    fi
    # Cleanup old balkanmd artifacts
    [ -f "$BIN_DIR/balkanmd" ] && rm -f "$BIN_DIR/balkanmd" && echo -e "  ${GREEN}✓${NC} Obrisan stari: $BIN_DIR/balkanmd"
    [ -f "$DESKTOP_DIR/balkanmd.desktop" ] && rm -f "$DESKTOP_DIR/balkanmd.desktop" && echo -e "  ${GREEN}✓${NC} Obrisan stari: $DESKTOP_DIR/balkanmd.desktop"

    # 3. Čisti sistem
    echo -e "${YELLOW}[3/5] Čistim sistem...${NC}"
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true

    # 4. Nova instalacija
    echo -e "${YELLOW}[4/5] Instaliram novu verziju...${NC}"
    do_install_silent
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Greška prilikom instalacije${NC}"
        if [ "$HAS_BACKUP" = true ]; then
            echo -e "${YELLOW}Vraćam backup postavki...${NC}"
            mkdir -p "$(dirname "$SETTINGS_FILE")"
            do_restore_settings
        fi
        exit 1
    fi

    # 5. Restore postavki i verifikacija
    echo -e "${YELLOW}[5/5] Verifikacija i restore postavki...${NC}"
    if [ "$HAS_BACKUP" = true ]; then
        do_restore_settings
    fi

    if [ -d "$INSTALL_DIR" ] && [ -f "$BIN_DIR/nzmdviewer" ]; then
        echo -e "${GREEN}✅ Force reinstall uspješan!${NC}"
    else
        echo -e "${RED}❌ Greška prilikom reinstalacije${NC}"
        exit 1
    fi

    echo ""
    echo -e "${GREEN}🎉 NZ-MDviewer v$VERSION je instaliran!${NC}"
    echo ""
}

do_install_silent() {
    # Instalacija bez interaktivnog ispisa (za force install)
    mkdir -p "$INSTALL_DIR" || { echo -e "${RED}❌ Ne mogu kreirati $INSTALL_DIR${NC}" >&2; return 1; }
    mkdir -p "$BIN_DIR" || { echo -e "${RED}❌ Ne mogu kreirati $BIN_DIR${NC}" >&2; return 1; }
    mkdir -p "$DESKTOP_DIR" || { echo -e "${RED}❌ Ne mogu kreirati $DESKTOP_DIR${NC}" >&2; return 1; }

    # Provjeri source
    if [ ! -d "$SCRIPT_DIR/NZ-MDviewer" ]; then
        echo -e "${RED}❌ GREŠKA: Ne mogu naći NZ-MDviewer/ paket${NC}" >&2
        return 1
    fi

    # Provjeri da li python3 postoji
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ GREŠKA: python3 nije instaliran${NC}" >&2
        return 1
    fi

    # Kreiraj venv i instaliraj
    rm -rf "$VENV_DIR" 2>/dev/null
    python3 -m venv --system-site-packages "$VENV_DIR" || {
        echo -e "${RED}❌ GREŠKA: Ne mogu kreirati virtualno okruženje${NC}" >&2
        return 1
    }
    "$VENV_DIR/bin/pip" install --upgrade pip wheel -q 2>/dev/null || true
    "$VENV_DIR/bin/pip" install markdown pymdown-extensions pygments -q 2>/dev/null || true

    # Kopiraj paket (sve je unutar NZ-MDviewer/)
    cp -r "$SCRIPT_DIR/NZ-MDviewer" "$INSTALL_DIR/"

    # Wrapper skripta
    cat > "$BIN_DIR/nzmdviewer" << WRAPPER_EOF
#!/bin/bash
INSTALL_DIR="$INSTALL_DIR"
exec "\$INSTALL_DIR/venv/bin/python" "\$INSTALL_DIR/NZ-MDviewer/NZ-MDviewer.py" "\$@"
WRAPPER_EOF

    chmod +x "$BIN_DIR/nzmdviewer"

    # Instaliraj ikone u hicolor theme (proper desktop integracija)
    do_install_icons

    # Desktop entry — Icon=nzmdviewer (sistem nađe ikonu iz hicolor)
    cat > "$DESKTOP_DIR/nzmdviewer.desktop" << DESKTOP_EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=NZ-MDviewer
GenericName=Markdown Viewer
Comment=NZ-MDviewer — GitHub-style Markdown Viewer v$VERSION
Exec=$BIN_DIR/nzmdviewer %f
Icon=nzmdviewer
Terminal=false
Categories=Office;Viewer;TextEditor;
MimeType=text/markdown;text/x-markdown;
Keywords=markdown;md;viewer;github;nzmdviewer;
StartupNotify=true
StartupWMClass=NZ-MDviewer
DESKTOP_EOF

    chmod 644 "$DESKTOP_DIR/nzmdviewer.desktop"
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    xdg-mime default nzmdviewer.desktop text/markdown 2>/dev/null || true
    xdg-mime default nzmdviewer.desktop text/x-markdown 2>/dev/null || true
    return 0
}

# ============================================
# UPDATE FUNKCIJA
# ============================================
do_update() {
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  🔄 NZ-MDviewer Updater                    ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════╝${NC}"
    echo ""

    INSTALLED_VER="$(_get_installed_version)"

    if [ -z "$INSTALLED_VER" ]; then
        echo -e "${YELLOW}NZ-MDviewer nije instaliran. Pokreni --install za instalaciju.${NC}"
        echo ""
        exit 1
    fi

    echo -e "  Instalirana verzija : ${YELLOW}v$INSTALLED_VER${NC}"
    echo -e "  Dostupna verzija    : ${GREEN}v$VERSION${NC}"
    echo ""

    if [ "$INSTALLED_VER" = "$VERSION" ]; then
        echo -e "${GREEN}✓ Već imaš najnoviju verziju (v$VERSION). Nema potrebe za ažuriranjem.${NC}"
        echo ""
        exit 0
    fi

    echo -e "${YELLOW}Nova verzija dostupna! Ažuriram...${NC}"
    echo ""
    do_force_install
}

# ============================================
# INSTALL FUNKCIJA
# ============================================
do_install() {
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  📦 NZ-MDviewer Installer                  ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════╝${NC}"
    echo ""

    # Provjeri da li je već instaliran
    INSTALLED_VER="$(_get_installed_version)"
    if [ -n "$INSTALLED_VER" ] && [ -f "$BIN_DIR/nzmdviewer" ]; then
        echo -e "${YELLOW}NZ-MDviewer v$INSTALLED_VER je već instaliran.${NC}"
        echo ""
        echo "  Opcije:"
        echo "  - $0 --update    → Ažuriraj na v$VERSION"
        echo "  - $0 --force     → Force reinstall"
        echo ""
        exit 0
    fi

    # Provjeri source
    if [ ! -d "$SCRIPT_DIR/NZ-MDviewer" ]; then
        echo -e "${RED}❌ GREŠKA: Ne mogu naći NZ-MDviewer/ paket${NC}"
        echo "   Stavi ovu skriptu u isti folder sa NZ-MDviewer/ direktorijumom"
        exit 1
    fi

    echo -e "${GREEN}✓${NC} Pronađen source paket: $SCRIPT_DIR/NZ-MDviewer"
    echo ""

    # 1. Kreiraj direktorije
    echo "[1/6] Kreiram direktorije..."
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$BIN_DIR"
    mkdir -p "$DESKTOP_DIR"

    # 2. Kreiraj virtualno okruženje
    echo "[2/6] Kreiram Python virtualno okruženje..."
    rm -rf "$VENV_DIR" 2>/dev/null
    python3 -m venv --system-site-packages "$VENV_DIR"

    # 3. Instaliraj dependencije
    echo "[3/6] Instaliram dependencije..."
    "$VENV_DIR/bin/pip" install --upgrade pip wheel -q 2>/dev/null || true
    "$VENV_DIR/bin/pip" install \
        markdown \
        pymdown-extensions \
        pygments \
        -q 2>/dev/null || true

    # Provjeri da li PySide6 radi
    if ! "$VENV_DIR/bin/python" -c "from PySide6.QtWebEngineWidgets import QWebEngineView" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  PySide6-WebEngine nije dostupan kroz pip za tvoju Python verziju${NC}"
        echo "   Instaliram system package..."

        if command -v pacman &> /dev/null; then
            echo "   Pokreni: sudo pacman -S pyside6 qt6-webengine"
        elif command -v apt &> /dev/null; then
            echo "   Pokreni: sudo apt install python3-pyside6.qtwebengine"
        elif command -v dnf &> /dev/null; then
            echo "   Pokreni: sudo dnf install python3-pyside6"
        fi

        echo ""
        echo -e "${YELLOW}Nakon instalacije system paketa, pokreni ovu skriptu ponovo.${NC}"
        exit 1
    fi

    # 4. Kopiraj paket (sve je unutar NZ-MDviewer/)
    echo "[4/6] Kopiram aplikaciju..."
    cp -r "$SCRIPT_DIR/NZ-MDviewer" "$INSTALL_DIR/"

    # 5. Kreiraj wrapper skriptu
    echo "[5/6] Kreiram launcher..."
    cat > "$BIN_DIR/nzmdviewer" << WRAPPER_EOF
#!/bin/bash
# NZ-MDviewer Launcher
# Auto-generated wrapper

INSTALL_DIR="$INSTALL_DIR"

exec "\$INSTALL_DIR/venv/bin/python" "\$INSTALL_DIR/NZ-MDviewer/NZ-MDviewer.py" "\$@"
WRAPPER_EOF

    chmod +x "$BIN_DIR/nzmdviewer"

    # 6. Instaliraj ikone u hicolor theme
    echo "[6/7] Instaliram ikone..."
    do_install_icons

    # 7. Kreiraj .desktop fajl
    echo "[7/7] Kreiram desktop entry..."
    cat > "$DESKTOP_DIR/nzmdviewer.desktop" << DESKTOP_EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=NZ-MDviewer
GenericName=Markdown Viewer
Comment=NZ-MDviewer — GitHub-style Markdown Viewer v$VERSION
Exec=$BIN_DIR/nzmdviewer %f
Icon=nzmdviewer
Terminal=false
Categories=Office;Viewer;TextEditor;
MimeType=text/markdown;text/x-markdown;
Keywords=markdown;md;viewer;github;nzmdviewer;
StartupNotify=true
StartupWMClass=NZ-MDviewer
DESKTOP_EOF

    chmod 644 "$DESKTOP_DIR/nzmdviewer.desktop"

    echo ""
    echo "Postavljam kao default za .md fajlove..."
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    xdg-mime default nzmdviewer.desktop text/markdown 2>/dev/null || true
    xdg-mime default nzmdviewer.desktop text/x-markdown 2>/dev/null || true

    # Provjeri PATH
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        echo ""
        echo -e "${YELLOW}⚠️  ~/.local/bin nije u PATH!${NC}"
        echo "   Dodajem u ~/.bashrc..."

        if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' ~/.bashrc 2>/dev/null; then
            echo '' >> ~/.bashrc
            echo '# Added by NZ-MDviewer installer' >> ~/.bashrc
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        fi

        echo "   Pokreni: source ~/.bashrc"
    fi

    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ INSTALACIJA USPJEŠNA!                  ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Instalirano u: $INSTALL_DIR"
    echo "Executable:    $BIN_DIR/nzmdviewer"
    echo "Desktop file:  $DESKTOP_DIR/nzmdviewer.desktop"
    echo ""
    echo "═══════════════════════════════════════════"
    echo "  KAKO KORISTITI:"
    echo "═══════════════════════════════════════════"
    echo ""
    echo "  Terminal:    nzmdviewer ~/notes/README.md"
    echo "  Dolphin:     Desni klik na .md → Open With → NZ-MDviewer"
    echo ""
    echo "Ako Dolphin ne vidi aplikaciju odmah, probaj:"
    echo "  - Restartuj Dolphin"
    echo "  - Ili se odjavi/prijavi"
    echo ""
    echo -e "${GREEN}Uživaj brate! 🎉${NC}"
    echo ""
}

# ============================================
# UNINSTALL FUNKCIJA
# ============================================
do_uninstall() {
    echo ""
    echo -e "${RED}╔════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  🗑️  NZ-MDviewer Uninstaller               ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════╝${NC}"
    echo ""

    # Provjeri da li je instalirano
    HAS_INSTALL=false
    [ -d "$INSTALL_DIR" ] && HAS_INSTALL=true
    [ -f "$BIN_DIR/nzmdviewer" ] && HAS_INSTALL=true
    [ -f "$DESKTOP_DIR/nzmdviewer.desktop" ] && HAS_INSTALL=true
    # Also check old balkanmd artifacts
    [ -f "$BIN_DIR/balkanmd" ] && HAS_INSTALL=true
    [ -f "$DESKTOP_DIR/balkanmd.desktop" ] && HAS_INSTALL=true

    if [ "$HAS_INSTALL" = false ]; then
        echo -e "${YELLOW}NZ-MDviewer nije instaliran.${NC}"
        echo ""
        exit 0
    fi

    echo "Ovo će ukloniti:"
    [ -d "$INSTALL_DIR" ] && echo "  - $INSTALL_DIR"
    [ -f "$BIN_DIR/nzmdviewer" ] && echo "  - $BIN_DIR/nzmdviewer"
    [ -f "$DESKTOP_DIR/nzmdviewer.desktop" ] && echo "  - $DESKTOP_DIR/nzmdviewer.desktop"
    echo "  - Ikone iz ~/.local/share/icons/hicolor/"
    [ -f "$BIN_DIR/balkanmd" ] && echo "  - $BIN_DIR/balkanmd (stari)"
    [ -f "$DESKTOP_DIR/balkanmd.desktop" ] && echo "  - $DESKTOP_DIR/balkanmd.desktop (stari)"
    echo ""

    read -p "Jesi li siguran? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deinstalacija otkazana."
        exit 0
    fi

    echo ""
    echo "[1/4] Brišem program..."
    if [ -d "$INSTALL_DIR" ]; then
        rm -rf "$INSTALL_DIR"
        echo -e "  ${GREEN}✓${NC} Obrisan: $INSTALL_DIR"
    fi

    echo "[2/4] Brišem launcher..."
    if [ -f "$BIN_DIR/nzmdviewer" ]; then
        rm -f "$BIN_DIR/nzmdviewer"
        echo -e "  ${GREEN}✓${NC} Obrisan: $BIN_DIR/nzmdviewer"
    fi
    # Cleanup old balkanmd
    if [ -f "$BIN_DIR/balkanmd" ]; then
        rm -f "$BIN_DIR/balkanmd"
        echo -e "  ${GREEN}✓${NC} Obrisan stari: $BIN_DIR/balkanmd"
    fi

    echo "[3/4] Brišem desktop entry..."
    if [ -f "$DESKTOP_DIR/nzmdviewer.desktop" ]; then
        rm -f "$DESKTOP_DIR/nzmdviewer.desktop"
        echo -e "  ${GREEN}✓${NC} Obrisan: $DESKTOP_DIR/nzmdviewer.desktop"
    fi
    if [ -f "$DESKTOP_DIR/balkanmd.desktop" ]; then
        rm -f "$DESKTOP_DIR/balkanmd.desktop"
        echo -e "  ${GREEN}✓${NC} Obrisan stari: $DESKTOP_DIR/balkanmd.desktop"
    fi

    echo "[4/4] Brišem ikone..."
    do_remove_icons
    echo -e "  ${GREEN}✓${NC} Ikone uklonjene iz hicolor theme"

    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true

    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ DEINSTALACIJA ZAVRŠENA!                ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
    echo ""
    echo "NZ-MDviewer je uklonjen sa sistema."
    echo ""
    echo -e "${YELLOW}Napomena:${NC} PATH postavka u ~/.bashrc nije uklonjena."
    echo "Možeš je ručno obrisati ako želiš."
    echo ""
}

# ============================================
# MAIN MENU
# ============================================
show_menu() {
    clear
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║       🎨 NZ-MDviewer Setup                 ║${NC}"
    echo -e "${CYAN}║       Beautiful Markdown Viewer            ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════╝${NC}"
    echo ""

    INSTALLED_VER="$(_get_installed_version)"
    if [ -n "$INSTALLED_VER" ] && [ -f "$BIN_DIR/nzmdviewer" ]; then
        if [ "$INSTALLED_VER" = "$VERSION" ]; then
            echo -e "  Status: ${GREEN}✓ Instaliran v$INSTALLED_VER (najnovija)${NC}"
        else
            echo -e "  Status: ${YELLOW}⚠ Instaliran v$INSTALLED_VER → dostupna v$VERSION${NC}"
        fi
    else
        echo -e "  Status: ${YELLOW}○ Nije instaliran  (dostupna v$VERSION)${NC}"
    fi
    echo ""
    echo "═══════════════════════════════════════════"
    echo ""
    echo "  1) 📦 Instaliraj"
    echo "  2) 🔄 Ažuriraj (update)"
    echo "  3) 🔁 Force reinstall"
    echo "  4) 🗑️  Deinstaliraj"
    echo "  5) ❌ Izlaz"
    echo ""
    echo "═══════════════════════════════════════════"
    echo ""
}

# ============================================
# MAIN
# ============================================
case "$1" in
    --install|-i)
        do_install
        exit 0
        ;;
    --update|-U)
        do_update
        exit 0
        ;;
    --force|-f)
        do_force_install
        exit 0
        ;;
    --uninstall|-u)
        do_uninstall
        exit 0
        ;;
    --help|-h)
        show_help
        exit 0
        ;;
    --version|-v)
        show_version
        exit 0
        ;;
    "")
        # Nema argumenta - prikaži meni
        ;;
    *)
        echo -e "${RED}Nepoznata opcija: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac

while true; do
    show_menu
    read -p "  Odaberi opciju [1-5]: " choice

    case $choice in
        1)
            do_install
            echo ""
            read -p "Pritisni Enter za nastavak..."
            ;;
        2)
            do_update
            echo ""
            read -p "Pritisni Enter za nastavak..."
            ;;
        3)
            do_force_install
            echo ""
            read -p "Pritisni Enter za nastavak..."
            ;;
        4)
            do_uninstall
            echo ""
            read -p "Pritisni Enter za nastavak..."
            ;;
        5)
            echo ""
            echo "Doviđenja! 👋"
            echo ""
            exit 0
            ;;
        *)
            echo -e "${RED}Nevažeća opcija!${NC}"
            sleep 1
            ;;
    esac
done
