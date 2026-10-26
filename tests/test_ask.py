from types import SimpleNamespace

from app import ask as ask_module


def test_main_keeps_chat_history_for_follow_up_questions(monkeypatch, capsys):
    class FakeChat:
        def __init__(self):
            self.questions = []

        def send_message(self, question):
            self.questions.append(question)
            return SimpleNamespace(text=f"回答: {question}", usage_metadata=None)

    chat = FakeChat()

    class FakeChats:
        def create(self, *, model):
            assert model == ask_module.MODEL
            return chat

    class FakeClient:
        chats = FakeChats()

        def __init__(self, *, api_key):
            assert api_key == "test-key"

    monkeypatch.setattr("sys.argv", ["app.ask", "最初の質問"])
    questions = iter(["続きの質問", ""])
    monkeypatch.setattr("builtins.input", lambda _: next(questions))
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    monkeypatch.setattr(ask_module.genai, "Client", FakeClient)

    ask_module.main()

    assert chat.questions == ["最初の質問", "続きの質問"]
    assert "回答: 最初の質問" in capsys.readouterr().out
