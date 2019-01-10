# AudioLabApp
Laboratorium dźwiękowe.

Serwis labapp pozwala na gromadzenie i zarządzanie nagraniami dźwiękowymi pochodzącymi z eksperymentów. 

## Testy i uruchomienie w środowisku deweloperskim

1. Sklonuj to repozytorium

2. Dodaj ścieżkę folderu ```labapp``` do zmiennej systemowej ```PYTHONPATH```

3. Pobierz i uruchom kontener MySQL poleceniem

        docker run --name mysql \
            -p 3306:3306 \
            -e MYSQL_RANDOM_ROOT_PASSWORD=yes \
            -e MYSQL_DATABASE=labapp \
            -e MYSQL_USER=labapp \
            -e MYSQL_PASSWORD=<passphrase> \
            -d mysql:5.7

4. Ustaw odpowiednio zmienną DATABASE_URL:

    export DATABASE_URL=mysql://labapp:<passphrase>@<database_address:port>/labapp

5. Przejdź do folderu ```labapp``` i przeprowadź testy automatyczne poleceniem

        ./test.sh

6. Zaktualizuj bazę danych wykonując polecenia

        flask db upgrade

7. Uruchom aplikację poleceniem

        flask run

UWAGA: aplikacja domyślnie uruchomiona zostanie w trybie 'development', aby uruchomić w trybie 'production' zmień wartości zmiennych w pliku .flaskenv:

    FLASK_APP="app:create_app('app.config.ProductionConfig')"
    FLASK_ENV="production"

8. API można testować dowolnym narzędziem, lub w przeglądarkowym eksploratorze Swagger pod adresem:

        http://[url_aplikacji]/1.0/lab/ui


## Uruchomienie skonteneryzowanej aplikacji

Istnieje możliwość uruchomienia aplikacji w kontenerze za pomocą docker-compose. W tym celu należy najpierw zapewnić następujące zmienne środowiskowe:

    export APP_PORT= \
        DB_ROOT_PASSWORD= \
        DB_NAME= \
        DB_USER= \
        DB_PASSWORD= \
        DB_PORT= \
        SECRET_KEY= \
        MEDIA_DIR=

A następnie będąc w folderze ```labapp``` wykonać polecenie:

    docker-compose up -d --build