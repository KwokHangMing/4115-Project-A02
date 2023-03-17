
# How **NOT** to create translation
Run following commands
```
cd app/
mkdir translations
pybabel extract -F babel.cfg -k lazy_gettext -o translations/messages.pot .
pybabel init -i translations/messages.pot -d translations -l en
pybabel init -i translations/messages.pot -d translations -l es
pybabel init -i translations/messages.pot -d translations -l zh
pybabel compile -d translations
```

# How to update translation
```
cd app/
pybabel update -i translations/messages.pot -d translations
```

# User
login as demo
pw is 123

# Flask-uploads

In ```flask_uploads.py```

Change
```
from werkzeug import secure_filename,FileStorage
```
to
```
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
```
