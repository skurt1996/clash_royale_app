# clash_royale_app
Diese Webanwendung dient zum Tracken von privaten Kämpfen innerhalb unseres Clans im Spiel "Clash Royale". Die Anwendung wird noch ausgebaut. Der Code ist noch unvollständig und ausbaufähig. Ziel der Anwendung ist es zum Schluss mit Hilfe von historischen Daten die Ausgänge von Kämpfen mit einer angemessenen Präzision vorauszusagen und interessante Statistiken für meinen Clan zu erstellen.

Sie können meine Webseite unter http://45.84.199.64/ erreichen

Leitfaden zum Starten der Anwendung:
1) Installieren Sie mithilfe von `pip` die Abhängigkeiten, die in `requirements.txt` gelistet sind.
2) Erstellen Sie eine MySQL Datenbank und erteilen Sie ihrem MySQL Benutzer die notwendigen Privilegien.
3) Erstellen Sie entsprechende Umgebungsvariablen mit den Namen `MYSQL_USERNAME` und `MYSQL_PASSWORD` auf ihrem Betriebssystem.
4) Erstellen Sie einen API Key auf https://developer.clashroyale.com/ und erstellen Sie eine Umgebungsvariable mit dem Namen `CLASH_ROYALE_API_TOKEN` auf ihrem Betriebssystem.
5) Erstellen Sie eine Umgebungsvariable mit dem Namen `SECRET_KEY` auf ihrem Betriebssystem. Dazu ist die Methode `token_hex` des Python-Moduls `secrets` gut geeignet. Eine Mindestlänge von 24 Bytes ist von Flask empfohlen.
6) Führen Sie die `initialize_tables` Methode in `db.py` aus, um die notwendigen Tabellen für ihre Datenbank automatisch zu erstellen.
7) Führen Sie regelmäßig (bevorzugt via `crontab` in Ubuntu) die Methoden `insert_members`, `insert_new_battles`, `update_player_infos` aus, um Daten aus der API für ihre Webanwendung herunterzuladen.
8) Die Variable `CLAN_TAG` in `data_retrieval.py` sollte an ihren Clan Tag angepasst werden, um Daten für Ihren Clan herunterzuladen. Es werden ausschließlich die Kampfmodi und Kampftypen beachtet, die in den Variablen `ALLOWED_BATTLE_TYPE` und `ALLOWED_BATTLE_MODES` gelistet sind. Die Variablen können entsprechend verändert werden, um weitere Kampfmodi und Kampftypen zu unterstützen. 
9) Führen Sie `run.py` aus. Nun können Sie auf ihre eigene Clash Royale Clan Statistik Webseite über `localhost:5000` lokal zugreifen.

Achtung:
1) Die Bilder, die in den html templates referenziert werden, sind nicht Teil dieses Code Bases. Diese können gerne bei mir erfragt werden. Die Funktionalität der Webanwendung wurde nicht ohne die statischen Files getestet.
2) Sie sollten Benutzernamen, Passwörter und Tokens am Besten als Umgebungsvariablen speichern anstatt Sie in Klartext als Bestandteil ihres Codes zu haben. Der Code in dieser Repository dient nur zu Demonstrationszwecken.
3) Die Dokumentationen für die einzelnen Python Methoden wurden per ChatGPT erstellt und nur grob auf Korrektheit überprüft.
4) Diese Anwendung ist noch in Bearbeitung. Die Korrektheit und Sicherheit kann nicht garantiert werden.
