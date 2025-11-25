from googleapiclient.errors import HttpError
import json

def is_quota_exceeded_error(e):
    if not isinstance(e, HttpError):
        return False
    if e.resp.status != 403:
        return False
    try:
        error_details = json.loads(e.content.decode('utf-8'))
        for error in error_details.get('error', {}).get('errors', []):
            if error.get('reason') == 'quotaExceeded':
                return True
    except Exception as e:
        pass
    return False