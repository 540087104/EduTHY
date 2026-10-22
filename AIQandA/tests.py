"""AIQandA 应用的单元测试。"""

from django.test import TestCase

from .models import Chapter, Course, QuestionAnswerPair
from .services import AIChatService, MatchResult


class QuestionAnswerPairTest(TestCase):
    """验证问答对模型能正常创建和查询。"""

    def setUp(self):
        """准备测试数据。"""
        self.course = Course.objects.create(name="Linux 基础")
        self.chapter = Chapter.objects.create(course=self.course, title="文件操作", order=1)
        self.qa = QuestionAnswerPair.objects.create(
            chapter=self.chapter,
            question="如何查看当前目录？",
            answer="pwd",
            keywords="目录 pwd",
        )

    def test_qa_created(self):
        """问答对创建后数量与内容正确。"""
        self.assertEqual(QuestionAnswerPair.objects.count(), 1)
        self.assertEqual(self.qa.answer, "pwd")

    def test_str(self):
        """__str__ 返回问题前 50 字。"""
        self.assertIn("如何查看当前目录", str(self.qa))


class AIChatServiceTest(TestCase):
    """验证 AI 匹配引擎的语义匹配能力。"""

    def setUp(self):
        course = Course.objects.create(name="Linux 基础")
        chapter = Chapter.objects.create(course=course, title="文件操作", order=1)
        self.qa = QuestionAnswerPair.objects.create(
            chapter=chapter,
            question="如何查看当前目录？",
            answer="使用 pwd 命令查看当前目录。",
            keywords="查看 当前 目录 pwd 路径",
        )
        self.service = AIChatService()

    def test_exact_question_matches(self):
        """完全相同的问题应命中。"""
        result = self.service.answer("如何查看当前目录？")
        self.assertIsInstance(result, MatchResult)
        self.assertIsNotNone(result.qa)
        self.assertEqual(result.qa.id, self.qa.id)

    def test_synonym_question_matches(self):
        """措辞不同但语义相近的问题也应命中，体现 AI 模糊匹配。"""
        result = self.service.answer("怎么查看当前所在的目录")
        self.assertIsNotNone(result.qa)
        self.assertIn("pwd", result.answer)

    def test_unrelated_question_falls_back(self):
        """完全不相关的问题应走兜底回答。"""
        result = self.service.answer("今天天气怎么样？")
        self.assertIsNone(result.qa)
        self.assertIn("暂时没有找到", result.answer)

    def test_empty_knowledge_base(self):
        """知识库为空时返回提示。"""
        QuestionAnswerPair.objects.all().delete()
        result = self.service.answer("任意问题")
        self.assertIsNone(result.qa)
        self.assertIn("暂无内容", result.answer)
