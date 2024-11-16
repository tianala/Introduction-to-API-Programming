from flask import Flask, jsonify, request
from http import HTTPStatus
import mysql.connector

app = Flask(__name__)

db_config = {
    "host": "localhost",
    "user": "root",      
    "password": "root",  
    "database": "library_db"
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route("/api/books_dbms", methods=["GET"])
def get_books():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"success": True, "data": books, "total": len(books)}), HTTPStatus.OK

@app.route("/api/books_dbms/<int:book_id>", methods=["GET"])
def get_book(book_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    book = cursor.fetchone()
    cursor.close()
    conn.close()

    if book is None:
        return jsonify({"success": False, "error": "Book not found"}), HTTPStatus.NOT_FOUND

    return jsonify({"success": True, "data": book}), HTTPStatus.OK

@app.route("/api/books_dbms", methods=["POST"])
def create_book():
    if not request.is_json:
        return jsonify({"success": False, "error": "Content-type must be application/json"}), HTTPStatus.BAD_REQUEST

    data = request.get_json()
    required_fields = ["title", "author", "year"]
    for field in required_fields:
        if field not in data:
            return jsonify({"success": False, "error": f"Missing required fields: {field}"}), HTTPStatus.BAD_REQUEST

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO books (title, author, year) VALUES (%s, %s, %s)", 
                   (data['title'], data['author'], data['year']))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({"success": True, "data": {"id": new_id, "title": data['title'], "author": data['author'], "year": data['year']}}), HTTPStatus.CREATED

@app.route("/api/books_dbms/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    if not request.is_json:
        return jsonify({"success": False, "error": "Content-type must be application/json"}), HTTPStatus.BAD_REQUEST

    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    book = cursor.fetchone()
    if book is None:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "error": "Book not found"}), HTTPStatus.NOT_FOUND

    cursor.execute("UPDATE books SET title = %s, author = %s, year = %s WHERE id = %s",
                   (data.get("title", book["title"]), data.get("author", book["author"]), data.get("year", book["year"]), book_id))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"success": True, "data": {"id": book_id, "title": data.get("title", book["title"]), "author": data.get("author", book["author"]), "year": data.get("year", book["year"])}}), HTTPStatus.OK

@app.route("/api/books_dbms/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    book = cursor.fetchone()
    if book is None:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "error": "Book not found"}), HTTPStatus.NOT_FOUND

    cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"success": True, "message": "Book deleted"}), HTTPStatus.NO_CONTENT

@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "Resource not found"}), HTTPStatus.NOT_FOUND

@app.errorhandler(500)
def internal_server(error):
    return jsonify({"success": False, "error": "Internal Server Error"}), HTTPStatus.INTERNAL_SERVER_ERROR

if __name__ == "__main__":
    
    app.run(debug=True)
