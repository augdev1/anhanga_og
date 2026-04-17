from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from app import db
from app.models import User
from database import get_db, UserORM, ReportORM, AuthTokenORM
import secrets
from datetime import datetime

bp = Blueprint("main", __name__)

# ============ API ENDPOINTS ============

def _extract_bearer_token():
    """Extract token from Authorization header or session."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return session.get("token")


@bp.route("/api/auth/register", methods=["POST"])
def api_register():
    """Register new user."""
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    data_nasc = data.get("data_nasc", "").strip()
    telefone = data.get("telefone", "").strip()
    username = data.get("username", "").strip().lower()
    password = data.get("password", "")

    if not name or not username or not password:
        return jsonify({"status": "error", "detail": "Preencha todos os campos obrigatórios"}), 400

    db_session = get_db()
    try:
        existing = db_session.query(UserORM).filter(UserORM.username == username).first()
        if existing:
            return jsonify({"status": "error", "detail": "Usuário já existe"}), 409

        user = UserORM(
            username=username,
            name=name,
            email=email if email else None,
            data_nasc=data_nasc if data_nasc else None,
            telefone=telefone if telefone else None,
            password_hash=password,
            user_type=0
        )
        db_session.add(user)
        db_session.commit()

        # Create token
        token = secrets.token_urlsafe(24)
        auth_token = AuthTokenORM(token=token, username=username, name=name)
        db_session.add(auth_token)
        db_session.commit()

        session["token"] = token
        session["username"] = username

        return jsonify({
            "status": "ok",
            "token": token,
            "token_type": "bearer",
            "user": {"username": username, "name": name, "user_type": 0}
        })
    finally:
        db_session.close()


@bp.route("/api/auth/login", methods=["POST"])
def api_login():
    """Login user."""
    data = request.get_json() or {}
    username = data.get("username", "").strip().lower()
    password = data.get("password", "")
    
    if not username or not password:
        return jsonify({"status": "error", "detail": "Username e password são obrigatórios"}), 400
    
    db_session = get_db()
    try:
        user = db_session.query(UserORM).filter(UserORM.username == username).first()
        if not user or user.password_hash != password:
            return jsonify({"status": "error", "detail": "Credenciais inválidas"}), 401
        
        token = secrets.token_urlsafe(24)
        auth_token = AuthTokenORM(token=token, username=username, name=user.name or username)
        db_session.add(auth_token)
        db_session.commit()
        
        session["token"] = token
        session["username"] = username
        
        return jsonify({
            "status": "ok",
            "token": token,
            "token_type": "bearer",
            "user": {"username": username, "name": user.name or username, "user_type": user.user_type}
        })
    finally:
        db_session.close()


@bp.route("/api/auth/me", methods=["GET"])
def api_me():
    """Get current user info."""
    token = _extract_bearer_token()
    if not token:
        return jsonify({"status": "error", "detail": "Token ausente"}), 401

    db_session = get_db()
    try:
        auth_token = db_session.query(AuthTokenORM).filter(AuthTokenORM.token == token).first()
        if not auth_token:
            return jsonify({"status": "error", "detail": "Token inválido"}), 401

        # Get full user info
        user = db_session.query(UserORM).filter(UserORM.username == auth_token.username).first()
        if not user:
            return jsonify({"status": "error", "detail": "Usuário não encontrado"}), 404

        return jsonify({
            "status": "ok",
            "user": {
                "id": user.id,
                "username": user.username,
                "name": user.name,
                "email": user.email,
                "data_nasc": user.data_nasc,
                "telefone": user.telefone,
                "foto_url": user.foto_url,
                "user_type": user.user_type
            }
        })
    finally:
        db_session.close()


@bp.route("/api/auth/logout", methods=["POST"])
def api_logout():
    """Logout user."""
    token = _extract_bearer_token()
    db_session = get_db()
    try:
        if token:
            db_session.query(AuthTokenORM).filter(AuthTokenORM.token == token).delete()
            db_session.commit()
        session.clear()
        return jsonify({"status": "ok"})
    finally:
        db_session.close()


@bp.route("/api/reportar/queimada", methods=["POST"])
def api_reportar():
    """Report fire/queimada with user type logic.

    Tipo 0 (normal): Reporta -> alerta (1). Outro usuario confirma -> suspeito (2).
                     Outro usuario confirma -> confirmado (3). Mesmo usuario nao pode confirmar.
    Tipo 1 (especial): Reporta -> confirmado (3) imediatamente.
    Distancia: ~500m (0.0045 graus)
    """
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)

    if lat is None or lon is None:
        return jsonify({"status": "error", "detail": "lat e lon são obrigatórios"}), 400

    token = _extract_bearer_token()
    if not token:
        return jsonify({"status": "error", "detail": "Autenticação necessária"}), 401

    db_session = get_db()
    try:
        # Get user info
        auth_token = db_session.query(AuthTokenORM).filter(AuthTokenORM.token == token).first()
        if not auth_token:
            return jsonify({"status": "error", "detail": "Token inválido"}), 401

        username = auth_token.username
        user = db_session.query(UserORM).filter(UserORM.username == username).first()
        if not user:
            return jsonify({"status": "error", "detail": "Usuário não encontrado"}), 404

        user_id = user.id
        user_type = user.user_type  # 0 = normal, 1 = especial

        # 500m em graus (aproximadamente)
        DISTANCE_THRESHOLD = 0.0045

        # Verificar se existe reporte na mesma área
        nearby_report = db_session.query(ReportORM).filter(
            (ReportORM.lat >= lat - DISTANCE_THRESHOLD) &
            (ReportORM.lat <= lat + DISTANCE_THRESHOLD) &
            (ReportORM.lon >= lon - DISTANCE_THRESHOLD) &
            (ReportORM.lon <= lon + DISTANCE_THRESHOLD)
        ).order_by(ReportORM.created_at.desc()).first()

        if nearby_report:
            # Ja existe reporte nesta area - verificar se usuario ja confirmou
            user_confirmed = db_session.query(ReportORM).filter(
                (ReportORM.lat >= lat - DISTANCE_THRESHOLD) &
                (ReportORM.lat <= lat + DISTANCE_THRESHOLD) &
                (ReportORM.lon >= lon - DISTANCE_THRESHOLD) &
                (ReportORM.lon <= lon + DISTANCE_THRESHOLD) &
                (ReportORM.user_id == user_id)
            ).first()

            if user_confirmed:
                return jsonify({
                    "status": "error",
                    "detail": "Você já reportou/confirmou nesta localização"
                }), 409

            # Usuario diferente - contar como confirmacao
            # Contar usuarios unicos que confirmaram
            unique_users = db_session.query(ReportORM.user_id).filter(
                (ReportORM.lat >= lat - DISTANCE_THRESHOLD) &
                (ReportORM.lat <= lat + DISTANCE_THRESHOLD) &
                (ReportORM.lon >= lon - DISTANCE_THRESHOLD) &
                (ReportORM.lon <= lon + DISTANCE_THRESHOLD)
            ).distinct().count()

            new_count = unique_users + 1

            # Determinar nivel baseado no count
            if new_count >= 3:
                nivel = "confirmado"
            elif new_count >= 2:
                nivel = "suspeito"
            else:
                nivel = "alerta"

            # Atualizar o reporte original com novo nivel
            nearby_report.nivel = nivel
            nearby_report.count = new_count

            # Criar novo registro de confirmacao
            file = request.files.get("file")
            filename = file.filename if file else None

            confirm_report = ReportORM(
                lat=lat, lon=lon, user_id=user_id, username=username,
                filename=filename, nivel=nivel, count=new_count,
                is_confirmation=True  # Marcar como confirmacao
            )
            db_session.add(confirm_report)
            db_session.commit()

            return jsonify({
                "status": "ok",
                "nivel": nivel,
                "usuarios": new_count,
                "message": f"Confirmação registrada! Status: {nivel}"
            })

        else:
            # Novo reporte nesta area
            file = request.files.get("file")
            filename = file.filename if file else None

            # Tipo 1 (especial): ja vira confirmado
            # Tipo 0 (normal): começa como alerta
            if user_type == 1:
                nivel = "confirmado"
                count = 3
                message = "Reporte registrado como CONFIRMADO (usuário especial)"
            else:
                nivel = "alerta"
                count = 1
                message = "Reporte registrado como ALERTA. Aguardando confirmações."

            report = ReportORM(
                lat=lat, lon=lon, user_id=user_id, username=username,
                filename=filename, nivel=nivel, count=count
            )
            db_session.add(report)
            db_session.commit()

            return jsonify({
                "status": "ok",
                "nivel": nivel,
                "usuarios": count,
                "message": message
            })
    finally:
        db_session.close()


@bp.route("/api/reportar/lista", methods=["GET"])
@bp.route("/api/reportar/queimadas/todos", methods=["GET"])
def api_reportar_lista():
    """List recent reports."""
    limit = request.args.get("limit", 50, type=int)
    
    db_session = get_db()
    try:
        reports = db_session.query(ReportORM).order_by(ReportORM.created_at.desc()).limit(limit).all()
        data = [{
            "id": r.id, "lat": r.lat, "lon": r.lon,
            "username": r.username, "filename": r.filename,
            "nivel": r.nivel, "count": r.count,
            "timestamp": r.created_at.isoformat() if r.created_at else None
        } for r in reports]
        return jsonify({"status": "ok", "count": len(data), "data": data})
    finally:
        db_session.close()


@bp.route("/api/reportar/queimadas/mapa", methods=["GET"])
def api_reportar_mapa():
    """List reports as GeoJSON for map."""
    status = request.args.get("status", "todos")
    
    db_session = get_db()
    try:
        query = db_session.query(ReportORM)
        if status != "todos":
            query = query.filter(ReportORM.nivel == status)
        
        reports = query.order_by(ReportORM.created_at.desc()).all()
        
        features = []
        for r in reports:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [r.lon, r.lat]
                },
                "properties": {
                    "id": r.id,
                    "nivel": r.nivel,
                    "count": r.count,
                    "username": r.username,
                    "timestamp": r.created_at.isoformat() if r.created_at else None
                }
            })
        
        return jsonify({
            "type": "FeatureCollection",
            "features": features
        })
    finally:
        db_session.close()


# Real API endpoints for alerts (GFW and FIRMS)
@bp.route("/api/alertas/unificado", methods=["GET"])
def api_alertas_unificado():
    """Get unified alerts from GFW and FIRMS."""
    try:
        # Import alert modules
        import gfw_alerts
        import firms_alerts

        # Get parameters
        days = request.args.get("days", 7, type=int)
        confidence = request.args.get("confidence", "medium")

        # Fetch GFW alerts (deforestation)
        gfw_data = gfw_alerts.get_alerts_amazon(
            token=gfw_alerts.TOKEN,
            days=days,
            confidence=confidence
        ) or []

        # Fetch FIRMS alerts (fires)
        firms_geojson = firms_alerts.fetch_firms_alerts(
            days=days,
            min_confidence=50 if confidence == "medium" else 80 if confidence == "high" else 0
        )
        firms_features = firms_geojson.get("features", [])

        # Convert to unified format
        unified_alerts = []

        # Add GFW alerts
        for alert in gfw_data:
            unified_alerts.append({
                "latitude": alert.get("latitude"),
                "longitude": alert.get("longitude"),
                "alert_date": alert.get("alert_date"),
                "confidence": alert.get("confidence", "medium"),
                "source": "GFW",
                "alert_type": alert.get("alert_type", "deforestation"),
                "intensity": None
            })

        # Add FIRMS alerts
        for feature in firms_features:
            props = feature.get("properties", {})
            unified_alerts.append({
                "latitude": props.get("latitude"),
                "longitude": props.get("longitude"),
                "alert_date": props.get("alert_date"),
                "confidence": props.get("confidence", 50),
                "source": "FIRMS",
                "alert_type": "fire",
                "intensity": props.get("frp")
            })

        return jsonify({
            "status": "ok",
            "count": len(unified_alerts),
            "sources": ["GFW", "FIRMS"],
            "data": unified_alerts
        })

    except Exception as e:
        print(f"[Alertas Error] {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "ok",
            "count": 0,
            "data": [],
            "error": str(e)
        })


@bp.route("/api/alertas/landsat", methods=["GET"])
def api_alertas_landsat():
    """Get Landsat alerts (using FIRMS as proxy for thermal alerts)."""
    try:
        import firms_alerts

        days = request.args.get("days", 7, type=int)

        # ALWAYS use Amazon region bbox - ignore any bbox parameter
        bbox_tuple = firms_alerts.AMAZON_BBOX

        # Fetch alerts
        firms_geojson = firms_alerts.fetch_firms_alerts(
            days=days,
            bbox=bbox_tuple,
            limit=500
        )

        return jsonify(firms_geojson)

    except Exception as e:
        print(f"[Landsat Error] {e}")
        return jsonify({"type": "FeatureCollection", "features": []})


@bp.route("/api/alertas/mapa", methods=["GET"])
def api_alertas_mapa():
    """Get all alerts for map display (Amazon only)."""
    try:
        import gfw_alerts
        import firms_alerts

        days = request.args.get("days", 7, type=int)

        # ALWAYS use Amazon region - ignore any bbox parameter
        bbox_tuple = firms_alerts.AMAZON_BBOX

        # Get FIRMS fire alerts
        firms_geojson = firms_alerts.fetch_firms_alerts(
            days=days,
            bbox=bbox_tuple,
            limit=300
        )

        for feature in firms_geojson.get("features", []):
            props = feature.get("properties", {})
            geom = feature.get("geometry", {})
            coords = geom.get("coordinates", [0, 0])

            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": coords
                },
                "properties": {
                    "source": "FIRMS",
                    "type": "fire",
                    "confidence": props.get("confidence", 0),
                    "date": props.get("alert_date", ""),
                    "intensity": props.get("frp", 0),
                    "color": "#ef4444"  # Red for fire
                }
            })

        # Get GFW deforestation alerts
        gfw_alerts_list = gfw_alerts.get_alerts_amazon(
            token=gfw_alerts.TOKEN,
            days=days
        ) or []

        for alert in gfw_alerts_list[:200]:  # Limit to 200
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [alert.get("longitude", 0), alert.get("latitude", 0)]
                },
                "properties": {
                    "source": "GFW",
                    "type": "deforestation",
                    "confidence": alert.get("confidence", "medium"),
                    "date": alert.get("alert_date", ""),
                    "intensity": None,
                    "color": "#f59e0b"  # Orange for deforestation
                }
            })

        return jsonify({
            "type": "FeatureCollection",
            "count": len(features),
            "features": features
        })

    except Exception as e:
        print(f"[Mapa Error] {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "type": "FeatureCollection",
            "count": 0,
            "features": []
        })


# ============ TEMPLATE ROUTES ============


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/login.html")
def login():
    return render_template("login.html")


@bp.route("/register.html")
def register():
    return render_template("register.html")


@bp.route("/mapa.html")
def mapa():
    return render_template("mapa.html")


@bp.route("/monitoramento.html")
def monitoramento():
    return render_template("monitoramento.html")


@bp.route("/filtros.html")
def filtros():
    return render_template("filtros.html")


@bp.route("/insights.html")
def insights():
    return render_template("insights.html")


@bp.route("/reportar.html")
def reportar():
    return render_template("reportar.html")


# ============ ADMIN ENDPOINTS ============

@bp.route("/admin.html")
def admin_page():
    """Admin page for managing users."""
    return render_template("admin.html")


@bp.route("/api/admin/users", methods=["GET"])
def api_admin_list_users():
    """List all users (admin only)."""
    token = _extract_bearer_token()
    if not token:
        return jsonify({"status": "error", "detail": "Autenticação necessária"}), 401

    db_session = get_db()
    try:
        # Verify admin
        auth_token = db_session.query(AuthTokenORM).filter(AuthTokenORM.token == token).first()
        if not auth_token:
            return jsonify({"status": "error", "detail": "Token inválido"}), 401

        user = db_session.query(UserORM).filter(UserORM.username == auth_token.username).first()
        if not user or user.user_type != 1:
            return jsonify({"status": "error", "detail": "Acesso restrito a administradores"}), 403

        # List all users
        users = db_session.query(UserORM).order_by(UserORM.created_at.desc()).all()
        data = [{
            "id": u.id,
            "username": u.username,
            "name": u.name,
            "user_type": u.user_type,
            "created_at": u.created_at.isoformat() if u.created_at else None
        } for u in users]

        return jsonify({"status": "ok", "count": len(data), "data": data})
    finally:
        db_session.close()


@bp.route("/api/admin/users/<int:user_id>/promote", methods=["POST"])
def api_admin_promote_user(user_id):
    """Promote user to type 1 (admin only)."""
    token = _extract_bearer_token()
    if not token:
        return jsonify({"status": "error", "detail": "Autenticação necessária"}), 401

    db_session = get_db()
    try:
        # Verify admin
        auth_token = db_session.query(AuthTokenORM).filter(AuthTokenORM.token == token).first()
        if not auth_token:
            return jsonify({"status": "error", "detail": "Token inválido"}), 401

        admin_user = db_session.query(UserORM).filter(UserORM.username == auth_token.username).first()
        if not admin_user or admin_user.user_type != 1:
            return jsonify({"status": "error", "detail": "Acesso restrito a administradores"}), 403

        # Find target user
        target_user = db_session.query(UserORM).filter(UserORM.id == user_id).first()
        if not target_user:
            return jsonify({"status": "error", "detail": "Usuário não encontrado"}), 404

        # Promote to type 1
        target_user.user_type = 1
        db_session.commit()

        return jsonify({
            "status": "ok",
            "message": f"Usuário {target_user.username} promovido para tipo especial",
            "user": {
                "id": target_user.id,
                "username": target_user.username,
                "user_type": target_user.user_type
            }
        })
    finally:
        db_session.close()


@bp.route("/api/admin/users/<int:user_id>/demote", methods=["POST"])
def api_admin_demote_user(user_id):
    """Demote user to type 0 (admin only)."""
    token = _extract_bearer_token()
    if not token:
        return jsonify({"status": "error", "detail": "Autenticação necessária"}), 401

    db_session = get_db()
    try:
        # Verify admin
        auth_token = db_session.query(AuthTokenORM).filter(AuthTokenORM.token == token).first()
        if not auth_token:
            return jsonify({"status": "error", "detail": "Token inválido"}), 401

        admin_user = db_session.query(UserORM).filter(UserORM.username == auth_token.username).first()
        if not admin_user or admin_user.user_type != 1:
            return jsonify({"status": "error", "detail": "Acesso restrito a administradores"}), 403

        # Find target user
        target_user = db_session.query(UserORM).filter(UserORM.id == user_id).first()
        if not target_user:
            return jsonify({"status": "error", "detail": "Usuário não encontrado"}), 404

        # Prevent demoting self
        if target_user.id == admin_user.id:
            return jsonify({"status": "error", "detail": "Não pode rebaixar a si mesmo"}), 400

        # Demote to type 0
        target_user.user_type = 0
        db_session.commit()

        return jsonify({
            "status": "ok",
            "message": f"Usuário {target_user.username} rebaixado para tipo normal",
            "user": {
                "id": target_user.id,
                "username": target_user.username,
                "user_type": target_user.user_type
            }
        })
    finally:
        db_session.close()


@bp.route("/perfil.html")
def perfil_page():
    """User profile page."""
    return render_template("perfil.html")


@bp.route("/api/user/profile", methods=["PUT"])
def api_update_profile():
    """Update user profile data."""
    token = _extract_bearer_token()
    if not token:
        return jsonify({"status": "error", "detail": "Autenticação necessária"}), 401

    db_session = get_db()
    try:
        auth_token = db_session.query(AuthTokenORM).filter(AuthTokenORM.token == token).first()
        if not auth_token:
            return jsonify({"status": "error", "detail": "Token inválido"}), 401

        user = db_session.query(UserORM).filter(UserORM.username == auth_token.username).first()
        if not user:
            return jsonify({"status": "error", "detail": "Usuário não encontrado"}), 404

        data = request.get_json() or {}

        # Update fields
        if "name" in data:
            user.name = data["name"].strip()
        if "email" in data:
            email = data["email"].strip()
            if email:
                # Check if email is already used by another user
                existing = db_session.query(UserORM).filter(
                    UserORM.email == email,
                    UserORM.id != user.id
                ).first()
                if existing:
                    return jsonify({"status": "error", "detail": "Email já está em uso"}), 409
                user.email = email
        if "data_nasc" in data:
            user.data_nasc = data["data_nasc"].strip() if data["data_nasc"] else None
        if "telefone" in data:
            user.telefone = data["telefone"].strip() if data["telefone"] else None

        db_session.commit()

        return jsonify({
            "status": "ok",
            "message": "Perfil atualizado com sucesso",
            "user": {
                "id": user.id,
                "username": user.username,
                "name": user.name,
                "email": user.email,
                "data_nasc": user.data_nasc,
                "telefone": user.telefone,
                "foto_url": user.foto_url,
                "user_type": user.user_type
            }
        })
    finally:
        db_session.close()


@bp.route("/api/user/password", methods=["PUT"])
def api_change_password():
    """Change user password."""
    token = _extract_bearer_token()
    if not token:
        return jsonify({"status": "error", "detail": "Autenticação necessária"}), 401

    db_session = get_db()
    try:
        auth_token = db_session.query(AuthTokenORM).filter(AuthTokenORM.token == token).first()
        if not auth_token:
            return jsonify({"status": "error", "detail": "Token inválido"}), 401

        user = db_session.query(UserORM).filter(UserORM.username == auth_token.username).first()
        if not user:
            return jsonify({"status": "error", "detail": "Usuário não encontrado"}), 404

        data = request.get_json() or {}
        current_password = data.get("current_password", "")
        new_password = data.get("new_password", "")

        if not current_password or not new_password:
            return jsonify({"status": "error", "detail": "Senha atual e nova senha são obrigatórias"}), 400

        if user.password_hash != current_password:
            return jsonify({"status": "error", "detail": "Senha atual incorreta"}), 401

        user.password_hash = new_password
        db_session.commit()

        return jsonify({
            "status": "ok",
            "message": "Senha alterada com sucesso"
        })
    finally:
        db_session.close()


@bp.route("/api/user/foto", methods=["POST"])
def api_upload_foto():
    """Upload user profile photo (base64)."""
    token = _extract_bearer_token()
    if not token:
        return jsonify({"status": "error", "detail": "Autenticação necessária"}), 401

    db_session = get_db()
    try:
        auth_token = db_session.query(AuthTokenORM).filter(AuthTokenORM.token == token).first()
        if not auth_token:
            return jsonify({"status": "error", "detail": "Token inválido"}), 401

        user = db_session.query(UserORM).filter(UserORM.username == auth_token.username).first()
        if not user:
            return jsonify({"status": "error", "detail": "Usuário não encontrado"}), 404

        file = request.files.get("file")
        if not file:
            return jsonify({"status": "error", "detail": "Nenhum arquivo enviado"}), 400

        # Read and convert to base64
        import base64
        file_content = file.read()
        base64_foto = base64.b64encode(file_content).decode('utf-8')

        # Store as data URL
        mime_type = file.content_type or "image/jpeg"
        foto_url = f"data:{mime_type};base64,{base64_foto}"

        user.foto_url = foto_url
        db_session.commit()

        return jsonify({
            "status": "ok",
            "message": "Foto atualizada com sucesso",
            "foto_url": foto_url
        })
    finally:
        db_session.close()
