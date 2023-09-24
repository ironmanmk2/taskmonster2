import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.template_folder = os.path.abspath('templates')

# タスクリストを格納するリスト (データベースの代わり)
tasks = []

# ユーザーの経験値を格納する辞書
user_experience = {'value': 0}

# タスク完了時に経験値を加算
def add_experience():
    user_experience['value'] += 10  # 仮の経験値加算値

@app.route('/')
def index():
    # タスクを優先度でソート
    sorted_tasks = sorted(tasks, key=lambda task: task['priority'])
    return render_template('index.html', tasks=sorted_tasks, user_experience=user_experience)

@app.route('/add_task', methods=['POST'])
def add_task():
    task_titles = request.form.getlist('task_titles')  # タスク名をリストとして取得
    task_priority_str = request.form.get('task_priority')  # 優先度の文字列を取得
    task_deadline_str = request.form.get('task_deadline')  # 締切日の文字列を取得

    # 優先度が空の場合、デフォルト値 3 を設定
    if not task_priority_str:
        task_priority_str = 3

    # 締切日が空の場合、None を設定
    if not task_deadline_str:
        task_deadline = None
    else:
        try:
            # 締切日を日付オブジェクトに変換
            task_deadline = datetime.strptime(task_deadline_str, '%Y-%m-%d').date()
        except ValueError:
            flash('無効な日付形式です。正しい形式（YYYY-MM-DD）で入力してください', 'danger')
            return redirect(url_for('index'))

    if not task_titles:
        flash('少なくとも1つのタスクを入力してください', 'danger')
    else:
        for task_title in task_titles:
            task = {
                'title': task_title,
                'priority': int(task_priority_str),
                'deadline': task_deadline,
                'completed': False
            }
            tasks.append(task)
        flash('タスクが追加されました', 'success')

    return redirect(url_for('index'))

@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    if 0 <= task_id < len(tasks):
        task = tasks.pop(task_id)
        flash(f'タスク "{task["title"]}" が削除されました', 'success')
    else:
        flash('指定されたタスクは存在しません', 'danger')

    return redirect(url_for('index'))

@app.route('/complete_task/<int:task_id>')
def complete_task(task_id):
    if 0 <= task_id < len(tasks):
        task = tasks[task_id]
        task['completed'] = True
        add_experience()  # タスク完了時に経験値を加算
        flash(f'タスク "{task["title"]}" が完了されました', 'success')
        # タスクを削除
        tasks.pop(task_id)
    else:
        flash('指定されたタスクは存在しません', 'danger')

    return redirect(url_for('index'))
if __name__ == '__main__':
    app.run(debug=True)
