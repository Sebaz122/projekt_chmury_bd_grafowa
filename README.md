# SocialGraph

Prosta aplikacja "Proof of Concept" do pracy z grafem społecznościowym w Neo4j, z interfejsem w Flasku, wizualizacją grafu oraz zestawem endpointów (użytkownicy, zainteresowania, relacje FRIENDS_WITH i LIKES).
Aplikacja ma symulować sieć społecznościową składającą się z osób, połączonych relacją znajomości oraz zainteresowaniami, z którymi połączone są osoby relacją typu like (osoba lubi coś).

## Wymagania

- Python 3.13+
- Konto/instancja Neo4j + URI i dane logowania
- Pakiety z `requirements.txt`

## Instalacja

Zainstaluj zależności (Windows PowerShell):

```powershell
pip install -r requirements.txt
```

## Konfiguracja połączenia z Neo4j

Aplikacja korzysta ze zmiennych środowiskowych. Utwórz plik `.env` w katalogu projektu i uzupełnij:

```env
NEO4J_URI= uri twojej bazy danych
NEO4J_USER= twoj username
NEO4J_PASSWORD= twoje hasło
```

## Uruchomienie aplikacji

Przejdź do folderu głównego aplikacji i użyj komendy:

```powershell
python .\backend.py
# Otwórz: http://127.0.0.1:5000/
```

Aby aplikacja działała poprawnie trzeba połączyć się z bazą danych Neo4J i jak wspomniane wyżej utworzyć plik `.env` z danymi.

## Interfejs WWW

- Strona główna (`/`):
  - Linki do podstron: Użytkownik, Zainteresowanie, Relacje
  - Osadzona wizualizacja grafu (PyVis) z Neo4j (`/graph`)
- `Użytkownik` (`/uzytkownik`):
  - Dodawanie/Usuwanie użytkownika, zmiana nazwy, dodanie dowolnej właściwości do użytkownika
  - Wyszukiwanie znajomych użytkownika
- `Zainteresowanie` (`/zainteresowanie`):
  - Dodawanie/Usuwanie zainteresowania
  - Wyszukiwanie zainteresowań użytkownika
- `Relacje` (`/relacje`):
  - Tworzenie/Usuwanie relacji FRIENDS_WITH
  - Tworzenie/Usuwanie relacji LIKES
