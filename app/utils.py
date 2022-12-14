from pydoc import plain
from passlib.context import CryptContext
from datetime import datetime, timezone

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password:str):
    return pwd_context.hash(password)

def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def date_beautifier(values):
    d = values['created_at']
    if d is not None:
        diff = datetime.now(tz=timezone.utc) - d
        s = diff.seconds
        if diff.days > 30 or diff.days < 0:
            values['created_at'] = d.strftime('Y-m-d H:i')
            return values
        elif diff.days == 1:
            values['created_at'] = 'One day ago'
            return values
        elif diff.days > 1:
            values['created_at'] = '{} days ago'.format(diff.days)
            return values
        elif s <= 1:
            values['created_at'] = 'just now'
            return values
        elif s < 60:
            values['created_at'] = '{} seconds ago'.format(s)
            return values
        elif s < 120:
            values['created_at'] = 'one minute ago'
            return values
        elif s < 3600:
            values['created_at'] = '{} minutes ago'.format(round(s/60))
            return values
        elif s < 7200:
            values['created_at'] = 'one hour ago'
            return values
        else:
            values['created_at'] = '{} hours ago'.format(round(s/3600))
            return values
    else:
        values['created_at'] = None
        return values