from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from app import db
from app.models import User
from database import get_db, UserORM, ReportORM, AuthTokenORM, ActivityLogORM, log_activity, get_online_users, get_recent_activities
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
    """Register new user with approval flow."""
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    data_nasc = data.get("data_nasc", "").strip()
    telefone = data.get("telefone", "").strip()
    username = data.get("username", "").strip().lower()
    password = data.get("password", "")
    foto_url = data.get("foto_url", "").strip()

    # Validar campos obrigatórios
    if not name:
        return jsonify({"status": "error", "detail": "Nome é obrigatório"}), 400
    if not email:
        return jsonify({"status": "error", "detail": "Email é obrigatório"}), 400
    if not data_nasc:
        return jsonify({"status": "error", "detail": "Data de nascimento é obrigatória"}), 400
    if not telefone:
        return jsonify({"status": "error", "detail": "Telefone é obrigatório"}), 400
    if not username:
        return jsonify({"status": "error", "detail": "Username é obrigatório"}), 400
    if not password:
        return jsonify({"status": "error", "detail": "Senha é obrigatória"}), 400
    if not foto_url:
        return jsonify({"status": "error", "detail": "Foto de perfil é obrigatória"}), 400

    # Validar senha mínima 8 caracteres
    if len(password) < 8:
        return jsonify({"status": "error", "detail": "Senha deve ter no mínimo 8 caracteres"}), 400

    # Validar idade mínima 12 anos
    try:
        from datetime import datetime
        nasc = datetime.strptime(data_nasc, "%Y-%m-%d")
        hoje = datetime.now()
        idade = hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
        if idade < 12:
            return jsonify({"status": "error", "detail": "É necessário ter no mínimo 12 anos para se cadastrar"}), 400
    except ValueError:
        return jsonify({"status": "error", "detail": "Data de nascimento inválida. Use formato AAAA-MM-DD"}), 400

    db_session = get_db()
    try:
        # Verificar username duplicado
        existing_user = db_session.query(UserORM).filter(UserORM.username == username).first()
        if existing_user:
            return jsonify({"status": "error", "detail": "Username já existe"}), 409

        # Verificar email duplicado
        existing_email = db_session.query(UserORM).filter(UserORM.email == email).first()
        if existing_email:
            return jsonify({"status": "error", "detail": "Email já cadastrado"}), 409

        user = UserORM(
            username=username,
            name=name,
            email=email,
            data_nasc=data_nasc,
            telefone=telefone,
            password_hash=password,
            foto_url=foto_url,
            user_type=0  # 0 = pendente (aguardando aprovação do admin)
        )
        db_session.add(user)
        db_session.commit()

        return jsonify({
            "status": "ok",
            "message": "Cadastro realizado com sucesso! Aguarde aprovação do administrador para acessar o sistema.",
            "user": {"username": username, "name": name, "user_type": 0}
        })
    finally:
        db_session.close()


@bp.route("/api/auth/login", methods=["POST"])
def api_login():
    """Login user with approval check."""
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

        # Verificar se usuário está aprovado (user_type != 0)
        if user.user_type == 0:
            return jsonify({
                "status": "error",
                "detail": "Cadastro pendente de aprovação. Aguarde o administrador ativar sua conta."
            }), 403

        token = secrets.token_urlsafe(24)
        auth_token = AuthTokenORM(token=token, username=username, name=user.name or username)
        db_session.add(auth_token)
        db_session.commit()

        session["token"] = token
        session["username"] = username

        # Registrar atividade de login
        log_activity(
            username=username,
            action="login",
            details="Login realizado com sucesso",
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent", "")[:256]
        )

        return jsonify({
            "status": "ok",
            "token": token,
            "token_type": "bearer",
            "user": {
                "username": username,
                "name": user.name or username,
                "email": user.email,
                "data_nasc": user.data_nasc,
                "telefone": user.telefone,
                "foto_url": user.foto_url,
                "user_type": user.user_type
            }
        })
    finally:
        db_session.close()


