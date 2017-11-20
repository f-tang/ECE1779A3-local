

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
    def __init__(self, chapter_id, title, content, article_id, author_id, author_name, create_time, thumb_num):
        self.chapter_id = chapter_id
        self.title = title
        self.content = content
        self.article_id = article_id
        self.author_id = author_id
        self.author_name = author_name
        self.create_time = create_time
        self.thumb_num = thumb_num

class comment:
    def __init__(self, comment_id, chapter_id, content, commenter_id, commenter_name, create_time):
        self.comment_id = comment_id
        self.chapter_id = chapter_id
        self.content = content
        self.commenter_id = commenter_id
        self.commenter_name = commenter_name
        self.create_time = create_time