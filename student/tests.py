from django.test import TestCase
from django.urls import reverse
from .models import Student


# Create your tests here.
class StudentTestCase(TestCase):
    def setUp(self):
        Student.objects.create(
            name='test',
            sex=1,
            email='333@mail.com',
            profession='Coder',
            qq='888888',
            phone='123456'
        )

    def test_create_a_student(self):
        student = Student.objects.all()[0]
        student_name = '<Student: test>'
        self.assertEqual(str(student), student_name)

    def test_filter(self):
        students = Student.objects.filter(name='test')
        self.assertEqual(students.count(), 1)

    def test_get_index(self):
        response = self.client.get(reverse('student:index'))
        self.assertEqual(response.status_code, 200)

    def test_post_student(self):
        data = {
            'name': 'tester',
            'sex': 1,
            'email': '123@qq.com',
            'profession': 'coder',
            'qq': '1234',
            'phone': '123456'
        }
        response = self.client.post(reverse('student:index'), data)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('student:index'))
        self.assertTrue(b'tester' in response.content)