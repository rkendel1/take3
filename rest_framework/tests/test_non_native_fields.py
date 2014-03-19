from django.db import models
from django.test import TestCase
from rest_framework import serializers


class ExampleModel(models.Model):
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)


class ExampleSerializer(serializers.ModelSerializer):
    password_confirmation = serializers.CharField()
    def validate_password_confirmation(self, attrs, source):
        password_confirmation = attrs[source]
        password = attrs['password']
        if password_confirmation != password:
            raise serializers.ValidationError('Password confirmation mismatch')
            attrs.pop(source)
        return attrs
    class Meta:
        model = ExampleModel
        fields = ('email', 'password', 'password_confirmation',)
        write_only_fields = ('password',)
        non_native_fields = ('password_confirmation',)


class NonNativeFieldTests(TestCase):
    def test_non_native_fields(self):
        data = {
            'email': 'foo@example.com',
            'password': '123',
            'password_confirmation': '123',
        }
        serializer = ExampleSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertTrue(isinstance(serializer.object, ExampleModel))
        self.assertEquals(serializer.object.email, data['email'])
        self.assertEquals(serializer.object.password, data['password'])
        self.assertEquals(serializer.data, {'email': 'foo@example.com'})

    def test_non_native_fields_validation_error(self):
        data = {
            'email': 'foo@example.com',
            'password': '123',
            'password_confirmation': 'abc',
        }
        serializer = ExampleSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEquals(len(serializer.errors), 1)
        self.assertEquals(serializer.errors['password_confirmation'],
            ['Password confirmation mismatch'])
