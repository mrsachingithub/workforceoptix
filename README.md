# WorkForceOptix

WorkForceOptix is a comprehensive Workforce Management and Resource Allocation System designed to streamline the management of employees, projects, and resource allocations. It helps organizations track employee availability, manage bench strength, and ensure efficient project staffing.

## Features

- **Employee Management**
  - specific profiles with skills, designation, and contact details.
  - Track availability status (Active, Bench, Partially Utilized).
  - Calculate bench days automatically.

- **Project Management**
  - Create and update project details including client info, required skills, and timelines.
  - Monitor project status (Active, Completed).

- **Resource Allocation**
  - Allocate employees to projects based on skills and availability.
  - Track allocated hours and duration to prevent over-allocation.
  - Visual timeline of allocations.

- **Dashboards & Analytics**
  - **Main Dashboard:** Overview of total employees, projects, and active allocations.
  - **Bench Management:** Dedicated view for employees currently on the bench to facilitate quick staffing.

- **Authentication & Security**
  - Secure User Login/Signup.
  - Role-Based Access Control (Admin, Manager, Employee).
  - Secure password hashing and token-based authentication.

## Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite (Default) / SQLAlchemy ORM
- **Migrations:** Flask-Migrate
- **Authentication:** Flask-JWT-Extended
- **Frontend:** HTML5, CSS3, JavaScript (Jinja2 Templates)

## Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd WorkForceOptix
   ```

2. **Set Up Virtual Environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   Initialize and upgrade the database.
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

5. **Seed Initial Data**
   Create an admin user and initial data.
   ```bash
   python seed.py
   ```
   *This will create a default admin user:*
   - **Username:** `admin`
   - **Password:** `admin123`

## Running the Application

1. **Start the Flask Server**
   ```bash
   python run.py
   ```

2. **Access the App**
   Open your browser and navigate to:
   `http://127.0.0.1:5000`

## Configuration

Environment variables can be set in a `.env` file or directly in the system.
- `SECRET_KEY`: App secret key.
- `DATABASE_URL`: Database connection string (defaults to local SQLite).
- `JWT_SECRET_KEY`: Secret key for JWT tokens.

## License

This project is open-source and available for personal and educational use.
