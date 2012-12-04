import copy
import datetime
import types
from decimal import Decimal
from django.db import models
from django.forms import widgets
from django.utils.datastructures import SortedDict
from django.core.exceptions import ImproperlyConfigured
from rest_framework.compat import get_concrete_model, empty

# Note: We do the following so that users of the framework can use this style:
#
#     example_field = serializers.CharField(...)
#
# This helps keep the seperation between model fields, form fields, and
# serializer fields more explicit.


from rest_framework.fields import *


class DictWithMetadata(dict):
    """
    A dict-like object, that can have additional properties attached.
    """
    pass


class SortedDictWithMetadata(SortedDict, DictWithMetadata):
    """
    A sorted dict-like object, that can have additional properties attached.
    """
    pass


def _is_protected_type(obj):
    """
    True if the object is a native datatype that does not need to
    be serialized further.
    """
    return isinstance(obj, (
        types.NoneType,
        int, long,
        datetime.datetime, datetime.date, datetime.time,
        float, Decimal,
        basestring)
    )


def _get_declared_fields(bases, attrs):
    """
    Create a list of serializer field instances from the passed in 'attrs',
    plus any fields on the base classes (in 'bases').

    Note that all fields from the base classes are used.
    """
    fields = [(field_name, attrs.pop(field_name))
              for field_name, obj in attrs.items()
              if isinstance(obj, Field)]
    fields.sort(key=lambda x: x[1].creation_counter)

    # If this class is subclassing another Serializer, add that Serializer's
    # fields.  Note that we loop over the bases in *reverse*. This is necessary
    # in order to maintain the correct order of fields.
    for base in bases[::-1]:
        if hasattr(base, 'base_fields'):
            fields = base.base_fields.items() + fields

    return SortedDict(fields)

def _get_options_instance(bases, attrs):
    options_class = Meta = empty
    if '_options_class' in attrs:
        options_class = attrs['_options_class']
    else:
        for base in bases:
            if hasattr(base, '_options_class'):
                options_class = getattr(base, '_options_class')
                break
        if options_class is empty:
            raise ImproperlyConfigured, 'A Serializer requires an "_options_class" attribute' 
            
    if 'Meta' in attrs:
        Meta = attrs['Meta']
    else:
        for base in bases:
            if hasattr(base, 'Meta'):
                Meta = getattr(base, 'Meta')
                break
        if Meta is empty:
            raise ImproperlyConfigured, 'A Serializer requires an "Meta" attribute' 
    
    return options_class(Meta)

class SerializerMetaclass(type):
    def __new__(cls, name, bases, attrs):
        attrs['base_fields'] = _get_declared_fields(bases, attrs)
        attrs['opts'] = _get_options_instance(bases, attrs)
        return super(SerializerMetaclass, cls).__new__(cls, name, bases, attrs)


class SerializerOptions(object):
    """
    Meta class options for Serializer
    """
    def __init__(self, meta):
        self.depth = getattr(meta, 'depth', 0)
        self.fields = getattr(meta, 'fields', ())
        self.exclude = getattr(meta, 'exclude', ())


