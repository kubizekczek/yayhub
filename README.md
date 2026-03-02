# Yay gui

PyQt6 frontend do **pacmana** i **yay** dla Arch Linuksa.

## Funkcjonalności

✅ **Zarządzanie pakietami**
- Przeglądanie pakietów z oficjalnych repozytoriów (core, extra, multilib)
- Obsługa pakietów AUR (wymaga yay)
- Live search - wyszukiwanie w rzeczywistym czasie
- Filtrowanie: wszystkie, zainstalowane, niezainstalowane
- Sortowanie: nazwa, repozytorium

✅ **Cache**
- Automatyczne indeksowanie pakietów
- Buforowanie listy pakietów (JSON)
- Odświeżanie listy przyciskiem "Refresh"

✅ **Instalacja i usuwanie**
- Wsparcie dla pkexec (brak potrzeby terminalowego hasła)
- Wsparcie dla pacmana (repo)
- Wsparcie dla yay (AUR)
- Podgląd logu instalacji

✅ **UI**
- Kompatybilność z Wayland i X11
- Ciemny motyw (PyQt6 style)
- Responsywny interfejs
- Podgląd szczegółów pakietu

## Wymagania

- **Arch Linux** (lub pochodna)
- **Python 3.8+**
- **pacman** (domyślny)
- **yay** (opcjonalnie, dla AUR)
- **PyQt6** (zainstalowany automatycznie)

## Instalacja

### 1. Szybka instalacja (zalecane)

```bash
cd aplikacja
chmod +x install.sh
./install.sh
```

### 2. Instalacja ręczna

```bash
# 1. Zainstaluj zależności
pip install --user -r requirements.txt

# 2. Uruchom aplikację
python3 main.py
```

### 3. Instalacja yay (dla AUR)

```bash
# Jeśli jeszcze nie masz yay
git clone https://aur.archlinux.org/yay.git
cd yay
makepkg -si
```

## Użytkowanie

### Uruchomienie

```bash
python3 main.py
```

Lub jeśli zainstalowałeś desktop entry:
- Otwórz application menu i szukaj "Pacman GUI"

### Interfejs

1. **Wyszukiwanie** - wpisz nazwę pakietu lub część opisu
2. **Filtrowanie** - wybierz z dropdown: Wszystkie / Zainstalowane / Niezainstalowane
3. **Sortowanie** - sortuj po nazwie lub repozytorium
4. **Refresh** - odśwież listę pakietów z systemu
5. **Listę pakietów** - kliknij na pakiet aby zobaczyć szczegóły
6. **Szczegóły** - przycisk "Install" lub "Remove" (zależy od statusu)

### `package_manager.py`
- Wrapper dla komend pacman i yay
- Obsługa instalacji, usuwania, listy pakietów
- Parsowanie wyjścia z pacmana

### `cache_manager.py`
- Buforowanie listy pakietów do JSON
- Automatyczne czyszczenie cache po 1 godzinie
- Ładowanie cache przy starcie

### `main_window.py`
- Główne okno aplikacji QMainWindow
- Koordynacja między widgetami
- Wątki dla asynchronicznego ładowania

### UI Widgets
- `SearchWidget` - pole wyszukiwania z live preview
- `PackageListWidget` - tabela pakietów
- `PackageDetailsWidget` - szczegóły wybranego pakietu
- `main_window.py` - integracja wszystkich widgetów

## Obsługa błędów

Aplikacja sprawdza:
- ✅ Dostępność yay (dla AUR)
- ✅ Dostępność pacmana
- ✅ Dostępność pkexec (sudo)
- ✅ Błędy połączenia sieciowego
- ✅ Błędy instalacji/usuwania

## Opcje zaawansowane

### Zmiana timeout cache
Edytuj plik `pacman_gui/utils/cache_manager.py`:
```python
CACHE_TIMEOUT = 3600  # Zmień na liczbę sekund
```

### Bezpieczne polecenia sudo
Aplikacja używa `pkexec` zamiast `sudo` dla bezpieczeństwa.

## Rozwiązywanie problemów

### "yay not found - AUR support disabled"
Zainstaluj yay:
```bash
git clone https://aur.archlinux.org/yay.git
cd yay
makepkg -si
```

### "Permission denied" lub problemy z sudo
Upewnij się, że:
- Zainstalowałeś `polkit`
- Twój użytkownik ma dostęp do sudo

```bash
sudo pacman -S polkit
```

### Aplikacja się nie uruchamia
Sprawdź logi:
```bash
python3 main.py 2>&1 | head -50
```

## Licencja

MIT License

## Autor

Created for Arch Linux users

## Roadmap / TODO

- [ ] AppImage bundle
- [ ] Ciemny motyw (już jest domyślny)
- [ ] Pasek postępu przy instalacji
- [ ] Możliwość wyboru między pacmanem a yay
- [ ] Historia instala
- [ ] Statystyki pakietów
