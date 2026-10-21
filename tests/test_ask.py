from types import SimpleNamespace

from app import ask as ask_module


def test_main_keeps_chat_history_for_follow_up_questions(monkeypatch, capsys):
    class FakeChat:
        def __init__(self):
            self.questions = []

        def send_message(self, question):
            self.questions.append(question)
            return SimpleNamespace(text=f"回答: {question}", usage_metadata=None)

    class FakeClient:
        def __init__(self):
            self.chat = FakeChat()
            self.chats = SimpleNamespace(create=lambda model: self.chat)

    client = FakeClient()
    monkeypatch.setattr(ask_module.genai, "Client", lambda api_key: client)
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    monkeypatch.setattr("sys.argv", ["app.ask", "最初の質問"])
    questions = iter(["続きの質問", ""])
    monkeypatch.setattr("builtins.input", lambda prompt: next(questions))

    ask_module.main()

    assert client.chat.questions == ["最初の質問", "続きの質問"]
    assert "回答: 続きの質問" in capsys.readouterr().out