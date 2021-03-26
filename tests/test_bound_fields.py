import pytest
from django.http import QueryDict

from rest_framework import serializers


class TestSimpleBoundField:
    def test_empty_bound_field(self):
        class ExampleSerializer(serializers.Serializer):
            text = serializers.CharField(max_length=100)
            amount = serializers.IntegerField()

        serializer = ExampleSerializer()

        assert serializer['text'].value == ''
        assert serializer['text'].errors is None
        assert serializer['text'].name == 'text'
        assert serializer['amount'].value is None
        assert serializer['amount'].errors is None
        assert serializer['amount'].name == 'amount'

    def test_populated_bound_field(self):
        class ExampleSerializer(serializers.Serializer):
            text = serializers.CharField(max_length=100)
            amount = serializers.IntegerField()

        serializer = ExampleSerializer(data={'text': 'abc', 'amount': 123})
        assert serializer.is_valid()
        assert serializer['text'].value == 'abc'
        assert serializer['text'].errors is None
        assert serializer['text'].name == 'text'
        assert serializer['amount'].value == 123
        assert serializer['amount'].errors is None
        assert serializer['amount'].name == 'amount'

    def test_error_bound_field(self):
        class ExampleSerializer(serializers.Serializer):
            text = serializers.CharField(max_length=100)
            amount = serializers.IntegerField()

        serializer = ExampleSerializer(data={'text': 'x' * 1000, 'amount': 123})
        serializer.is_valid()

        assert serializer['text'].value == 'x' * 1000
        assert serializer['text'].errors == ['Ensure this field has no more than 100 characters.']
        assert serializer['text'].name == 'text'
        assert serializer['amount'].value == 123
        assert serializer['amount'].errors is None
        assert serializer['amount'].name == 'amount'

    def test_delete_field(self):
        class ExampleSerializer(serializers.Serializer):
            text = serializers.CharField(max_length=100)
            amount = serializers.IntegerField()

        serializer = ExampleSerializer()
        del serializer.fields['text']
        assert 'text' not in serializer.fields

    def test_as_form_fields(self):
        class ExampleSerializer(serializers.Serializer):
            bool_field = serializers.BooleanField()
            nullable_bool_field = serializers.BooleanField(allow_null=True)
            null_field = serializers.IntegerField(allow_null=True)

        serializer = ExampleSerializer(data={'bool_field': False, 'nullable_bool_field': False, 'null_field': None})
        assert serializer.is_valid()
        assert serializer['bool_field'].as_form_field().value == ''
        assert serializer['nullable_bool_field'].as_form_field().value is False
        assert serializer['null_field'].as_form_field().value == ''

    def test_rendering_boolean_field(self):
        from rest_framework.renderers import HTMLFormRenderer

        class ExampleSerializer(serializers.Serializer):
            bool_field = serializers.BooleanField(
                style={'base_template': 'checkbox.html', 'template_pack': 'rest_framework/vertical'})

        serializer = ExampleSerializer(data={'bool_field': True})
        assert serializer.is_valid()
        renderer = HTMLFormRenderer()
        rendered = renderer.render_field(serializer['bool_field'], {})
        expected_packed = (
            '<divclass="form-group">'
            '<divclass="checkbox">'
            '<label>'
            '<inputtype="checkbox"name="bool_field"value="true"checked>'
            'Boolfield'
            '</label>'
            '</div>'
            '</div>'
        )
        rendered_packed = ''.join(rendered.split())
        assert rendered_packed == expected_packed

    @pytest.mark.parametrize('bool_field_value', [True, False, None])
    def test_rendering_nullable_boolean_field(self, bool_field_value):
        from rest_framework.renderers import HTMLFormRenderer

        class ExampleSerializer(serializers.Serializer):
            bool_field = serializers.BooleanField(
                allow_null=True,
                style={'base_template': 'select_boolean.html', 'template_pack': 'rest_framework/vertical'})

        serializer = ExampleSerializer(data={'bool_field': bool_field_value})
        assert serializer.is_valid()
        renderer = HTMLFormRenderer()
        rendered = renderer.render_field(serializer['bool_field'], {})
        if bool_field_value is True:
            expected_packed = (
                '<divclass="form-group">'
                '<label>Boolfield</label>'
                '<selectclass="form-control"name="bool_field">'
                '<optionvalue="">Unknown</option>'
                '<optionvalue="True"selected>Yes</option>'
                '<optionvalue="False">No</option>'
                '</select>'
                '</div>'
            )
        elif bool_field_value is False:
            expected_packed = (
                '<divclass="form-group">'
                '<label>Boolfield</label>'
                '<selectclass="form-control"name="bool_field">'
                '<optionvalue="">Unknown</option>'
                '<optionvalue="True">Yes</option>'
                '<optionvalue="False"selected>No</option>'
                '</select>'
                '</div>'
            )
        elif bool_field_value is None:
            expected_packed = (
                '<divclass="form-group">'
                '<label>Boolfield</label>'
                '<selectclass="form-control"name="bool_field">'
                '<optionvalue=""selected>Unknown</option>'
                '<optionvalue="True">Yes</option>'
                '<optionvalue="False">No</option>'
                '</select>'
                '</div>'
            )
        rendered_packed = ''.join(rendered.split())
        assert rendered_packed == expected_packed