class BaseSerializer(Field):
    class Meta(object):
        pass

    _options_class = SerializerOptions
    _dict_class = SortedDictWithMetadata  # Set to unsorted dict for backwards compatibility with unsorted implementations.

    def __init__(self, instance=None, data=None, files=None, context=None, partial=False, **kwargs):
        super(BaseSerializer, self).__init__(**kwargs)
        self.parent = None
        self.root = None
        self.partial = partial

        self.context = context or {}

        self.init_data = data
        self.init_files = files
        self.object = instance
        self.fields = self.get_fields()

        self._data = None
        self._files = None
        self._errors = None

    #####
    # Methods to determine which fields to use when (de)serializing objects.

    def get_default_fields(self):
        """
        Return the complete set of default fields for the object, as a dict.
        """
        return {}

    def get_fields(self):
        """
        Returns the complete set of fields for the object as a dict.

        This will be the set of any explicitly declared fields,
        plus the set of fields returned by get_default_fields().
        """
        ret = SortedDict()

        # Get the explicitly declared fields
        base_fields = copy.deepcopy(self.base_fields)
        for key, field in base_fields.items():
            ret[key] = field
            # Set up the field
            field.initialize(parent=self, field_name=key)

        # Add in the default fields
        default_fields = self.get_default_fields()
        for key, val in default_fields.items():
            if key not in ret:
                ret[key] = val

        # If 'fields' is specified, use those fields, in that order.
        if self.opts.fields:
            new = SortedDict()
            for key in self.opts.fields:
                new[key] = ret[key]
            ret = new

        # Remove anything in 'exclude'
        if self.opts.exclude:
            for key in self.opts.exclude:
                ret.pop(key, None)

        return ret

    #####
    # Field methods - used when the serializer class is itself used as a field.

    def initialize(self, parent, field_name):
        """
        Same behaviour as usual Field, except that we need to keep track
        of state so that we can deal with handling maximum depth.
        """
        super(BaseSerializer, self).initialize(parent, field_name)
        if parent.opts.depth:
            self.opts.depth = parent.opts.depth - 1

    #####
    # Methods to convert or revert from objects <--> primitive representations.

    def get_field_key(self, field_name):
        """
        Return the key that should be used for a given field.
        """
        return field_name

    def convert_object(self, obj):
        """
        Core of serialization.
        Convert an object into a dictionary of serialized field values.
        """
        ret = self._dict_class()
        ret.fields = {}

        for field_name, field in self.fields.items():
            key = self.get_field_key(field_name)
            value = field.field_to_native(obj, field_name)
            ret[key] = value
            ret.fields[key] = field
        return ret

    def restore_fields(self, data, files):
        """
        Core of deserialization, together with `restore_object`.
        Converts a dictionary of data into a dictionary of deserialized fields.
        """
        reverted_data = {}
        for field_name, field in self.fields.items():
            try:
                field.field_from_native(data, files, field_name, reverted_data)
            except ValidationError as err:
                self._errors[field_name] = list(err.messages)

        return reverted_data

    def perform_validation(self, attrs):
        """
        Run `validate_<fieldname>()` and `validate()` methods on the serializer
        """
        for field_name, field in self.fields.items():
            try:
                validate_method = getattr(self, 'validate_%s' % field_name, None)
                if validate_method:
                    source = field.source or field_name
                    attrs = validate_method(attrs, source)
            except ValidationError as err:
                self._errors[field_name] = self._errors.get(field_name, []) + list(err.messages)

        try:
            attrs = self.validate(attrs)
        except ValidationError as err:
            self._errors['non_field_errors'] = err.messages

        return attrs

    def validate(self, attrs):
        """
        Stub method, to be overridden in Serializer subclasses
        """
        return attrs

    def restore_object(self, attrs, instance=None):
        """
        Deserialize a dictionary of attributes into an object instance.
        You should override this method to control how deserialized objects
        are instantiated.
        """
        if instance is not None:
            instance.update(attrs)
            return instance
        return attrs

    def to_native(self, obj):
        """
        Serialize objects -> primitives.
        """
        if hasattr(obj, '__iter__'):
            return [self.convert_object(item) for item in obj]
        return self.convert_object(obj)

    def from_native(self, data, files):
        """
        Deserialize primitives -> objects.
        """
        if hasattr(data, '__iter__') and not isinstance(data, dict):
            # TODO: error data when deserializing lists
            return (self.from_native(item) for item in data)

        self._errors = {}
        if data is not None or files is not None:
            attrs = self.restore_fields(data, files)
            attrs = self.perform_validation(attrs)
        else:
            self._errors['non_field_errors'] = ['No input provided']

        if not self._errors:
            return self.restore_object(attrs, instance=getattr(self, 'object', None))

    def field_to_native(self, obj, field_name):
        """
        Override default so that we can apply ModelSerializer as a nested
        field to relationships.
        """
        obj = getattr(obj, self.source or field_name)

        if is_simple_callable(obj):
            obj = obj()

        # If the object has an "all" method, assume it's a relationship
        if is_simple_callable(getattr(obj, 'all', None)):
            return [self.to_native(item) for item in obj.all()]

        return self.to_native(obj)

    @property
    def errors(self):
        """
        Run deserialization and return error data,
        setting self.object if no errors occurred.
        """
        if self._errors is None:
            obj = self.from_native(self.init_data, self.init_files)
            if not self._errors:
                self.object = obj
        return self._errors

    def is_valid(self):
        return not self.errors

    @property
    def data(self):
        if self._data is None:
            self._data = self.to_native(self.object)
        return self._data

    def save(self):
        """
        Save the deserialized object and return it.
        """
        self.object.save()
        return self.object


