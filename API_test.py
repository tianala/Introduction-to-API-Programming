import unittest
import json
from API_CRUD_DBMS import app, get_db_connection
from unittest.mock import patch

class FlaskDBMSTestCase(unittest.TestCase):
    def setUp(self):

        self.app = app.test_client()
        self.app.testing = True
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS books")
        cursor.execute("""
            CREATE TABLE books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                year INT NOT NULL
            )
        """)
        cursor.execute("INSERT INTO books (title, author, year) VALUES (%s, %s, %s)", ("The Great Gatsby", "F. Scott Fitzgerald", 1925))
        cursor.execute("INSERT INTO books (title, author, year) VALUES (%s, %s, %s)", ("1984", "George Orwell", 1949))
        conn.commit()
        cursor.close()
        conn.close()

    def tearDown(self):
        """Clean up the database after each test."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM books")
        conn.commit()
        cursor.close()
        conn.close()


    def test_get_all_books(self):
        response = self.app.get("/api/books_dbms")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertEqual(len(data["data"]), 2)

    def test_get_single_book(self):
        response = self.app.get("/api/books_dbms/1")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["title"], "The Great Gatsby")

    def test_get_nonexistent_book(self):
        response = self.app.get("/api/books_dbms/999")
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Book not found")

    def test_create_book(self):
        new_book = {
            "title": "Brave New World",
            "author": "Aldous Huxley",
            "year": 1932
        }
        response = self.app.post("/api/books_dbms", data=json.dumps(new_book), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["title"], new_book["title"])

        # Verify the book was added
        response = self.app.get("/api/books_dbms")
        data = json.loads(response.data)
        self.assertEqual(len(data["data"]), 3)

    def test_create_book_missing_fields(self):
        new_book = {"title": "Incomplete Book"}
        response = self.app.post("/api/books_dbms", data=json.dumps(new_book), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data["success"])
        self.assertIn("Missing required fields", data["error"])

    def test_update_book(self):
        updated_data = {"title": "Updated Title", "author": "Updated Author", "year": 1933}
        response = self.app.put("/api/books_dbms/1", data=json.dumps(updated_data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["title"], updated_data["title"])


        response = self.app.get("/api/books_dbms/1")
        data = json.loads(response.data)
        self.assertEqual(data["data"]["title"], updated_data["title"])

    def test_update_nonexistent_book(self):
        updated_data = {"title": "Nonexistent"}
        response = self.app.put("/api/books_dbms/999", data=json.dumps(updated_data), content_type="application/json")
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Book not found")

    def test_delete_book(self):
        response = self.app.delete("/api/books_dbms/1")
        self.assertEqual(response.status_code, 204)

        response = self.app.get("/api/books_dbms/1")
        self.assertEqual(response.status_code, 404)

    def test_delete_nonexistent_book(self):
        response = self.app.delete("/api/books_dbms/999")
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Book not found")

    def test_404_error(self):
        response = self.app.get("/nonexistent-route")
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Resource not found")


def test_500_error(self):
    with patch("API_CRUD_DBMS.get_db_connection", side_effect=Exception):
        response = self.app.get("/api/books_dbms")
        self.assertEqual(response.status_code, 500)
        self.assertIn("Internal Server Error", response.get_data(as_text=True))



if __name__ == "__main__":
    unittest.main()
