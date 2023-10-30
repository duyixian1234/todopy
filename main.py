from typing import Annotated
import uuid
from fastapi import Depends, FastAPI, Form
from fastapi.responses import HTMLResponse
from html_dsl.elements import BaseHtmlElement
from html_dsl.common import (
    H1,
    DIV,
    UL,
    LI,
    SPAN,
    BUTTON,
    HTML,
    HEAD,
    TITLE,
    SCRIPT,
    BODY,
    META,
    FORM,
    INPUT,
    STYLE,
)

app = FastAPI()
_todos = {"1": "todo 1"}


def render(element: BaseHtmlElement):
    return HTMLResponse(str(element))


def render_todos(todos):
    return render(
        UL(_class="border rounded-lg overflow-hidden")[
            [
                LI(_class="flex items-center justify-between px-3 py-2 border-b")[
                    SPAN(_class="text-lg")[todo],
                    BUTTON(
                        hx_delete=f"/todo/{id}",
                        hx_target="#todo-list",
                        _class="text-red-500 hover:text-red-700",
                    )["delete"],
                ]
                for id, todo in todos.items()
            ]
        ]
    )


def todos():
    yield _todos


GLOBAL_STYLE = """body {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    }"""


@app.get("/")
def root():
    return render(
        HTML(lang="en")[
            HEAD[
                META['charset="utf-8"'],
                META['name="viewport" content="width=device-width, initial-scale=1"'],
                TITLE["Todo App"],
                SCRIPT(src="https://unpkg.com/htmx.org@1.9.6"),
                SCRIPT(src="https://cdn.tailwindcss.com"),
                STYLE[GLOBAL_STYLE],
            ],
            BODY[
                DIV(_class="max-w-md max-auto")[
                    H1(_class="text-2xl font-bold mb-4")["Todo List"],
                    FORM(_class="mb-4", hx_post="/todos", hx_target="#todo-list")[
                        DIV(_class="flex items-center")[
                            INPUT(
                                type="text",
                                name="task",
                                _class="border rounded-l px-3 py-2 w-full",
                                placeholder="Add new todo",
                            ),
                            BUTTON(
                                type="submit",
                                _class="bg-blue-500 hover:bg-blue-700 text-white font-bold rounded-r px-4 py-2",
                            )["Add"],
                        ]
                    ],
                    DIV(id="todo-list", hx_get="/todos", hx_trigger="load"),
                ],
            ],
        ]
    )


@app.get("/todos")
def todos_list(todos: Annotated[dict, Depends(todos)]):
    return render_todos(todos)


@app.post("/todos")
def todos_add(todos: Annotated[dict, Depends(todos)], task: str = Form("task")):
    id = uuid.uuid4().hex
    todos[id] = task
    return render_todos(todos)


@app.delete("/todo/{id}")
def todos_delete(todos: Annotated[dict, Depends(todos)], id: str):
    del todos[id]
    return render_todos(todos)
