

class article:
    def __init__(self, article_id, title, content, tag, starter_id, create_time, modify_time, thumb_num):
        self.article_id = article_id
        self.title = title
        self.content = content
        self.tag = tag
        self.starter_id = starter_id
        self.create_time = create_time
        self.modify_time = modify_time
        self.thumb_num = thumb_num

class chapter:
    def __init__(self, chapter_id, title, content, article_id, author_id, create_time, thumb_num):
        self.chapter_id = chapter_id
        self.title = title
        self.content = content
        self.article_id = article_id
        self.author_id = author_id
        self.create_time = create_time
        self.thumb_num = thumb_num

class comment:
    def __init__(self, comment_id, chapter_id, content, commenter_id, create_time):
        self.comment_id = comment_id
        self.chapter_id = chapter_id
        self.content = content
        self.commenter_id = commenter_id
        self.create_time = create_time