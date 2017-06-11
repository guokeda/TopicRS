from flask import Flask, render_template, session, redirect, url_for, flash
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField
from wtforms.validators import Required, DataRequired
import random
import sqlite3
import os
import RS

# option database

cur_dir = os.path.dirname(__file__)
db = os.path.join(cur_dir, 'TopicBank.sqlite')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)


# random porduce a question
def produceID():
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    rownum = cur.execute("SELECT count(*) FROM topicbank").fetchall()[0][0]
    rowid = random.randint(1, rownum)
    cur.close()
    conn.close()
    return rowid


global rowid
rowid = produceID()


def producetopic():
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    topic = cur.execute("SELECT * FROM topicbank WHERE rowid=(?);", (rowid,)).fetchall()[0]
    cur.close()
    conn.close()
    return topic


def produce_recommend(recommend_id):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    topic = cur.execute("SELECT * FROM topicbank WHERE rowid=(?);", (recommend_id,)).fetchall()[0]
    cur.close()
    conn.close()
    return topic


# define global var convenience call it
index_topic = producetopic()

stopchracters = ['这', '的', '、', '：', '\n', ]
cs = RS.CS(stopchracters)
cs.buildworddictionary()
cs.factormatrix()
recommend_list = cs.mianfunction(rowid)

recommend_topic1 = produce_recommend(recommend_list[0])
recommend_topic2 = produce_recommend(recommend_list[1])
recommend_topic3 = produce_recommend(recommend_list[2])

# define initial interface form
class indexForm(FlaskForm):
    option = RadioField('option', choices=[('a', index_topic[2]), ('b', index_topic[3]), ('c', index_topic[4]),
                                           ('d', index_topic[5])],
                        validators=[DataRequired()])
    submit = SubmitField('Submit', validators=[DataRequired()])


class recommendForm1(FlaskForm):
    option = RadioField('option',
                        choices=[('a', recommend_topic1[2]), ('b', recommend_topic1[3]), ('c', recommend_topic1[4]), ('d', recommend_topic1[5])],
                        validators=[DataRequired()])
    submit1 = SubmitField('Submit')


class recommendForm2(FlaskForm):
    option = RadioField('option',
                        choices=[('a', recommend_topic2[2]), ('b', recommend_topic2[3]), ('c', recommend_topic2[4]), ('d', recommend_topic2[5])],
                        validators=[DataRequired()])
    submit2 = SubmitField('Submit')


class recommendForm3(FlaskForm):
    option = RadioField('option',
                        choices=[('a', recommend_topic3[2]), ('b', recommend_topic3[3]), ('c', recommend_topic3[4]), ('d', recommend_topic3[5])],
                        validators=[DataRequired()])
    submit3 = SubmitField('Submit')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    form = indexForm()
    if form.validate_on_submit():
        if (form.option.data != index_topic[0].lower()):
            flash('答案：本题选择' + index_topic[0] + '。详解：' + index_topic[6], category='error')
        else:
            flash('这道题你做对了' + '。详解：' + index_topic[6])
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=index_topic[1])


@app.route('/qianghua', methods=['GET', 'POST'])
def recommend():
    form1 = recommendForm1()
    form2 = recommendForm2()
    form3 = recommendForm3()

    if form1.submit1.data:
        if (form1.option.data != recommend_topic1[0].lower()):
            flash('答案：本题选择' + recommend_topic1[0] + '。详解：' + recommend_topic1[6], category='error')
        else:
            flash('这道题你做对了' + '。详解：' + recommend_topic1[6])
        return redirect(url_for('recommend'))
    if form2.submit2.data:
        if (form2.option.data != recommend_topic2[0].lower()):
            flash('答案：本题选择' + recommend_topic2[0] + '。详解：' + recommend_topic2[6], category='error')
        else:
            flash('这道题你做对了' + '。详解：' + recommend_topic2[6])
        return redirect(url_for('recommend'))
    if form3.submit3.data:
        if (form3.option.data != recommend_topic3[0].lower()):
            flash('答案：本题选择' + recommend_topic3[0] + '。详解：' + recommend_topic3[6], category='error')
        else:
            flash('这道题你做对了' + '。详解：' + recommend_topic3[6])
        return redirect(url_for('recommend'))
    return render_template('qianghua.html', form1=form1, form2=form2, form3=form3, topic1=recommend_topic1[1],
                           topic2=recommend_topic2[1], topic3=recommend_topic3[1])


if __name__ == '__main__':
    app.run()