class CustomJSONField(serializers.JSONField):
    pass


class TestNestedBoundField:
    def test_nested_empty_bound_field(self):
        class Nested(serializers.Serializer):
            more_text = serializers.CharField(max_length=100)
            amount = serializers.IntegerField()

        class ExampleSerializer(serializers.Serializer):
            text = serializers.CharField(max_length=100)
            nested = Nested()

        serializer = ExampleSerializer()

        assert serializer['text'].value == ''
        assert serializer['text'].errors is None
        assert serializer['text'].name == 'text'
        assert serializer['nested']['more_text'].value == ''
        assert serializer['nested']['more_text'].errors is None
        assert serializer['nested']['more_text'].name == 'nested.more_text'
        assert serializer['nested']['amount'].value is None
        assert serializer['nested']['amount'].errors is None
        assert serializer['nested']['amount'].name == 'nested.amount'

    def test_as_form_fields(self):
        class Nested(serializers.Serializer):
            bool_field = serializers.BooleanField()
            nullable_bool_field = serializers.BooleanField(allow_null=True)
            null_field = serializers.IntegerField(allow_null=True)
            json_field = serializers.JSONField()
            custom_json_field = CustomJSONField()

        class ExampleSerializer(serializers.Serializer):
            nested = Nested()

        serializer = ExampleSerializer(
            data={'nested': {
                'bool_field': False, 'nullable_bool_field': False, 'null_field': None,
                'json_field': {'bool_item': True, 'number': 1, 'text_item': 'text'},
                'custom_json_field': {'bool_item': True, 'number': 1, 'text_item': 'text'},
            }})
        assert serializer.is_valid()
        assert serializer['nested']['bool_field'].as_form_field().value == ''
        assert serializer['nested']['nullable_bool_field'].as_form_field().value is False
        assert serializer['nested']['null_field'].as_form_field().value == ''
        assert serializer['nested']['json_field'].as_form_field().value == '''{
    "bool_item": true,
    "number": 1,
    "text_item": "text"
}'''
        assert serializer['nested']['custom_json_field'].as_form_field().value == '''{
    "bool_item": true,
    "number": 1,
    "text_item": "text"
}'''

    def test_rendering_nested_fields_with_none_value(self):
        from rest_framework.renderers import HTMLFormRenderer

        class Nested1(serializers.Serializer):
            text_field = serializers.CharField()

        class Nested2(serializers.Serializer):
            nested1 = Nested1(allow_null=True)
            text_field = serializers.CharField()

        class ExampleSerializer(serializers.Serializer):
            nested2 = Nested2()

        serializer = ExampleSerializer(data={'nested2': {'nested1': None, 'text_field': 'test'}})
        assert serializer.is_valid()
        renderer = HTMLFormRenderer()
        for field in serializer:
            rendered = renderer.render_field(field, {})
            expected_packed = (
                '<fieldset>'
                '<legend>Nested2</legend>'
                '<fieldset>'
                '<legend>Nested1</legend>'
                '<divclass="form-group">'
                '<label>Textfield</label>'
                '<inputname="nested2.nested1.text_field"class="form-control"type="text"value="">'
                '</div>'
                '</fieldset>'
                '<divclass="form-group">'
                '<label>Textfield</label>'
                '<inputname="nested2.text_field"class="form-control"type="text"value="test">'
                '</div>'
                '</fieldset>'
            )
            rendered_packed = ''.join(rendered.split())
            assert rendered_packed == expected_packed

    def test_rendering_nested_fields_with_not_mappable_value(self):
        from rest_framework.renderers import HTMLFormRenderer

        class Nested(serializers.Serializer):
            text_field = serializers.CharField()

        class ExampleSerializer(serializers.Serializer):
            nested = Nested()

        serializer = ExampleSerializer(data={'nested': 1})
        assert not serializer.is_valid()
        renderer = HTMLFormRenderer()
        for field in serializer:
            rendered = renderer.render_field(field, {})
            expected_packed = (
                '<fieldset>'
                '<legend>Nested</legend>'
                '<divclass="form-group">'
                '<label>Textfield</label>'
                '<inputname="nested.text_field"class="form-control"type="text"value="">'
                '</div>'
                '</fieldset>'
            )

            rendered_packed = ''.join(rendered.split())
            assert rendered_packed == expected_packed


class TestJSONBoundField:
    def test_as_form_fields(self):
        class TestSerializer(serializers.Serializer):
            json_field = serializers.JSONField()

        data = QueryDict(mutable=True)
        data.update({'json_field': '{"some": ["json"}'})
        serializer = TestSerializer(data=data)
        assert serializer.is_valid() is False
        assert serializer['json_field'].as_form_field().value == '{"some": ["json"}'
