import re
import unicodedata
import uuid


def sanitize_filename(filename):
    filename = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')

    filename = re.sub(r'[/\0:]', '_', filename)

    filename = filename.strip('. ')

    filename = filename[:255]

    return str(uuid.uuid4())+filename
