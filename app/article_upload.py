from flask import render_template, redirect, url_for, request, g, flash, session
from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SelectField, validators
from app import webapp, login_required, get_db, teardown_db, get_s3bucket, get_dbresource, get_microseconds
from pymysql import escape_string
from wand.image import Image

import boto3
from boto3.dynamodb.conditions import Key

import datetime
import gc
import os, shutil

# get the absolute path of the file
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# path of s3 article folder
ARTICLES_PATH = "articles/"


class ArticleForm(FlaskForm):
    title = StringField(
        label='Title',
        validators=[validators.Length(min=1, max=100, message="Title should be less than 100 characters long")]
    )
    content = TextAreaField(
        label='Content',
        validators=[validators.data_required(message='Content is empty!')]
    )
    tag = SelectField(
        label='Tag',
        choices=[('fiction', 'Fiction'), ('marvel', 'Marvel'), ('fairytale', 'Fairytale')]
    )


# page for new article
@webapp.route('/new-story', methods=['GET', 'POST'])
@login_required
def new_article():
    error = ''
    APP_RELATED = 'static/tmp/' + session['username'] + str(get_microseconds())
    tmp_target = os.path.join(APP_ROOT, APP_RELATED)

    try:
        form = ArticleForm(request.form)
        if request.method == "POST":
            # check if form is validated
            if not form.validate_on_submit():
                error = "request is invalidated"
                return render_template("article-upload.html", title='new story', form=form, error=error)

            # access to database
            dynamodb = get_dbresource()
            article_table = dynamodb.Table('articles')
            chapter_table = dynamodb.Table('chapters')

            s3 = get_s3bucket()

            # file path of articles
            if not os.path.isdir(os.path.join(APP_ROOT, 'static/tmp/')):
                os.mkdir(os.path.join(APP_ROOT, 'static/tmp/'))

            # create a tmp folder for the user if it does not exist
            if not os.path.isdir(tmp_target):
                os.mkdir(tmp_target)

            # check if file exists in the request
            if 'file' not in request.files:
                error = "file does not exist"
                return render_template("article-upload.html", title="new story", form=form, error=error)

            # insert the article info into the database
            article_id = str(get_microseconds())
            starter_id = session['username']
            starter_name = session['nickname']
            chapter_id = article_id + '_' + str(get_microseconds())
            author_id = session['username']
            author_name = session['nickname']
            thumb_num = 0
            content = ARTICLES_PATH + article_id + '/' + chapter_id + '.md'

            # TODO: get article title, tag and chapter title
            article_title = ''
            chapter_title = ''
            create_time = str(datetime.datetime.now())[:16]
            modify_time = create_time
            tag = ''

            response1 = article_table.query(
                KeyConditionExpression=Key('ArticleID').eq(escape_string(article_id))
            )
            response2 = chapter_table.query(
                KeyConditionExpression=Key('ChapterID').eq(escape_string(chapter_id))
            )

            if response1['Count'] > 0 or response2['Count'] > 0:
                flash("Server is busy, please try again.")
                return render_template("article-upload.html", title="new article", error=error)

            article_table.put_item(
                Item={
                    'ArticleID': escape_string(article_id),
                    'Title': escape_string(article_title),
                    'Tag': escape_string(tag),
                    'StarterID': escape_string(starter_id),
                    'CreateTime': escape_string(create_time),
                    'ModifyTime': escape_string(modify_time),
                    'ThumbNum': escape_string(thumb_num)
                }
            )

            chapter_table.put_item(
                Item={
                    'ChapterID': escape_string(chapter_id),
                    'Title': escape_string(chapter_title),
                    'Content': escape_string(content),
                    'AuthorID': escape_string(author_id),
                    'ArticleID': escape_string(article_id),
                    'CreateTime': escape_string(create_time),
                    'ThumbNum': escape_string(thumb_num)
                }
            )

            # save the chapter file
            target = ARTICLES_PATH + article_id + '/' + chapter_id + '.md'
            tmp_dest = "/".join([tmp_target, chapter_id])

            # s3.put_object(Key=content, Body=file, ACL='public-read')

            # database commit, cleanup and garbage collect
            shutil.rmtree(tmp_target)
            gc.collect()

            flash("new story is created successfully")
            return redirect(url_for("full_article", article_id=article_id))

        return render_template("article-upload.html", title="new story", form=form)

    except Exception as e:
        if os.path.isdir(tmp_target):
            shutil.rmtree(tmp_target)
        return str(e)


# page for new article
@webapp.route('/<article_id>/new-chapter', methods=['POST'])
@login_required
def new_chapter(article_id):
    error = ''
    APP_RELATED = 'static/tmp/' + session['username'] + str(get_microseconds())
    tmp_target = os.path.join(APP_ROOT, APP_RELATED)

    try:
        # access to database
        dynamodb = get_dbresource()
        article_table = dynamodb.Table('articles')
        chapter_table = dynamodb.Table('chapters')

        s3 = get_s3bucket()

        # TODO: check if the article id exists

        # check if file exists in the request
        if 'file' not in request.files:
            error = "file does not exist"
            return redirect(url_for("full_article", article_id=article_id, error=error))

        file = request.files['file']

        # insert the article info into the database
        chapter_id = article_id + '_' + str(get_microseconds())
        author_id = session['username']
        author_name = session['nickname']
        thumb_num = 0
        content = ARTICLES_PATH + article_id + '/' + chapter_id + '.md'

        # TODO: get chapter title, tag
        chapter_title = ''
        create_time = str(datetime.datetime.now())[:16]
        modify_time = create_time
        tag = ''

        response = chapter_table.query(
            KeyConditionExpression=Key('ChapterID').eq(escape_string(chapter_id))
        )

        if response['Count'] > 0:
            flash("Server is busy, please try again.")
            return render_template("article-upload.html", title="new article", error=error)

        chapter_table.put_item(
            Item={
                'ChapterID': escape_string(chapter_id),
                'Title': escape_string(chapter_title),
                'Content': escape_string(content),
                'AuthorID': escape_string(author_id),
                'ArticleID': escape_string(article_id),
                'CreateTime': escape_string(create_time),
                'ThumbNum': escape_string(thumb_num)
            }
        )

        # save the chapter file
        target = ARTICLES_PATH + article_id + '/' + chapter_id + '.md'
        tmp_dest = "/".join([tmp_target, chapter_id])

        s3.put_object(Key=content, Body=file, ACL='public-read')

        # TODO: update article's modify time

        # database commit, cleanup and garbage collect
        shutil.rmtree(tmp_target)
        gc.collect()

        flash("new story is created successfully")
        return redirect(url_for("full_article", article_id=article_id))

    except Exception as e:
        if os.path.isdir(tmp_target):
            shutil.rmtree(tmp_target)
        return str(e)


# thumbup for article
@webapp.route('/thumbup/<article_id>', methods=['POST'])
@login_required
def thumbup_article(article_id):
    return redirect(url_for("full_article"))


# thumbup for chapter
@webapp.route('/thumbup/<chapter_id>', methods=['POST'])
@login_required
def thumbup_chapter(chapter_id):
    return redirect(url_for("full_article"))