class Serializer(BaseSerializer):
    __metaclass__ = SerializerMetaclass


class ModelSerializerOptions(SerializerOptions):
    """
    Meta class options for ModelSerializer
    """
    def __init__(self, meta):
        super(ModelSerializerOptions, self).__init__(meta)
        self.model = getattr(meta, 'model', None)
        self.read_only_fields = getattr(meta, 'read_only_fields', ())


class ModelSerializer(Serializer):
    """
    A serializer that deals with model instances and querysets.
    """
    _options_class = ModelSerializerOptions

    def get_default_fields(self):
        """
        Return all the fields that should be serialized for the model.
        """

        cls = self.opts.model
        opts = get_concrete_model(cls)._meta
        pk_field = opts.pk
        while pk_field.rel:
            pk_field = pk_field.rel.to._meta.pk
        fields = [pk_field]
        fields += [field for field in opts.fields if field.serialize]
        fields += [field for field in opts.many_to_many if field.serialize]

        ret = SortedDict()
        nested = bool(self.opts.depth)
        is_pk = True  # First field in the list is the pk

        for model_field in fields:
            if is_pk:
                field = self.get_pk_field(model_field)
                is_pk = False
            elif model_field.rel and nested:
                field = self.get_nested_field(model_field)
            elif model_field.rel:
                to_many = isinstance(model_field,
                                     models.fields.related.ManyToManyField)
                field = self.get_related_field(model_field, to_many=to_many)
            else:
                field = self.get_field(model_field)

            if field:
                field.initialize(parent=self, field_name=model_field.name)
                ret[model_field.name] = field

        for field_name in self.opts.read_only_fields:
            assert field_name in ret, \
                "read_only_fields on '%s' included invalid item '%s'" % \
                (self.__class__.__name__, field_name)
            ret[field_name].read_only = True

        return ret

    def get_pk_field(self, model_field):
        """
        Returns a default instance of the pk field.
        """
        return Field()

    def get_nested_field(self, model_field):
        """
        Creates a default instance of a nested relational field.
        """
        class NestedModelSerializer(ModelSerializer):
            class Meta:
                model = model_field.rel.to
        return NestedModelSerializer()

    def get_related_field(self, model_field, to_many=False):
        """
        Creates a default instance of a flat relational field.
        """
        # TODO: filter queryset using:
        # .using(db).complex_filter(self.rel.limit_choices_to)
        queryset = model_field.rel.to._default_manager
        if to_many:
            return ManyPrimaryKeyRelatedField(queryset=queryset)
        return PrimaryKeyRelatedField(queryset=queryset)

    def get_field(self, model_field):
        """
        Creates a default instance of a basic non-relational field.
        """
        kwargs = {}

        kwargs['blank'] = model_field.blank

        if model_field.null:
            kwargs['required'] = False

        if model_field.has_default():
            kwargs['required'] = False
            kwargs['default'] = model_field.get_default()

        if model_field.__class__ == models.TextField:
            kwargs['widget'] = widgets.Textarea

        # TODO: TypedChoiceField?
        if model_field.flatchoices:  # This ModelField contains choices
            kwargs['choices'] = model_field.flatchoices
            return ChoiceField(**kwargs)

        max_length = getattr(model_field, 'max_length', None)
        if max_length:
            kwargs['max_length'] = max_length

        field_mapping = {
            models.FloatField: FloatField,
            models.IntegerField: IntegerField,
            models.PositiveIntegerField: IntegerField,
            models.SmallIntegerField: IntegerField,
            models.PositiveSmallIntegerField: IntegerField,
            models.DateTimeField: DateTimeField,
            models.DateField: DateField,
            models.EmailField: EmailField,
            models.CharField: CharField,
            models.URLField: URLField,
            models.SlugField: SlugField,
            models.TextField: CharField,
            models.CommaSeparatedIntegerField: CharField,
            models.BooleanField: BooleanField,
            models.FileField: FileField,
            models.ImageField: ImageField,
        }
        try:
            return field_mapping[model_field.__class__](**kwargs)
        except KeyError:
            return ModelField(model_field=model_field, **kwargs)

    def restore_object(self, attrs, instance=None):
        """
        Restore the model instance.
        """
        self.m2m_data = {}

        if instance is not None:
            for key, val in attrs.items():
                setattr(instance, key, val)
            return instance

        # Reverse relations
        for (obj, model) in self.opts.model._meta.get_all_related_m2m_objects_with_model():
            field_name = obj.field.related_query_name()
            if field_name in attrs:
                self.m2m_data[field_name] = attrs.pop(field_name)

        # Forward relations
        for field in self.opts.model._meta.many_to_many:
            if field.name in attrs:
                self.m2m_data[field.name] = attrs.pop(field.name)
        return self.opts.model(**attrs)

    def save(self, save_m2m=True):
        """
        Save the deserialized object and return it.
        """
        self.object.save()

        if getattr(self, 'm2m_data', None) and save_m2m:
            for accessor_name, object_list in self.m2m_data.items():
                setattr(self.object, accessor_name, object_list)
            self.m2m_data = {}

        return self.object


