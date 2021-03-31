from flask import Flask

app = Flask(__name__)


# Flask类的route()函数是一个装饰器，它告诉应用程序哪个URL应该调用相关的函数。
# 通过向规则参数添加变量部分，可以动态构建URL。此变量部分标记为<variable-name>
@app.route('/blog/<int:postID>/')
def show_blog(postID):
    return 'Blog Number %d' % postID


@app.route('/rev/<float:revNo>/')
def revision(revNo):
    return 'Revision Number %f' % revNo


if __name__ == '__main__':
    app.run()
