def _reindex_task_positions(task_list):
    def sort_key(t):
        # None becomes 9999 to sort to end, otherwise use actual position
        position = t.position if t.position is not None else 9999
        task_id = t.id if t.id is not None else 0
        return (position, task_id)
    
    sorted_tasks = sorted(task_list, key=sort_key)
    
    for new_position, task in enumerate(sorted_tasks, start=1):
        task.position = new_position