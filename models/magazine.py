from database.connection import get_db_connection
class Magazine:
    def __init__(self, id=None, name=None, category=None):
        if not isinstance(name, str) or len(name) < 2 or len(name) > 16:
            raise ValueError("Magazine name must be a string between 2 and 16 characters.")
        
        if category is None:
            category = "General"  # Assign a default category if none is provided
        elif not isinstance(category, str) or len(category) == 0:
            raise ValueError("Category must be a non-empty string.")
        
        self.id = id
        self._name = name
        self.category = category
        
        if not id:
            conn = get_db_connection() 
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO magazines (name, category) VALUES (?, ?)''', (name, category))
            conn.commit()
            
            self._id = cursor.lastrowid
            conn.close()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        if not isinstance(new_name, str) or len(new_name) < 2 or len(new_name) > 16:
            raise ValueError("Magazine name must be a string between 2 and 16 characters.")
        self._name = new_name

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, new_category):
        if not isinstance(new_category, str) or len(new_category) == 0:
            raise ValueError("Category must be a non-empty string.")
        self._category = new_category

    def __repr__(self):
        return f'<Magazine {self.name}>'

    def articles(self):
        """Return all articles associated with this magazine."""
        from models.article import Article  # Import Article class to avoid circular import

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT a.id, a.title, a.content, a.author_id, a.magazine_id
            FROM articles a
            WHERE a.magazine_id = ?
        ''', (self.id,))

        articles_data = cursor.fetchall()

        articles = []
        for article_data in articles_data:
            article = Article(article_data[3], article_data[1], article_data[2], article_data[4], article_data[0])
            articles.append(article)

        conn.close()
        return articles

    def contributors(self):
        """Return all authors associated with this magazine."""
        from models.author import Author

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT DISTINCT a.id, a.name
            FROM authors a
            JOIN articles ar ON ar.author_id = a.id
            WHERE ar.magazine_id = ?
        ''', (self.id,))

        authors_data = cursor.fetchall()

        authors = []
        for author_data in authors_data:
            author = Author(author_data[0], author_data[1])
            authors.append(author)

        conn.close()
        return authors

    def article_titles(self):
        """Return the titles of all articles associated with this magazine."""
        articles = self.articles()  # Retrieve all articles
        if not articles:
            return None
        return [article.title for article in articles]

    def contributing_authors(self):
        """Return authors who have contributed more than two articles to this magazine."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT a.id, a.name, COUNT(ar.id) as article_count
            FROM authors a
            JOIN articles ar ON ar.author_id = a.id
            WHERE ar.magazine_id = ?
            GROUP BY a.id
            HAVING COUNT(ar.id) > 2
        ''', (self.id,))

        authors_data = cursor.fetchall()

        contributing_authors = []
        from models.author import Author 
        for author_data in authors_data:
            author = Author(author_data[0], author_data[1])
            contributing_authors.append(author)

        conn.close()

        if not contributing_authors:
            return None
        return contributing_authors
