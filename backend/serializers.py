import json
from datetime import datetime, date
from app import db, logger, app
from operator import itemgetter
from sqlalchemy import inspect

API_HOST = app.config["API_HOST"]


class CustomEncoder(json.JSONEncoder):
    """
    Define encoding rules for fields that are not readily serializable.
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            # encoded_obj = obj.strftime("%B %d, %Y, %H:%M")
            encoded_obj = obj.strftime("%Y-%m-%d, %T")
        elif isinstance(obj, date):
            encoded_obj = obj.strftime("%B %d, %Y")
        elif isinstance(obj, db.Model):
            try:
                encoded_obj = json.dumps(obj.to_dict(), cls=CustomEncoder, indent=4)
            except Exception:
                encoded_obj = str(obj)
        else:
            encoded_obj = json.JSONEncoder.default(self, obj)
        return encoded_obj


def model_to_dict(obj, include_related=False):
    """
    Convert a single model object to dict. Nest related resources.
    """

    # attributes from columns
    columns = obj.__mapper__.column_attrs.keys()
    tmp_dict = {
        key: getattr(obj, key) for key in columns
    }

    relations = obj.__mapper__.relationships.keys()
    for key in relations:
        # serialize eagerly loaded related objects, or all related objects if the flag is set
        if include_related or key not in inspect(obj).unloaded:
            related_content = getattr(obj, key)
            if related_content:
                try:
                    tmp_dict[key] = model_to_dict(related_content)
                except AttributeError as e:
                    tmp_dict[key] = []
                    for item in related_content:
                        tmp_dict[key].append(model_to_dict(item))
    return tmp_dict


def to_dict(obj, include_related=False):
    """
    Check if a custom serializer is defined for the given object, otherwise use the default.
    """
    try:
        return obj.to_dict(obj, include_related=include_related)
    except:
        return model_to_dict(obj, include_related=include_related)


def queryset_to_json(obj_or_list, count=None, next=None):
    """
    Convert a single model object, or a list of model objects to dicts, before
    serializing the results as a json string.
    """

    if isinstance(obj_or_list, db.Model):
        logger.debug("single obj")
        obj = obj_or_list
        # this a single object
        out = to_dict(obj, include_related=True)
    else:
        # this is a list of objects
        logger.debug("list of objs")
        results = []
        for obj in obj_or_list:
            results.append(to_dict(obj, include_related=False))
        out = {
            'count': count,
            'next': next,
            'results': results
            }

    return json.dumps(out, cls=CustomEncoder, indent=4)


def organisation_to_dict(obj, include_related=False):


    return model_to_dict(obj, include_related=include_related)