from django import forms
from .models import Student


class StudentForm(forms.ModelForm):
    def clean_qq(self):
        qq = self.cleaned_data['qq']
        if not qq.isdigit():
            raise forms.ValidationError('必须是数字!')
        return int(qq)

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone.isdigit():
            raise forms.ValidationError('必须是数字')
        return int(phone)

    class Meta:
        model = Student
        fields = (
            'name', 'sex', 'profession', 'email', 'qq', 'phone'
        )
