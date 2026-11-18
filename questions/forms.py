from django import forms

from questions.models import Answer


class QuestionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    title = forms.CharField(max_length=200, required=True)
    text = forms.CharField(widget=forms.Textarea, required=True)

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise forms.ValidationError("This field is required.")
        return title

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if not text:
            raise forms.ValidationError("This field is required.")
        return text

    def save(self, user):
        data = self.cleaned_data.copy()
        data['author'] = user
        from questions.models import Question
        return Question.objects.create(**data)

class AnswerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Answer
        fields = ['text']
        labels = {
            'text': 'Your answer',
        }

    def save(self, user, question, commit=True):
        answer = super().save(commit=False)
        answer.user = user
        answer.question = question
        answer.is_correct = False
        if commit:
            answer.save()
        return answer
