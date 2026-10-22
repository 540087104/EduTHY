"""AIQandA 视图层：提供聊天页面与提问接口。"""

from __future__ import annotations

import json
import uuid

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import ChatHistory
from .services import AIChatService


def index(request: HttpRequest) -> HttpResponse:
    """聊天首页。"""
    return render(request, "AIQandA/chat.html")


@csrf_exempt
@require_http_methods(["POST"])
def ask(request: HttpRequest) -> JsonResponse:
    """接收用户提问，调用 AI 匹配引擎并返回回答。

    请求体：{"question": "如何查看当前目录？"}
    响应体：{"answer": "...", "matched": true, "score": 0.83}
    """
    try:
        data = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "请求体不是合法 JSON"}, status=400)

    question = (data.get("question") or "").strip()
    if not question:
        return JsonResponse({"error": "问题不能为空"}, status=400)

    service = AIChatService()
    result = service.answer(question)

    # 记录对话历史（允许匿名用户）
    ChatHistory.objects.create(
        user=request.user if request.user.is_authenticated else None,
        session_key=_get_or_create_session(request),
        question=question,
        matched_qa=result.qa,
        answer=result.answer,
    )

    return JsonResponse(
        {
            "answer": result.answer,
            "matched": result.qa is not None,
            "score": round(result.score, 4),
            "chapter": result.qa.chapter.title if result.qa else None,
        }
    )


def _get_or_create_session(request: HttpRequest) -> str:
    """为匿名/登录用户维护一个会话标识。"""
    session_key = request.session.get("ai_chat_session")
    if not session_key:
        session_key = uuid.uuid4().hex
        request.session["ai_chat_session"] = session_key
    return session_key
