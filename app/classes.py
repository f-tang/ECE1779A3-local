from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SelectField, validators

class article:
    def __init__(self, article_id, title, cover_pic, tag, starter_id, starter_name, create_time, modify_time, thumb_num):
        self.article_id = article_id
        self.title = title
        self.cover_pic = cover_pic
        self.tag = tag
        self.starter_id = starter_id
        self.starter_name = starter_name
        self.create_time = create_time
        self.modify_time = modify_time
        self.thumb_num = thumb_num

class chapter:
    def __init__(self, chapter_id, content, article_id, author_id, author_name, create_time, thumb_num):
        self.chapter_id = chapter_id
        self.content = content
        self.article_id = article_id
        self.author_id = author_id
        self.author_name = author_name
        self.create_time = create_time
        self.thumb_num = thumb_num
        self.comment = None

class comment:
    def __init__(self, comment_id, chapter_id, content, commenter_id, commenter_name, create_time):
        self.comment_id = comment_id
        self.chapter_id = chapter_id
        self.content = content
        self.commenter_id = commenter_id
        self.commenter_name = commenter_name
        self.create_time = create_time

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

class ChapterForm(FlaskForm):
    content = TextAreaField(
        label='',
        validators=[validators.data_required(message='Content is empty!')]
    )

class CommentForm(FlaskForm):
    content = TextAreaField(
        label='',
        validators=[validators.data_required(message='Content is empty!')]
    )
