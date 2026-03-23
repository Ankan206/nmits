"""
app.py  –  Network Monitoring & Issue Ticketing System
"""
from flask import (Flask, render_template, redirect, url_for,
                   flash, request, jsonify)
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)
from flask_wtf.csrf import CSRFProtect
from datetime import datetime, timedelta

from config import Config
from models import db, User, NetworkDevice, NetworkLog, Ticket, TicketComment
from forms import (LoginForm, RegisterForm, DeviceForm,
                   TicketForm, CommentForm, UpdateTicketForm)
from network_monitor import ping_host, start_scheduler


# ── App factory ─────────────────────────────────────────────────────────────

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    csrf = CSRFProtect(app)

    login_manager = LoginManager(app)
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()
        _seed_admin()

    start_scheduler(app, interval_seconds=60)
    return app


def _seed_admin():
    """Create a default admin account if none exists."""
    if not User.query.filter_by(role='admin').first():
        admin = User(username='admin', email='admin@nmits.local', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()


app = create_app()


# ── Auth routes ─────────────────────────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken.', 'danger')
        elif User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'danger')
        else:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(request.args.get('next') or url_for('dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ── Dashboard ────────────────────────────────────────────────────────────────

@app.route('/')
@login_required
def dashboard():
    devices  = NetworkDevice.query.all()
    tickets  = Ticket.query.order_by(Ticket.created_at.desc()).limit(10).all()

    # Latest status per device
    device_status = {}
    for d in devices:
        log = (NetworkLog.query
               .filter_by(device_id=d.id)
               .order_by(NetworkLog.checked_at.desc())
               .first())
        device_status[d.id] = log

    stats = {
        'total_devices': len(devices),
        'up':            sum(1 for d in devices
                             if device_status.get(d.id) and
                             device_status[d.id].status == 'UP'),
        'down':          sum(1 for d in devices
                             if device_status.get(d.id) and
                             device_status[d.id].status == 'DOWN'),
        'open_tickets':  Ticket.query.filter_by(status='Open').count(),
        'total_tickets': Ticket.query.count(),
    }

    return render_template('dashboard.html',
                           devices=devices,
                           device_status=device_status,
                           tickets=tickets,
                           stats=stats)


# ── Network devices ──────────────────────────────────────────────────────────

@app.route('/devices')
@login_required
def devices():
    all_devices = NetworkDevice.query.all()
    device_status = {}
    for d in all_devices:
        log = (NetworkLog.query
               .filter_by(device_id=d.id)
               .order_by(NetworkLog.checked_at.desc())
               .first())
        device_status[d.id] = log
    form = DeviceForm()
    return render_template('devices.html',
                           devices=all_devices,
                           device_status=device_status,
                           form=form)


@app.route('/devices/add', methods=['POST'])
@login_required
def add_device():
    form = DeviceForm()
    if form.validate_on_submit():
        device = NetworkDevice(
            name=form.name.data,
            host=form.host.data,
            description=form.description.data,
            added_by=current_user.id
        )
        db.session.add(device)
        db.session.commit()
        flash(f'Device "{device.name}" added.', 'success')
    else:
        flash('Invalid form data.', 'danger')
    return redirect(url_for('devices'))


@app.route('/devices/<int:device_id>/delete', methods=['POST'])
@login_required
def delete_device(device_id):
    device = NetworkDevice.query.get_or_404(device_id)
    if not current_user.is_admin:
        flash('Admin access required.', 'danger')
        return redirect(url_for('devices'))
    db.session.delete(device)
    db.session.commit()
    flash('Device removed.', 'success')
    return redirect(url_for('devices'))


@app.route('/devices/<int:device_id>/logs')
@login_required
def device_logs(device_id):
    device = NetworkDevice.query.get_or_404(device_id)
    logs   = (NetworkLog.query
              .filter_by(device_id=device_id)
              .order_by(NetworkLog.checked_at.desc())
              .limit(100).all())
    return render_template('device_logs.html', device=device, logs=logs)


# ── Live ping (AJAX) ─────────────────────────────────────────────────────────

@app.route('/api/ping', methods=['POST'])
@login_required
def api_ping():
    data = request.get_json()
    host = (data or {}).get('host', '').strip()
    if not host:
        return jsonify({'error': 'No host provided'}), 400

    result = ping_host(host)

    # Persist log if host belongs to a tracked device
    device = NetworkDevice.query.filter_by(host=host).first()
    if device:
        log = NetworkLog(device_id=device.id,
                         status=result['status'],
                         latency_ms=result['latency_ms'])
        db.session.add(log)
        db.session.commit()

    return jsonify(result)


@app.route('/api/devices/status')
@login_required
def api_devices_status():
    """Return JSON list of all devices with their latest status."""
    devices = NetworkDevice.query.all()
    out = []
    for d in devices:
        log = (NetworkLog.query
               .filter_by(device_id=d.id)
               .order_by(NetworkLog.checked_at.desc())
               .first())
        out.append({
            'id':         d.id,
            'name':       d.name,
            'host':       d.host,
            'status':     log.status if log else 'UNKNOWN',
            'latency_ms': log.latency_ms if log else None,
            'checked_at': log.checked_at.isoformat() if log else None,
        })
    return jsonify(out)


@app.route('/api/stats')
@login_required
def api_stats():
    """Latency chart data for the last 24 h."""
    since   = datetime.utcnow() - timedelta(hours=24)
    devices = NetworkDevice.query.all()
    result  = {}
    for d in devices:
        logs = (NetworkLog.query
                .filter(NetworkLog.device_id == d.id,
                        NetworkLog.checked_at >= since)
                .order_by(NetworkLog.checked_at)
                .all())
        result[d.name] = [
            {'t': l.checked_at.isoformat(), 'ms': l.latency_ms}
            for l in logs if l.latency_ms is not None
        ]
    return jsonify(result)


# ── Tickets ──────────────────────────────────────────────────────────────────

@app.route('/tickets')
@login_required
def tickets():
    if current_user.is_admin:
        all_tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    else:
        all_tickets = (Ticket.query
                       .filter_by(user_id=current_user.id)
                       .order_by(Ticket.created_at.desc())
                       .all())
    form = TicketForm()
    form.device_id.choices = [(0, '-- None --')] + [
        (d.id, d.name) for d in NetworkDevice.query.all()
    ]
    return render_template('tickets.html', tickets=all_tickets, form=form)


@app.route('/tickets/create', methods=['POST'])
@login_required
def create_ticket():
    form = TicketForm()
    form.device_id.choices = [(0, '-- None --')] + [
        (d.id, d.name) for d in NetworkDevice.query.all()
    ]
    if form.validate_on_submit():
        ticket = Ticket(
            title       = form.title.data,
            description = form.description.data,
            priority    = form.priority.data,
            device_id   = form.device_id.data or None,
            user_id     = current_user.id
        )
        db.session.add(ticket)
        db.session.commit()
        flash('Ticket created.', 'success')
    else:
        flash('Please fill all required fields.', 'danger')
    return redirect(url_for('tickets'))


@app.route('/tickets/<int:ticket_id>')
@login_required
def ticket_detail(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if not current_user.is_admin and ticket.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('tickets'))
    comment_form = CommentForm()
    update_form  = UpdateTicketForm(obj=ticket)
    return render_template('ticket_detail.html',
                           ticket=ticket,
                           comment_form=comment_form,
                           update_form=update_form)


@app.route('/tickets/<int:ticket_id>/comment', methods=['POST'])
@login_required
def add_comment(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    form   = CommentForm()
    if form.validate_on_submit():
        c = TicketComment(ticket_id=ticket_id,
                          user_id=current_user.id,
                          comment=form.comment.data)
        db.session.add(c)
        db.session.commit()
        flash('Comment added.', 'success')
    return redirect(url_for('ticket_detail', ticket_id=ticket_id))


@app.route('/tickets/<int:ticket_id>/update', methods=['POST'])
@login_required
def update_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if not current_user.is_admin:
        flash('Admin access required.', 'danger')
        return redirect(url_for('ticket_detail', ticket_id=ticket_id))
    form = UpdateTicketForm()
    if form.validate_on_submit():
        ticket.status     = form.status.data
        ticket.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Ticket status updated.', 'success')
    return redirect(url_for('ticket_detail', ticket_id=ticket_id))


@app.route('/tickets/<int:ticket_id>/delete', methods=['POST'])
@login_required
def delete_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if not current_user.is_admin and ticket.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('tickets'))
    db.session.delete(ticket)
    db.session.commit()
    flash('Ticket deleted.', 'success')
    return redirect(url_for('tickets'))


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
