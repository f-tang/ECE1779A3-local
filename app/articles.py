from flask import render_template, redirect, url_for, request, g, session, flash
from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SelectField, validators
from app import webapp, login_required, get_db, teardown_db, get_s3client, get_dbresource, classes
from pymysql import escape_string

import boto3
from boto3.dynamodb.conditions import Key

import gc
import os, shutil
import operator

# get the absolute path of the file
APP_ROOT = os.path.dirname(os.path.abspath(__file__)) + "/static"

BUCKET_NAME = 'ece1779-ft'


# page for the article list
@webapp.route("/list-all")
def article_list():
    error = ""
    try:
        # access database
        dynamodb = get_dbresource()
        articletable = dynamodb.Table('articles')
        usertable = dynamodb.Table('users')

        cover_url = "https://s3.amazonaws.com/ece1779-ft/cover_pics/"

        # fetch all articles
        articles = []
        response = articletable.scan()
        for item in response['Items']:
            r = usertable.query(
                IndexName='UIDIndex',
                KeyConditionExpression=Key('UserID').eq(item['StarterID'])
            )
            if r['Count'] == 0:
                raise ValueError('Cannot find the author.')

            starter_name = r['Items'][0]['Nickname']

            article = classes.article(
                article_id=item['ArticleID'],
                title=item['Title'],
                cover_pic=escape_string(cover_url + item['Tag']),
                tag=item['Tag'],
                starter_id=item['StarterID'],
                starter_name=starter_name,
                create_time=item['CreateTime'],
                modify_time=item['ModifyTime'],
                thumb_num=item['ThumbNum']
            )
            articles.append(article)

        articles.sort(key=operator.attrgetter('modify_time'), reverse=True)
        # cleanup
        gc.collect()

        return render_template("article-list.html", title="Gallery", articles=articles, tag='all')

    except Exception as e:
        return str(e)


@webapp.route("/list-<tag>")
def article_list_tag(tag):
    error = ""
    try:
        # access database
        dynamodb = get_dbresource()
        articletable = dynamodb.Table('articles')
        usertable = dynamodb.Table('users')

        cover_url = "https://s3.amazonaws.com/ece1779-ft/cover_pics/"

        # fetch all articles
        articles = []
        response = articletable.query(
            IndexName='TagIndex',
            KeyConditionExpression=Key('Tag').eq(tag)
        )
        for item in response['Items']:
            r = usertable.query(
                IndexName='UIDIndex',
                KeyConditionExpression=Key('UserID').eq(item['StarterID'])
            )
            if r['Count'] == 0:
                raise ValueError('Cannot find the author.')

            starter_name = r['Items'][0]['Nickname']

            article = classes.article(
                article_id=item['ArticleID'],
                title=item['Title'],
                cover_pic=escape_string(cover_url + item['Tag']),
                tag=item['Tag'],
                starter_id=item['StarterID'],
                starter_name=starter_name,
                create_time=item['CreateTime'],
                modify_time=item['ModifyTime'],
                thumb_num=item['ThumbNum']
            )
            articles.append(article)

        articles.sort(key=operator.attrgetter('modify_time'), reverse=True)
        # cleanup
        gc.collect()

        return render_template("article-list.html", title="Gallery", articles=articles, tag=tag)

    except Exception as e:
        return str(e)  # page for showing full articles

@webapp.route("/article/<article_id>")
def full_article(article_id):
    try:
        cover_url = "https://s3.amazonaws.com/ece1779-ft/cover_pics/"
        s3_url = "https://s3.amazonaws.com/ece1779-ft/"
        chapter_form = classes.ChapterForm(request.form)
        comment_form = classes.CommentForm(request.form)

        # access database
        dynamodb = get_dbresource()
        chaptertable = dynamodb.Table('chapters')
        usertable = dynamodb.Table('users')
        articletable = dynamodb.Table('articles')
        comment_table = dynamodb.Table('comments')

        # query for article information
        response = articletable.query(
            KeyConditionExpression=Key('ArticleID').eq(article_id)
        )
        if response['Count'] == 0:
            raise ValueError('This page does not exist.')

        item = response['Items'][0]

        # query for starter information
        r = usertable.query(
            IndexName='UIDIndex',
            KeyConditionExpression=Key('UserID').eq(item['StarterID'])
        )
        if r['Count'] == 0:
            raise ValueError('Cannot find the author.')

        starter_name = r['Items'][0]['Nickname']
        article = classes.article(
            article_id=item['ArticleID'],
            title=item['Title'],
            cover_pic=escape_string(cover_url + item['Tag']),
            tag=item['Tag'],
            starter_id=item['StarterID'],
            starter_name=starter_name,
            create_time=item['CreateTime'],
            modify_time=item['ModifyTime'],
            thumb_num=item['ThumbNum']
        )

        # query for chapter information
        response = chaptertable.query(
            IndexName='ArticleIndex',
            KeyConditionExpression=Key('ArticleID').eq(article_id)
        )
        # initialize the chapter list
        chapters = []
        for item in response['Items']:
            r = usertable.query(
                IndexName='UIDIndex',
                KeyConditionExpression=Key('UserID').eq(item['AuthorID'])
            )
            if r['Count'] == 0:
                raise ValueError('Cannot find the author.')

            author_name = r['Items'][0]['Nickname']

            chapter = classes.chapter(
                chapter_id=item['ChapterID'],
                content=s3_url + item['Content'],
                article_id=item['ArticleID'],
                author_id=item['AuthorID'],
                author_name=author_name,
                create_time=item['CreateTime'],
                thumb_num=item['ThumbNum']
            )

            r_comment = comment_table.query(
                IndexName='ChapterIndex',
                KeyConditionExpression=Key('ChapterID').eq(chapter.chapter_id)
            )
            if r_comment['Count'] > 0:
                chapter.comment = []
                i_comments = r_comment['Items']
                for i in i_comments:
                    r_user = usertable.query(
                        IndexName='UIDIndex',
                        KeyConditionExpression=Key('UserID').eq(i['CommenterID'])
                    )
                    if r_user['Count'] > 0:
                        commenter_name = r_user['Items'][0]['Nickname']
                    else:
                        commenter_name = 'Anonymous'

                    comment = classes.comment(
                        comment_id=i['CommentID'],
                        chapter_id=i['ChapterID'],
                        content=s3_url + i['Content'],
                        commenter_id=i['CommenterID'],
                        commenter_name=commenter_name,
                        create_time=i['CreateTime'],
                    )
                    chapter.comment.append(comment)
                chapter.comment.sort(key=operator.attrgetter('create_time'), reverse=False)

            chapters.append(chapter)
        chapters.sort(key=operator.attrgetter('create_time'), reverse=False)

        return render_template(
            "full-article.html",
            article=article, chapters=chapters,
            chapterform=chapter_form, commentform=comment_form)

    except Exception as e:
        return str(e)
