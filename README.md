# 🎓 Student Performance & Academic Analytics System

Flask + MySQL + Pandas project with three logins
(Admin, Teacher, Student), analytics dashboards, charts, rule-based
performance analysis, and CSV/Excel report exports.

## 📁 Project Structure

```
student_analytics/
├── app.py                  # main entry point (run this)
├── config.py                # MySQL + Flask settings
├── extensions.py            # shared SQLAlchemy "db" object
├── models.py                 # database tables as Python classes
├── schema.sql                 # run this in MySQL first
├── requirements.txt
├── routes/
│   ├── auth.py               # login/logout
│   ├── admin.py               # admin features
│   ├── teacher.py              # teacher features
│   └── student.py               # student features
├── utils/
│   ├── analytics.py           # pandas calculations (%, grade, risk)
│   ├── charts.py                # matplotlib/seaborn chart images
│   ├── reports.py               # CSV/Excel export
│   └── decorators.py            # @login_required, @role_required
├── scripts/
│   ├── seed_data.py            # creates admin/teacher/sample students
├── templates/                  # all HTML pages (Jinja2 + Bootstrap 5)
└── static/                     # CSS + generated chart images
```

## 🛠️ Step-by-Step Setup

### 1. Install Python packages
```bash
cd student_analytics
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Create the MySQL database
Make sure MySQL is running, then:
```bash
mysql -u root -p < schema.sql
```
This creates the `student_analytics_db` database and all 6 tables.

### 3. Configure the application environment
Set a strong, unique `SECRET_KEY` before starting the application:

```bash
# Linux/macOS
export SECRET_KEY="replace-with-a-long-random-secret"

# Windows PowerShell
$env:SECRET_KEY = "replace-with-a-long-random-secret"
```

For local development, the same environment variable can be set in a local
`.env` file (which must not be committed) or in the shell before running the
application. The application will refuse to start if `SECRET_KEY` is missing.

### 4. Set your MySQL password
Open `config.py` and change:
```python
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "your_mysql_password")
```
to your actual MySQL root password. (Or set the `MYSQL_PASSWORD` environment
variable instead of editing the file.)

### 5. Load sample data (recommended for your demo)
```bash
python scripts/seed_data.py
```
This creates:
| Role    | Username  | Password    |
|---------|-----------|-------------|
| Admin   | admin     | admin123    |
| Teacher | teacher1  | teacher123  |
| Student | student1  | student123  |
| Student | student2  | student123  |
| ...     | student3-5| student123  |

with 4 sample subjects and randomly-generated marks/attendance so every
chart and report has something to show immediately.

### 6. Run the app
```bash
python app.py
```
Open **http://127.0.0.1:5000** in your browser.

## 🧭 How the App is Organized (for your viva / presentation)

- **`models.py`** defines the 6 database tables using SQLAlchemy ORM —
   this is the same as writing `CREATE TABLE` in SQL, but in Python.
- **`routes/`** is split by role (auth / admin / teacher / student) using
   Flask **Blueprints**, so each role's code lives in its own file instead
   of one giant `app.py`.
- **`utils/analytics.py`** is where Pandas does the real work: it reads
   rows from MySQL, puts them in a DataFrame, and calculates percentage,
   grade, attendance %, and risk level (Low/Medium/High) using simple
   rules.
- **`utils/charts.py`** uses Matplotlib/Seaborn to draw 3 charts (grade
   distribution, subject averages, attendance-vs-performance) and saves
   them as PNG files that the dashboard displays with a normal `<img>` tag.
- **`utils/reports.py`** exports the same Pandas DataFrames to CSV/Excel
   using `df.to_csv()` and `df.to_excel()` — one line each.
- **Validation** (no marks over 100%, no negative attendance, no duplicate
   roll numbers) is enforced in `routes/admin.py` and `routes/teacher.py`
   before anything is saved to the database.

## 🔑 Login Flow

1. `routes/auth.py` checks the username/password against the `users`
   table (passwords are hashed with Werkzeug, never stored as plain text).
2. On success, the user's id/role/name are saved into a Flask `session`
   (a secure cookie).
3. `utils/decorators.py` has `@role_required("admin")` etc. — put this
   decorator above any route to make sure only that role can access it.

## ➕ Extending the Project

Some easy next steps if you want to add more marks for your submission:
  semester) — this only needs a few extra `request.args.get()` calls in
  `routes/admin.py` and a `WHERE`-style `.filter()` in the query.
  data instead of the current-semester approximation used now.
