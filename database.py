todos = []
current_id = 1

def add_todo(todo_data: dict):
    global current_id
    todo = {
        "id": current_id,
        "title": todo_data.get("title", "No title"),
        "description": todo_data.get("description"),
        "completed": todo_data.get("completed", False)
    }
    todos.append(todo)
    current_id += 1
    return todo

def get_all_todos():
    return todos

def get_todo(todo_id: int):
    for todo in todos:
        if todo["id"] == todo_id:
            return todo
    return None

def update_todo(todo_id: int, todo_data: dict):
    todo = get_todo(todo_id)
    if todo:
        todo.update(todo_data)
        return todo
    return None

def delete_todo(todo_id: int):
    global todos
    todos = [t for t in todos if t["id"] != todo_id]
    return True