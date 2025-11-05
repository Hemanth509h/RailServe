from flask import Flask
from flask_cors import CORS
from models.database import db
import os

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///railway.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'database-api-secret-key-2025')

db.init_app(app)

from routes import (
    users, stations, trains, routes as train_routes, bookings, 
    payments, waitlist, tatkal, refunds, complaints, performance
)

app.register_blueprint(users.bp)
app.register_blueprint(stations.bp)
app.register_blueprint(trains.bp)
app.register_blueprint(train_routes.bp)
app.register_blueprint(bookings.bp)
app.register_blueprint(payments.bp)
app.register_blueprint(waitlist.bp)
app.register_blueprint(tatkal.bp)
app.register_blueprint(refunds.bp)
app.register_blueprint(complaints.bp)
app.register_blueprint(performance.bp)

@app.route('/')
def index():
    return {
        'status': 'running',
        'message': 'Railway Database API',
        'version': '1.0.0'
    }

@app.route('/health')
def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
