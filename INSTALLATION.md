# YayHub - Instrukcja Instalacji

Szybka i łatwa instalacja aplikacji z Git.

## Wymagania

- **Arch Linux** lub pochodne (Manjaro, EndeavourOS, itp.)
- **Python 3.8+**
- **Git**

## Szybka Instalacja (1 komenda)

```bash
bash <(curl -sL https://github.com/kubizekczek/yayhub/raw/main/install.sh)
```

Lub jeśli masz plik `install.sh` lokalnie:

```bash
chmod +x install.sh
./install.sh
```

## Krok po kroku

### 1. Pobierz skrypt instalacyjny
```bash
git clone https://github.com/kubizekczek/yayhub.git
cd yayhub
```

### 2. Uruchom instalator
```bash
chmod +x install.sh
./install.sh
```

Skrypt automatycznie:
- ✅ Sprawdzi wymagane zależności (Python, Git)
- ✅ Sklonuje repozytorium do `~/.local/opt/yayhub`
- ✅ Utworzy wirtualne środowisko Python
- ✅ Zainstaluje wszystkie zależności
- ✅ Stworzy launcher w menu aplikacji

### 3. Uruchom aplikację

**Metoda 1 - Menu aplikacji:**
- Otwórz menu aplikacji
- Wyszukaj "YayHub"
- Kliknij aby uruchomić

**Metoda 2 - Linia poleceń:**
```bash
~/.local/opt/yayhub/venv/bin/python3 ~/.local/opt/yayhub/main.py
```

## Ścieżki instalacji

- **Katalog instalacji:** `~/.local/opt/yayhub`
- **Launcher aplikacji:** `~/.local/share/applications/yayhub.desktop`
- **Python venv:** `~/.local/opt/yayhub/venv`

## Odinstalowanie

```bash
rm -rf ~/.local/opt/yayhub
rm ~/.local/share/applications/yayhub.desktop
```

## Rozwiązywanie problemów

### "Git nie jest zainstalowany!"
```bash
sudo pacman -S git
```

### "Python3 nie jest zainstalowany!"
```bash
sudo pacman -S python
```

### Aplikacja się nie uruchamia
Spróbuj uruchomić ręcznie aby zobaczyć błąd:
```bash
~/.local/opt/yayhub/venv/bin/python3 ~/.local/opt/yayhub/main.py
```

### Aktualizacja do najnowszej wersji
```bash
cd ~/.local/opt/yayhub
git pull origin main
./venv/bin/pip install -r requirements.txt
```

## Wsparcie

Przy problemach otwórz issue na GitHubie: https://github.com/kubizekczek/yayhub/issues

---

**Wersja:** 1.0  
**Data:** 2 marca 2026
