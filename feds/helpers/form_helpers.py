def extract_model_field_meta_data(form, attributes_to_extract):
    """ Extract meta-data from the data model fields the form is handling. """
    if not hasattr(form, 'base_fields'):
        raise AttributeError('Form does not have base_fields. Is it a ModelForm?')
    meta_data = dict()
    for field_name, field_data in form.base_fields.items():
        for attrib in attributes_to_extract:
            meta_data[field_name] = {
                attrib: getattr(field_data, attrib, '')
            }
    return meta_data
