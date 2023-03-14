work at other branch

# How to create translation
Run following commands

edited by leo
```
cd app/
mkdir translations
pybabel extract -F babel.cfg -k _l -o messages.pot .
pybabel update -i messages.pot -d app/translations
pybabel compile -d app/translations
```
