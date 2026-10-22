"""向知识库灌入示例课程与问答对，便于演示。

用法：python manage.py seed_data
"""

from django.core.management.base import BaseCommand

from AIQandA.models import Chapter, Course, QuestionAnswerPair


SAMPLE_DATA = [
    {
        "course": "Linux 基础",
        "chapters": [
            {
                "title": "文件与目录操作",
                "order": 1,
                "qas": [
                    {
                        "question": "如何查看当前所在目录？",
                        "answer": "使用 pwd 命令，它会打印当前工作目录的完整路径。",
                        "keywords": "查看,当前,目录,pwd,路径",
                    },
                    {
                        "question": "怎样列出目录下的文件？",
                        "answer": "使用 ls 命令；加 -l 显示详细信息，加 -a 显示隐藏文件。",
                        "keywords": "列出,文件,目录,ls,隐藏",
                    },
                    {
                        "question": "如何切换到其他目录？",
                        "answer": "使用 cd 命令，例如 cd /etc 切换到 /etc 目录，cd .. 返回上一级。",
                        "keywords": "切换,目录,cd,进入",
                    },
                    {
                        "question": "怎么创建一个新目录？",
                        "answer": "使用 mkdir 命令，例如 mkdir mydir 创建名为 mydir 的目录。",
                        "keywords": "创建,目录,新建,mkdir",
                    },
                    {
                        "question": "如何删除一个文件？",
                        "answer": "使用 rm 命令，例如 rm file.txt；删除目录用 rm -r dir。",
                        "keywords": "删除,文件,rm,目录",
                    },
                ],
            },
            {
                "title": "文件内容查看",
                "order": 2,
                "qas": [
                    {
                        "question": "怎样查看文件的全部内容？",
                        "answer": "使用 cat 命令，例如 cat file.txt 会把文件内容输出到终端。",
                        "keywords": "查看,内容,cat,文件",
                    },
                    {
                        "question": "如何分页查看大文件？",
                        "answer": "使用 less 或 more 命令，例如 less bigfile.txt，按 q 退出。",
                        "keywords": "分页,大文件,less,more",
                    },
                ],
            },
        ],
    },
]


class Command(BaseCommand):
    help = "灌入示例课程与问答对数据"

    def handle(self, *args, **options):
        for course_data in SAMPLE_DATA:
            course, _ = Course.objects.get_or_create(
                name=course_data["course"],
                defaults={"description": "Linux 系统基础课程示例"},
            )
            for ch_data in course_data["chapters"]:
                chapter, _ = Chapter.objects.get_or_create(
                    course=course,
                    title=ch_data["title"],
                    defaults={"order": ch_data["order"]},
                )
                for qa_data in ch_data["qas"]:
                    QuestionAnswerPair.objects.get_or_create(
                        chapter=chapter,
                        question=qa_data["question"],
                        defaults={
                            "answer": qa_data["answer"],
                            "keywords": qa_data["keywords"],
                        },
                    )
        self.stdout.write(self.style.SUCCESS("示例数据已灌入完成。"))