@bp.route("/api/auth/validate-recovery", methods=["POST"])
def api_validate_recovery():
    """Valida dados para recuperação de senha (email, nome, data_nasc)."""
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    nome = data.get("nome", "").strip()
    data_nasc = data.get("data_nasc", "").strip()

    if not email or not nome or not data_nasc:
        return jsonify({"status": "error", "detail": "Todos os campos são obrigatórios"}), 400

    db_session = get_db()
    try:
        # Buscar usuário por email
        user = db_session.query(UserORM).filter(UserORM.email == email).first()
        if not user:
            return jsonify({"status": "error", "detail": "Dados não encontrados"}), 404

        # Validar nome e data de nascimento
        if user.name.lower() != nome.lower():
            return jsonify({"status": "error", "detail": "Dados não encontrados"}), 404

        if user.data_nasc != data_nasc:
            return jsonify({"status": "error", "detail": "Dados não encontrados"}), 404

        return jsonify({
            "status": "ok",
            "username": user.username
        })
    finally:
        db_session.close()


@bp.route("/api/auth/reset-password", methods=["POST"])
def api_reset_password():
    """Redefine a senha do usuário após validação."""
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    new_password = data.get("new_password", "").strip()

    if not username or not new_password:
        return jsonify({"status": "error", "detail": "Todos os campos são obrigatórios"}), 400

    if len(new_password) < 8:
        return jsonify({"status": "error", "detail": "A senha deve ter no mínimo 8 caracteres"}), 400

    db_session = get_db()
    try:
        user = db_session.query(UserORM).filter(UserORM.username == username).first()
        if not user:
            return jsonify({"status": "error", "detail": "Usuário não encontrado"}), 404

        user.password_hash = new_password
        db_session.commit()

        return jsonify({"status": "ok", "message": "Senha redefinida com sucesso"})
    except Exception as e:
        db_session.rollback()
        return jsonify({"status": "error", "detail": str(e)}), 500
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
    """Logout user and log activity - remove ALL user tokens."""
    token = _extract_bearer_token()
    db_session = get_db()
    try:
        username = None
        if token:
            # Buscar token para pegar username
            auth_token = db_session.query(AuthTokenORM).filter(AuthTokenORM.token == token).first()
            if auth_token:
                username = auth_token.username
                # Deletar TODOS os tokens deste usuário (logout global)
                deleted = db_session.query(AuthTokenORM).filter(AuthTokenORM.username == username).delete()
                db_session.commit()
                print(f"[LOGOUT] Usuário {username} fez logout. {deleted} token(s) removido(s).")

                # Registrar logout
                log_activity(
                    username=username,
                    action="logout",
                    details="Usuário saiu do sistema",
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get("User-Agent", "")[:256]
                )
            else:
                # Token não existe, deletar o token passado mesmo assim
                db_session.query(AuthTokenORM).filter(AuthTokenORM.token == token).delete()
                db_session.commit()

        session.clear()
        return jsonify({"status": "ok"})
    finally:
        db_session.close()


