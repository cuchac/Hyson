from django.db.models.fields import NOT_PROVIDED
from django.utils import simplejson as json

from hyson.ordereddict import OrderedDict
from hyson.field_types import FIELD_TYPES
from hyson.utils import dejsonize

def convert(klass):
    #model_name = instance().__class__.__name__
    model_name = klass.__name__

    fields = list()
    validators = list()

    #for field_name in instance._meta.get_all_field_names():
    #    field = instance._meta.get_field_by_name(field_name)[0]

    #for field_name in klass._meta.get_all_field_names():
    for field in klass._meta._fields():
        #field = klass._meta.get_field_by_name(field_name)[0]

        field_class = field.__class__.__name__

        ext_type = FIELD_TYPES[field_class]

        field_dict = {
            'name': field.name,
            'type': ext_type
        }

        if ext_type == 'date':
            field_dict['dateFormat'] = 'timestamp'

        if hasattr(field, "default"):
            if field.default != NOT_PROVIDED:
                field_dict["defaultValue"] = field.default

        fields.append(field_dict)

        if hasattr(field, "max_length") and field.max_length:
            validators.append({'type': 'length', 'field': field.name, 'max': field.max_length})

        if hasattr(field, "_get_choices"):
            choices = field._get_choices()

            if len(choices):
                validators.append({'type': 'inclusion', 'field': field.name, 'list': [choice[1] for choice in choices]})

        if hasattr(field, "_get_choices") and not field.blank:
            validators.append({'type': 'presence', 'field': field.name})

    model = OrderedDict()
    model['extend'] = 'Ext.data.Model'
    model['fields'] = fields
    model['validations'] = validators

    model_str = """Ext.define('%(model_name)s', %(model)s);""" % {
        'model_name': model_name,
        'model': json.dumps(model, ensure_ascii=False, indent=" " * 4)
    }

    return dejsonize(model_str)