def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

def serialize(obj):
    if obj is None:
        return {}
    if hasattr(obj, '__dict__'):
        serialized_data = {key: value for key, value in obj.__dict__.items() if not 
                           key.startswith('_')}
        missing_attrs = set(obj.__dict__.keys()) - set(serialized_data.keys())
        for attr in missing_attrs:
            serialized_data[attr] = None
        return serialized_data
    if hasattr(obj, '__slots__'):
        serialized_data = {attr: getattr(obj, attr) for attr in obj.__slots__}
        missing_attrs = set(obj.__slots__) - set(serialized_data.keys())
        for attr in missing_attrs:
            serialized_data[attr] = None
        return serialized_data
    return {}