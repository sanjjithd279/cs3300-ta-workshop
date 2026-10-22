document.addEventListener('DOMContentLoaded', fetchTasks);

async function fetchTasks() {
    // Fetch tasks and render their titles and priorities.
    const response = await fetch('/api/tasks');
    const tasks = await response.json();
    const taskList = document.getElementById('task-list');
    taskList.innerHTML = '';

    tasks.forEach(task => {
        const li = document.createElement('li');
        const title = document.createElement('span');
        const priority = document.createElement('span');
        const deleteButton = document.createElement('button');

        title.textContent = task.title;
        priority.textContent = `Priority: ${task.priority || 'Medium'}`;
        deleteButton.className = 'delete-btn';
        deleteButton.textContent = 'Delete';
        deleteButton.addEventListener('click', () => deleteTask(task.id));

        li.appendChild(title);
        li.appendChild(priority);
        li.appendChild(deleteButton);
        taskList.appendChild(li);
    });
}

async function addTask() {
    // Create a task using the title and selected priority.
    const titleInput = document.getElementById('task-title');
    const priorityInput = document.getElementById('task-priority');
    const errorElement = document.getElementById('task-error');
    const title = titleInput.value.trim();
    const priority = priorityInput.value;

    errorElement.textContent = '';
    if (!title) return;

    const response = await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, priority })
    });

    if (!response.ok) {
        const result = await response.json();
        errorElement.textContent = result.error || 'Unable to create task';
        return;
    }

    titleInput.value = '';
    priorityInput.value = 'Medium';
    fetchTasks();
}

async function deleteTask(id) {
    // Delete the selected task and refresh the task list.
    await fetch(`/api/tasks/${id}`, {
        method: 'DELETE'
    });
    fetchTasks();
}
