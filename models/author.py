from database.connection import get_db_connection

class Author:
    def __init__(self, id=None, name: str = None):
        if not isinstance(name, str) or len(name) == 0:
            raise ValueError("Name must be a non-empty string")

        if id:
            self._id = id
            self._name = name
        else:
            conn = get_db_connection() 
            cursor = conn.cursor()

            # Insert the author into the database 
            cursor.execute('''
            INSERT INTO authors (name) VALUES (?)''', (name,))
            conn.commit()

            self._id = cursor.lastrowid  
            self._name = name
            conn.close()

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        raise AttributeError("ID cannot be set manually.")

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        # Prevent changing name after instantiation
        if hasattr(self, '_name'):
            raise AttributeError("Name cannot be changed after instantiation.")
        self._name = value

    def articles(self):
        """Return all articles associated with this author."""
        from models.article import Article
        conn = get_db_connection()
        cursor = conn.cursor()

        # SQL query to fetch all articles associated with the author
        cursor.execute('''
            SELECT a.id, a.title, a.content, a.author_id, a.magazine_id
            FROM articles a
            WHERE a.author_id = ?
        ''', (self.id,))
        
        # Fetch all articles and create Article objects
        articles_data = cursor.fetchall()
        
        articles = []
        for article_data in articles_data:
            article = Article(article_data[3], article_data[1], article_data[2], article_data[4], article_data[0])
            articles.append(article)

        conn.close()
        return articles

    def magazines(self):
        """Return all magazines associated with this author through their articles."""
        from models.magazine import Magazine
        conn = get_db_connection()
        cursor = conn.cursor()

        # SQL query to fetch all magazines associated with the articles written by this author
        cursor.execute('''
            SELECT DISTINCT m.id, m.name, m.category
            FROM magazines m
            JOIN articles a ON a.magazine_id = m.id
            WHERE a.author_id = ?
        ''', (self.id,))
        
        # Fetch all magazines and create Magazine objects
        magazines_data = cursor.fetchall()
        
        magazines = []
        for magazine_data in magazines_data:
            magazine = Magazine(magazine_data[0], magazine_data[1], magazine_data[2])
            magazines.append(magazine)

        conn.close()
        return magazines

    def __repr__(self):
        return f'<Author {self.name}>'
