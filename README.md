Google Calendar to Mathrice
========

Export des calendriers/événements Google Calendar aux formats Mathrice (JSON et iCalendar)

# init :
* `virtualenv -p python3 env`
* `source env/bin/activate`
* `pip install -r requirements.txt`
* Créer une clé "**service account**" ici :
  https://developers.google.com/api-client-library/python/auth/service-accounts
  et télécharger cette clé pour remplacer le fichier **client_secret_service_account.json**
* `./google_to_mathrice.py`



# informations :

Plateforme Mathrice (agenda CNRS des événements mathématiques) :
https://portail.math.cnrs.fr/agenda


Google Calendar :
https://calendar.google.com/calendar/
