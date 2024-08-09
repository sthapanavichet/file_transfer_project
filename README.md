# file_transfer_proejct
A group project made with fellow friends for a software development and deployment course.
This is a file sharing website that uses django and its sqlite database to store the models.
Files are encrypted and hashed for security.
Only accounts shared to by the file's original owner can download the file.
Only signed in users can access other parts of the website.

# How to setup the django application
1. Run the makemigrations command to ensure that any changes made to the models is updated

  python manage.py makemigrations
  
2. Run the migrate command to set up the database:

  python manage.py migrate

3. Run the server with this command

  python manage.py runserver

Superusers:
Username: brundern, Email: brunder03@gmail.com
Username: chet, Email: chet@gmail.com
