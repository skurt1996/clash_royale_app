# clash_royale_app
Diese Webanwendung dient zum Tracken von privaten Kämpfen innerhalb unseres Clans im Spiel "Clash Royale". Die Anwendung wird noch ausgebaut. Der Code ist noch unvollständig und ausbaufähig. Ziel der Anwendung ist es zum Schluss mit Hilfe von historischen Daten die Ausgänge von Kämpfen mit einer angemessenen Präzision vorauszusagen und interessante Statistiken für meinen Clan zu erstellen.

Sie können meine Webseite unter http://45.84.199.64/ erreichen

Leitfaden zum Starten der Anwendung:
1) Installieren Sie mithilfe von `pip` die Abhängigkeiten, die in `requirements.txt` gelistet sind.
2) Erstellen Sie eine MySQL Datenbank und erteilen Sie ihrem MySQL Benutzer die notwendigen Privilegien.
3) Passen Sie die `create_connection` Methode in `db.py` so an, dass Sie mit ihrem MySQL Benutzer per Python auf die Datenbank zugreifen können.
4) Erstellen Sie einen API Key auf https://developer.clashroyale.com/ und passen Sie die `API_TOKEN` Variable in `data_retrieval.py` entsprechend an.
5) Führen Sie die `initialize_tables` Methode in `db.py` aus, um die notwendigen Tabellen für ihre Datenbank automatisch zu erstellen.
6) Führen Sie regelmäßig (bevorzugt via `crontab` in Ubuntu) die Methoden `insert_members`, `insert_new_battles`, `update_player_infos` aus, um Daten aus der API für ihre Webanwendung herunterzuladen.
7) Die Variable `CLAN_TAG` in `data_retrieval.py` sollte an ihren Clan Tag angepasst werden, um Daten für Ihren Clan herunterzuladen. Es werden ausschließlich die Kampfmodi und Kampftypen beachtet, die in den Variablen `ALLOWED_BATTLE_TYPE` und `ALLOWED_BATTLE_MODES` gelistet sind. Die Variablen können entsprechend verändert werden, um weitere Kampfmodi und Kampftypen zu unterstützen. 
8) Führen Sie `run.py` aus. Nun können Sie auf ihre eigene Clash Royale Clan Statistik Webseite über `localhost:5000` zugreifen.

Achtung:
1) Die Bilder, die in den html templates referenziert werden, sind nicht Teil dieses Code Bases. Diese können gerne bei mir erfragt werden. Die Funktionalität der Webanwendung wurde nicht ohne die statischen Files getestet.
2) Sie sollten Benutzernamen, Passwörter und Tokens am Besten als Umgebungsvariablen speichern anstatt Sie in Klartext als Bestandteil ihres Codes zu haben. Der Code in dieser Repository dient nur zu Demonstrationszwecken.
3) Diese Anwendung ist noch in Bearbeitung. Die Korrektheit und Sicherheit kann nicht garantiert werden.
