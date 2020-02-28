# Things to do on Production Mode

## Django

#### Make sure to follow the [Django checklist](https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/)

Check if production ready with:

```bash
python manage.py check --deploy
```

##### Remember that the ```SECRET_KEY``` used in production is not in source control or accessible outside the production server



## Logging

#### Set in the Django Settings LOG_TO_CLOUD to True

```python
# settings.py
# turn this on to log into stackdriver
LOG_TO_CLOUD=True
```

This should be set to true in production

(e ter a variavel de  terminal GOOGLE_APPLICATION_CREDENTIALS definida com a chave, mais em LOGGING.md)
