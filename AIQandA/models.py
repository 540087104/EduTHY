from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    name = models.CharField(max_length=100, verbose_name="课程名称")
    description = models.TextField(blank=True, verbose_name="课程描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "课程"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Chapter(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="chapters", verbose_name="所属课程"
    )
    title = models.CharField(max_length=200, verbose_name="章节标题")
    order = models.IntegerField(default=0, verbose_name="章节顺序")
    content = models.TextField(blank=True, verbose_name="章节内容")

    class Meta:
        ordering = ["order"]
        verbose_name = "章节"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.course.name} - {self.title}"


class QuestionAnswerPair(models.Model):
    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE, related_name="qa_pairs", verbose_name="所属章节"
    )
    question = models.TextField(verbose_name="标准问题")
    answer = models.TextField(verbose_name="标准答案")
    keywords = models.CharField(max_length=255, blank=True, verbose_name="关键词")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")

    class Meta:
        verbose_name = "问答对"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.question[:50]


class ChatHistory(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chat_history",
        verbose_name="用户",
        null=True,
        blank=True,
    )
    session_key = models.CharField(max_length=40, verbose_name="会话标识")
    question = models.TextField(verbose_name="用户提问")
    matched_qa = models.ForeignKey(
        QuestionAnswerPair,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="命中问答对",
    )
    answer = models.TextField(blank=True, verbose_name="系统回答")
    is_helpful = models.BooleanField(null=True, blank=True, verbose_name="是否有帮助")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="提问时间")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "对话历史"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user.username}: {self.question[:30]}"