class HyperlinkedModelSerializerOptions(ModelSerializerOptions):
    """
    Options for HyperlinkedModelSerializer
    """
    def __init__(self, meta):
        super(HyperlinkedModelSerializerOptions, self).__init__(meta)
        self.view_name = getattr(meta, 'view_name', None)
        self.view_namespace = getattr(meta, 'view_namespace', None)


class HyperlinkedModelSerializer(ModelSerializer):
    """
    """
    _options_class = HyperlinkedModelSerializerOptions
    _default_view_name = '%(model_name)s-detail'

    def __init__(self, *args, **kwargs):
        if self.opts.view_name is None:
            self.opts.view_name = self._get_default_view_name(self.opts.model)
            
        self.base_fields.insert(0, 'url', HyperlinkedIdentityField(view_name=self.opts.view_name, view_namespace=self.opts.view_namespace))
        
        super(HyperlinkedModelSerializer, self).__init__(*args, **kwargs)

    def _get_default_view_name(self, model):
        """
        Return the view name to use if 'view_name' is not specified in 'Meta'
        """
        model_meta = model._meta
        format_kwargs = {
            'app_label': model_meta.app_label,
            'model_name': model_meta.object_name.lower()
        }
        return self._default_view_name % format_kwargs

    def get_pk_field(self, model_field):
        return None

    def get_related_field(self, model_field, to_many):
        """
        Creates a default instance of a flat relational field.
        """
        # TODO: filter queryset using:
        # .using(db).complex_filter(self.rel.limit_choices_to)
        rel = model_field.rel.to
        queryset = rel._default_manager
        kwargs = {
            'queryset': queryset,
            'view_name': self._get_default_view_name(rel)
        }
        if to_many:
            return ManyHyperlinkedRelatedField(**kwargs)
        return HyperlinkedRelatedField(**kwargs)