@bp.route("/api/reportar/queimada", methods=["POST"])
def api_reportar():
    """Report fire/queimada with user type logic.

    Regras:
    - Tipo 0 (pendente): BLOQUEADO - não pode reportar
    - Tipo 1 (ativo): Reporta -> ALERTA. Precisa de 2 confirmações de outros usuários tipo 1:
                      1 confirmação -> SUSPEITO, 2 confirmações -> CONFIRMADO
    - Tipo 2 (especial): Reporta -> CONFIRMADO imediatamente
    - Distancia: ~500m (0.0045 graus)
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
        user_type = user.user_type  # 0 = pendente, 1 = ativo, 2 = especial

        # BLOQUEAR usuários pendentes (tipo 0)
        if user_type == 0:
            return jsonify({
                "status": "error",
                "detail": "Usuário pendente de aprovação não pode reportar"
            }), 403

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

            # Usuario tipo 2 (especial) confirma imediatamente para CONFIRMADO
            if user_type == 2:
                nivel = "confirmado"
                new_count = nearby_report.count + 1
            else:
                # Usuario tipo 1 (ativo) - contar como confirmação normal
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

            # Log atividade
            log_activity(
                username=username,
                action="report_confirm",
                details=f"Confirmou queimada em {lat:.4f}, {lon:.4f} - Status: {nivel}",
                ip_address=request.remote_addr,
                user_agent=request.headers.get("User-Agent", "")[:256]
            )

            return jsonify({
                "status": "ok",
                "nivel": nivel,
                "usuarios": new_count,
                "message": f"Confirmação registrada! Status: {nivel}"
            })

        else:
            # NOVO REPORTE nesta area
            file = request.files.get("file")
            filename = file.filename if file else None

            # Tipo 2 (especial): ja vira confirmado imediatamente
            # Tipo 1 (ativo): começa como alerta, precisa de confirmações
            if user_type == 2:
                nivel = "confirmado"
                count = 3
                message = "Reporte registrado como CONFIRMADO (usuário especial)"
            else:
                nivel = "alerta"
                count = 1
                message = "Reporte registrado como ALERTA. Aguardando confirmações de outros usuários."

            report = ReportORM(
                lat=lat, lon=lon, user_id=user_id, username=username,
                filename=filename, nivel=nivel, count=count
            )
            db_session.add(report)
            db_session.commit()

            # Log atividade
            log_activity(
                username=username,
                action="report_create",
                details=f"Reportou queimada em {lat:.4f}, {lon:.4f} - Status: {nivel}",
                ip_address=request.remote_addr,
                user_agent=request.headers.get("User-Agent", "")[:256]
            )

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


@bp.route("/api/alertas/mapa/clusters", methods=["GET"])
def api_alertas_mapa_clusters():
    """Get clustered alerts for map display."""
    try:
        import gfw_alerts
        import firms_alerts
        import alerts_service

        days = request.args.get("days", 7, type=int)
        confidence = request.args.get("confidence", None)
        eps_km = request.args.get("eps_km", 1.0, type=float)
        min_samples = request.args.get("min_samples", 1, type=int)

        # Get clusters using alerts_service
        from datetime import date
        clusters = alerts_service.get_map_clusters(
            days=days,
            confidence=confidence,
            eps_km=eps_km,
            min_samples=min_samples
        )

        return jsonify({
            "data": clusters,
            "count": len(clusters)
        })

    except Exception as e:
        print(f"[Clusters Error] {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "data": [],
            "count": 0,
            "error": str(e)
        })


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


@bp.route("/recuperar-senha.html")
def recuperar_senha():
    return render_template("recuperar-senha.html")


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
        if not user or user.username != "admin":
            return jsonify({"status": "error", "detail": "Acesso restrito ao usuário admin"}), 403

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
    """Promote user from type 1 to type 2 (ativo -> especial, admin only)."""
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
        if not admin_user or admin_user.username != "admin":
            return jsonify({"status": "error", "detail": "Acesso restrito ao usuário admin"}), 403

        # Find target user
        target_user = db_session.query(UserORM).filter(UserORM.id == user_id).first()
        if not target_user:
            return jsonify({"status": "error", "detail": "Usuário não encontrado"}), 404

        # Only active users (type 1) can be promoted to special (type 2)
        if target_user.user_type != 1:
            return jsonify({"status": "error", "detail": "Apenas usuários ativos (tipo 1) podem ser promovidos"}), 400

        # Promote to type 2 (especial)
        target_user.user_type = 2
        db_session.commit()

        return jsonify({
            "status": "ok",
            "message": f"Usuário {target_user.username} promovido para especial",
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
    """Demote user from type 2 to type 1 (especial -> ativo, admin only)."""
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
        if not admin_user or admin_user.username != "admin":
            return jsonify({"status": "error", "detail": "Acesso restrito ao usuário admin"}), 403

        # Find target user
        target_user = db_session.query(UserORM).filter(UserORM.id == user_id).first()
        if not target_user:
            return jsonify({"status": "error", "detail": "Usuário não encontrado"}), 404

        # Prevent demoting self
        if target_user.id == admin_user.id:
            return jsonify({"status": "error", "detail": "Não pode rebaixar a si mesmo"}), 400

        # Only special users (type 2) can be demoted to active (type 1)
        if target_user.user_type != 2:
            return jsonify({"status": "error", "detail": "Apenas usuários especiais (tipo 2) podem ser rebaixados"}), 400

        # Demote to type 1 (ativo)
        target_user.user_type = 1
        db_session.commit()

        return jsonify({
            "status": "ok",
            "message": f"Usuário {target_user.username} rebaixado para ativo",
            "user": {
                "id": target_user.id,
                "username": target_user.username,
                "user_type": target_user.user_type
            }
        })
    finally:
        db_session.close()


@bp.route("/api/admin/users/<int:user_id>/approve", methods=["POST"])
def api_admin_approve_user(user_id):
    """Approve pending user (type 0 -> 1, admin only)."""
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
        if not admin_user or admin_user.username != "admin":
            return jsonify({"status": "error", "detail": "Acesso restrito ao usuário admin"}), 403

        # Find target user
        target_user = db_session.query(UserORM).filter(UserORM.id == user_id).first()
        if not target_user:
            return jsonify({"status": "error", "detail": "Usuário não encontrado"}), 404

        # Check if already approved
        if target_user.user_type != 0:
            return jsonify({"status": "error", "detail": "Usuário já está ativo ou especial"}), 400

        # Approve user (type 0 -> 1)
        target_user.user_type = 1
        db_session.commit()

        return jsonify({
            "status": "ok",
            "message": f"Usuário {target_user.username} aprovado com sucesso!",
            "user": {
                "id": target_user.id,
                "username": target_user.username,
                "name": target_user.name,
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


# ============ MONITORING ENDPOINTS ============

@bp.route("/api/admin/online-users", methods=["GET"])
def api_admin_online_users():
    """Get users online in last 30 minutes (admin only)."""
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
        if not admin_user or admin_user.username != "admin":
            return jsonify({"status": "error", "detail": "Acesso restrito ao usuário admin"}), 403

        # Get online users
        from datetime import timedelta, datetime
        cutoff = datetime.utcnow() - timedelta(minutes=30)

        online_users = get_online_users(db_session, minutes=30)

        # Debug: verificar tokens e logins no banco
        tokens = db_session.query(AuthTokenORM).filter(AuthTokenORM.created_at >= cutoff).all()
        tokens_count = len(tokens)
        logins_count = db_session.query(ActivityLogORM).filter(
            ActivityLogORM.action == "login",
            ActivityLogORM.created_at >= cutoff
        ).count()

        # Mostrar quais usuários têm tokens ativos
        token_users = [t.username for t in tokens]
        print(f"[DEBUG] Tokens ativos (30min): {tokens_count}")
        print(f"[DEBUG] Usuários com tokens: {token_users}")
        print(f"[DEBUG] Logins recentes (30min): {logins_count}")
        print(f"[DEBUG] Usuários online encontrados: {[u['username'] for u in online_users]}")

        # Preparar debug com horários dos tokens
        tokens_debug = [{"user": t.username, "created": t.created_at.isoformat() if t.created_at else None} for t in tokens[:10]]

        return jsonify({
            "status": "ok",
            "count": len(online_users),
            "users": online_users,
            "debug": {
                "tokens_count": tokens_count,
                "tokens_list": tokens_debug,
                "logins_count": logins_count,
                "cutoff": cutoff.isoformat()
            }
        })
    finally:
        db_session.close()


@bp.route("/api/admin/activities", methods=["GET"])
def api_admin_activities():
    """Get recent user activities (admin only)."""
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
        if not admin_user or admin_user.username != "admin":
            return jsonify({"status": "error", "detail": "Acesso restrito ao usuário admin"}), 403

        # Get activities
        limit = request.args.get("limit", 50, type=int)
        activities = get_recent_activities(db_session, limit=limit)

        return jsonify({
            "status": "ok",
            "count": len(activities),
            "activities": activities
        })
    finally:
        db_session.close()


@bp.route("/api/admin/reports", methods=["GET"])
def api_admin_list_reports():
    """List all fire reports (admin only)."""
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
        if not admin_user or admin_user.username != "admin":
            return jsonify({"status": "error", "detail": "Acesso restrito ao usuário admin"}), 403

        # Get reports
        reports = db_session.query(ReportORM).order_by(ReportORM.created_at.desc()).all()

        reports_data = []
        for report in reports:
            reports_data.append({
                "id": report.id,
                "user_id": report.user_id,
                "username": report.username,
                "latitude": report.lat,
                "longitude": report.lon,
                "nivel": report.nivel,
                "count": report.count,
                "fonte": report.fonte,
                "created_at": report.created_at.isoformat() if report.created_at else None,
                "photo_url": report.filename
            })

        return jsonify({
            "status": "ok",
            "count": len(reports_data),
            "reports": reports_data
        })
    finally:
        db_session.close()


@bp.route("/api/admin/reports/<int:report_id>", methods=["DELETE"])
def api_admin_delete_report(report_id):
    """Delete a fire report (admin only)."""
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
        if not admin_user or admin_user.username != "admin":
            return jsonify({"status": "error", "detail": "Acesso restrito ao usuário admin"}), 403

        # Delete report
        report = db_session.query(ReportORM).filter(ReportORM.id == report_id).first()
        if not report:
            return jsonify({"status": "error", "detail": "Reporte não encontrado"}), 404

        db_session.delete(report)
        db_session.commit()

        # Log activity
        log_activity(db_session, admin_user.id, "report_delete", f"Deletou reporte #{report_id}")

        return jsonify({"status": "ok", "message": "Reporte deletado com sucesso"})
    except Exception as e:
        db_session.rollback()
        return jsonify({"status": "error", "detail": str(e)}), 500
    finally:
        db_session.close()


@bp.route("/api/reportes", methods=["POST"])
def api_reportes_externos():
    """Recebe reportes externos do sistema TUPA."""
    data = request.get_json() or {}

    # Extrair campos do JSON
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    imagem = data.get("imagem")  # base64 opcional
    usuario = data.get("usuario")  # id opcional
    fonte = data.get("fonte", "tupa")
    nivel = data.get("nivel", 1)

    # Validar campos obrigatórios
    if not latitude or not longitude:
        return jsonify({"status": "error", "detail": "latitude e longitude são obrigatórios"}), 400

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except (ValueError, TypeError):
        return jsonify({"status": "error", "detail": "latitude e longitude devem ser números"}), 400

    db_session = get_db()
    try:
        # Determinar username e user_id
        # Se usuario for string (ex: "tupa_joao"), usar como username
        # Se usuario for int, usar como user_id
        # Se não enviado, gerar username = f"tupa_{fonte}"
        if isinstance(usuario, str):
            report_username = usuario
            report_user_id = None
        elif isinstance(usuario, int):
            report_username = None
            report_user_id = usuario
        else:
            report_username = f"tupa_{fonte}"
            report_user_id = None

        # Salvar reporte no banco
        report = ReportORM(
            lat=latitude,
            lon=longitude,
            user_id=report_user_id,
            username=report_username,
            filename=imagem,
            nivel="alerta" if nivel == 1 else "suspeito" if nivel == 2 else "confirmado",
            count=nivel,
            fonte=fonte
        )
        db_session.add(report)
        db_session.commit()

        # Enviar notificação para TUPA
        try:
            import requests
            tupa_payload = {
                "tipo": "queimada",
                "latitude": latitude,
                "longitude": longitude,
                "fonte": fonte
            }
            requests.post(
                "http://localhost:5001/api/notificacoes",
                json=tupa_payload,
                timeout=5
            )
        except Exception as e:
            # TUPA não está online - não falhar a requisição
            print(f"[TUPA] Erro ao enviar notificação: {e}")

        return jsonify({"status": "ok"})
    except Exception as e:
        db_session.rollback()
        return jsonify({"status": "error", "detail": str(e)}), 500
    finally:
        db_session.close()
