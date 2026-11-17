from django.contrib import admin
from questions.models import (
    Question, Answer, Tag, QuestionTag,
    QuestionLike, AnswerLike
)


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    raw_id_fields = ("user",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


class QuestionTagInline(admin.TabularInline):
    model = QuestionTag
    extra = 0
    raw_id_fields = ("tag",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('tag')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("title", "text", "user__username")
    inlines = (AnswerInline, QuestionTagInline)
    raw_id_fields = ("user",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "user", "is_correct", "created_at")
    list_filter = ("is_correct", "created_at")
    search_fields = ("text", "user__username", "question__title")
    raw_id_fields = ("user", "question")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'question')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    list_filter = ("created_at",)
    search_fields = ("title",)



@admin.register(QuestionTag)
class QuestionTagAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "tag")
    list_filter = ("tag",)
    search_fields = ("question__title", "tag__title")
    raw_id_fields = ("question", "tag")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('question', 'tag')


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "user", "is_like", "created_at")
    list_filter = ("is_like", "created_at")
    search_fields = ("question__title", "user__username")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('question', 'user')


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ("id", "answer", "user", "is_like", "created_at")
    list_filter = ("is_like", "created_at")
    search_fields = ("answer__text", "user__username")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('answer', 'user')