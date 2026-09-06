"""Минимальное desktop-приложение: диалог разрешения уведомлений."""

import tkinter as tk


class DecisionApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Mantoz — уведомления")
        self.root.geometry("760x420+80+80")
        self.root.configure(bg="#f4f1ea")
        self.decision: str | None = None

        tk.Label(
            self.root,
            text="Разрешить уведомления?",
            font=("DejaVu Sans", 22, "bold"),
            bg="#f4f1ea",
        ).pack(pady=(70, 20))
        tk.Label(
            self.root,
            text="Приложение будет сообщать о важных событиях.",
            font=("DejaVu Sans", 13),
            bg="#f4f1ea",
        ).pack(pady=(0, 45))

        row = tk.Frame(self.root, bg="#f4f1ea")
        row.pack()
        self.buttons: dict[str, tk.Button] = {}
        for value, label in (
            ("deny", "Запретить"),
            ("later", "Позже"),
            ("allow", "Разрешить"),
        ):
            button = tk.Button(
                row,
                text=label,
                width=15,
                font=("DejaVu Sans", 12),
                command=lambda choice=value: self.choose(choice),
            )
            button.pack(side="left", padx=10)
            self.buttons[value] = button

        self.status = tk.Label(
            self.root, text="", font=("DejaVu Sans", 13, "bold"), bg="#f4f1ea"
        )
        self.status.pack(pady=35)

    def choose(self, decision: str) -> None:
        self.decision = decision
        self.status.configure(text=f"Решение: {decision}")
