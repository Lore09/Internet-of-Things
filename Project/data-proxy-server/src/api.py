from flask import render_template, request, redirect, url_for, Blueprint

class DashboardCard:
    def __init__(self, title, label):
        self.title = title
        self.label = label

cards = [
    DashboardCard('Card 1', 'V1'),
    DashboardCard('Card 2', 'V2'),
    DashboardCard('Card 3', 'V3'),
    DashboardCard('Card 4', 'V4')
]


api = Blueprint('api', __name__, template_folder='../templates', static_folder='../static')

@api.route('/')
def dashboard():
    return render_template('dashboard.html', cards=cards)

@api.route('/form', methods=['POST'])
def handle_form():
    data = request.form
    print(data)  # For demonstration, you can handle data as needed.
    return redirect(url_for('dashboard')) 