from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy  #データベース
from datetime import datetime, timezone  #日付

#FlaskでWebアプリを作る
app = Flask(__name__) 
# app のDB保存先 test.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  
#pythonでdbを使うためのライブラリを変数に入れる
db = SQLAlchemy(app) 


# DB用クラスの設定
# db.Model = クラスをDBテーブルに対応させる
class Todo(db.Model):
    # Column(列名)の設定と制約
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(200), nullable = False)
    #completed = db.Column(db.Integer, default = 0)
    ##データ型(DateTime)の制約、初期値は現在のUTC（世界標準時）
    date_created = db.Column(db.DateTime, default = datetime.now(timezone.utc))

    #データの値を返す関数
    def __repr__(self):
        return '<Task %r>' % self.id

#メインページが開かれたときに実行する関数index
#GET  = データの取得（ページの表示）
#POST = データの送信（新しいタスクの追加）
@app.route('/', methods = ['POST', 'GET'])
def index():
    # index.html の form からタスク(content)が送られてきたとき
    if request.method == 'POST':
        # content を取り出す
        task_content = request.form['content']
        #Todoクラスの新しい content に task_content を追加する
        new_task = Todo(content = task_content)

        # try = エラーが出るかもしれない処理
        #追加したTodoをDBに add⇒commit
        try: 
            db.session.add(new_task)
            db.session.commit()
            # メインページをリロード
            return redirect('/')
        # error時
        except:
            return 'タスクの実行中に問題が発生しました'

    # GET でページを表示をするだけのとき
    else:
        # Todo クラスに対応する DB からタスクの作成日時順に、全部のデータを取り出す
        tasks = Todo.query.order_by(Todo.date_created).all()
        # index.html に tasks のデータを組み込んで表示する
        return render_template('index.html', tasks = tasks)
    
# DELETEボタンが押されたとき
@app.route('/delete/<int:id>')
def delete(id):

    # Todo から DALETE を押した id のタスクを取得。結果はGETか404エラー。
    task_to_delete = Todo.query.get_or_404(id)

    #例外処理
    # delete⇒ commit⇒ 反映
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'タスクの削除中に問題が発生しました'
    
# UPDATEボタンが押されたとき(GET or POST)
@app.route('/update/<int:id>', methods = ['GET', 'POST'])
def update(id):

    # Todo から UPDATE を押した id のタスクを取得。結果はGETか404エラー。
    task = Todo.query.get_or_404(id)

    # update.html の form から更新情報(content)が送られてきたとき
    if request.method == 'POST':
        # その ID のタスクに content を直接代入する。
        task.content = request.form['content']

        #例外処理
        # commit⇒ 反映
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'アップデート中に問題が発生しました'
    #UPDATEボタンが押されたときに update.html を表示する
    #その際に定義した task(id / content etc) を変数として送っている
    else:
        return render_template('update.html', task = task)

# システムを実行する
# __name__ = 現在実行されているファイルの役割を伝える変数
# __main__ = このファイルから直接実行されている時の値
# つまり、別のファイルからはページが開けない ⇒ app.pyからプログラムを実行したときのみ、アプリが起動される。
if __name__ == "__main__":
    # Flask の web アプリを起動する
    app.run(debug = True)
