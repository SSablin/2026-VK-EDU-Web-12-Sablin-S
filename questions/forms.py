from django import forms

from questions.models import Answer, Question, QuestionTag, Tag


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(max_length=300, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Question
        fields = ['title', 'text', 'tags']
        labels = {
            'title': 'Title',
            'text': 'Text question',
            'tags': 'Tags',
        }

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

    def save(self, user, commit=True):
        question = super().save(commit=False)
        question.user = user
        if commit:
            question.save()
            tags = self.cleaned_data.get('tags', '')
            for tag_title in tags.split(','):
                tag_title = tag_title.strip()
                if tag_title:
                    tag, created = Tag.objects.get_or_create(title=tag_title)
                    QuestionTag.objects.get_or_create(question=question, tag=tag)
        return question

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
