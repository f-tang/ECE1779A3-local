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
import os, decimal

# get the absolute path of the file
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# path of s3 article folder
ARTICLES_PATH = "articles/"


class ArticleForm(FlaskForm):
    title = StringField(
        label='Title',
        validators=[validators.data_required(message='Title is empty!'),
                    validators.Length(min=1, max=100, message="Title should be less than 100 characters long")]
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
    try:
        form = ArticleForm(request.form)
        if request.method == "POST":
            # check if form is validated
            if not form.validate_on_submit():
                error = "request is invalidated"
                return render_template("article-upload.html", title='new story', form=form, error=error)

            user_id = session['username']
            user_nickname = session['nickname']
            title = escape_string(form.title.data)
            content_body = form.content.data
            tag = form.tag.data

            # access to database
            dynamodb = get_dbresource()
            article_table = dynamodb.Table('articles')
            chapter_table = dynamodb.Table('chapters')

            article_id = str(get_microseconds())
            starter_id = user_id
            chapter_id = article_id + '_' + str(get_microseconds())
            author_id = user_id
            create_time = str(datetime.datetime.now())[:16]
            modify_time = create_time

            # insert the article info into the database
            response1 = article_table.query(
                KeyConditionExpression=Key('ArticleID').eq(escape_string(article_id))
            )
            response2 = chapter_table.query(
                KeyConditionExpression=Key('ChapterID').eq(escape_string(chapter_id))
            )

            if response1['Count'] > 0 or response2['Count'] > 0:
                flash("Server is busy, please try again.")
                return render_template("article-upload.html", title="new article", error=error)

            # upload article body to s3
            s3 = get_s3bucket()
            content = ARTICLES_PATH + article_id + '/' + chapter_id + '.md'
            s3.put_object(Key=content, Body=content_body, ACL='public-read')

            article_table.put_item(
                Item={
                    'ArticleID': escape_string(article_id),
                    'Title': escape_string(title),
                    'Tag': escape_string(tag),
                    'StarterID': escape_string(starter_id),
                    'CreateTime': escape_string(create_time),
                    'ModifyTime': escape_string(modify_time),
                    'ThumbNum': decimal.Decimal(0)
                }
            )

            chapter_table.put_item(
                Item={
                    'ChapterID': escape_string(chapter_id),
                    'Content': escape_string(content),
                    'AuthorID': escape_string(author_id),
                    'ArticleID': escape_string(article_id),
                    'CreateTime': escape_string(create_time),
                    'ThumbNum': decimal.Decimal(0)
                }
            )
            gc.collect()

            flash("new story is created successfully")
            return redirect(url_for("full_article", article_id=article_id))

        return render_template("article-upload.html", title="new story", form=form)

    except Exception as e:
        return str(e)

class ChapterForm(FlaskForm):
    content = TextAreaField(
        label='Content',
        validators=[validators.data_required(message='Content is empty!')]
    )


# page for new article
@webapp.route('/<article_id>/new-chapter', methods=['POST'])
@login_required
def new_chapter(article_id):
    error = ''
    try:
        form = ChapterForm(request.form)
        if not form.validate_on_submit():
            error = "request is invalidated"
            return redirect(url_for("full_article", article_id=article_id, error=error))

        # access to database
        dynamodb = get_dbresource()
        article_table = dynamodb.Table('articles')
        chapter_table = dynamodb.Table('chapters')

        response = article_table.query(
            KeyConditionExpression=Key('ArticleID').eq(escape_string(article_id))
        )
        if response['Count'] == 0:
            raise ValueError('This page does not exist.')

        content_body = form.content.data
        chapter_id = article_id + '_' + str(get_microseconds())
        author_id = session['username']
        create_time = str(datetime.datetime.now())[:16]
        modify_time = create_time

        response = chapter_table.query(
            KeyConditionExpression=Key('ChapterID').eq(escape_string(chapter_id))
        )

        if response['Count'] > 0:
            flash("Server is busy, please try again.")
            return render_template("article-upload.html", title="new article", error=error)

        # upload article body to s3
        s3 = get_s3bucket()
        content = ARTICLES_PATH + article_id + '/' + chapter_id + '.md'
        s3.put_object(Key=content, Body=content_body, ACL='public-read')

        # insert the article info into the database
        chapter_table.put_item(
            Item={
                'ChapterID': escape_string(chapter_id),
                'Content': escape_string(content),
                'AuthorID': escape_string(author_id),
                'ArticleID': escape_string(article_id),
                'CreateTime': escape_string(create_time),
                'ThumbNum': decimal.Decimal(0)
            }
        )

        # TODO: update article's modify time
        article_table.update_item(
            Key={
                'ArticleID': article_id
            },
            UpdateExpression="set ModifyTime = :m",
            ExpressionAttributeValues={
                ':m': modify_time
            },
            ReturnValues="UPDATED_NEW"
        )

        gc.collect()

        flash("new chapter is created successfully")
        return redirect(url_for("full_article", article_id=article_id))

    except Exception as e:
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
