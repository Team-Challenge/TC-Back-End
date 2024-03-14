from pydantic import ValidationError


class UserError(Exception):
    pass

class NotFoundError(Exception):
    pass

def serialize_validation_error(e: ValidationError) -> dict:
    error_messages = []
    for error in e.errors():
        error_messages.append({
            'type': error['type'],
            'msg': error['msg'],
            'loc': error['loc']
        })
    return {'error': error_messages}
