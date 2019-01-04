# AudioLabApp
Laboratorium dźwiękowe.

Serwis labapp pozwala na gromadzenie i zarządzanie nagraniami dźwiękowymi pochodzącymi z eksperymentów. 

## Testy i uruchomienie

1. Sklonuj to repozytorium

2. Dodaj ścieżkę folderu ```labapp``` do zmiennej systemowej ```PYTHONPATH```

3. Pobierz i uruchom kontener MySQL poleceniem

    docker run --name mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=toor -d mysql:5.7

4. Dostosuj zmienną LABAPP_DATABASE_URL w pliku ```config.py``` lub tworząc zmienną środowiskową

5. Przejdź do folderu ```labapp``` i przeprowadź testy automatyczne poleceniem

    ./test.sh

6. Wykonaj migrację do bazy danych wykonując polecenia

    flask db init
    flask db migrate
    flask db upgrade

7. Uruchom aplikację poleceniem

    flask run

UWAGA: aplikacja domyślnie uruchomiona zostanie w trybie 'development', aby uruchomić w trybie 'production' zmień wartości zmiennych w pliku .flaskenv:

    FLASK_APP="app:create_app('app.config.ProductionConfig')"
    FLASK_ENV="production"

8. API można testować dowolnym narzędzień, lub w przeglądarkowym eksploratorze Swagger pod adresem:

    http://[url_aplikacji]/1.0/lab/ui
